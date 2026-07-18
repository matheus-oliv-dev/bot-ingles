import os
import requests
import asyncio
from flask import Blueprint, request, send_from_directory, Response
from twilio.twiml.messaging_response import MessagingResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.services.gemini_service import model, load_audio_inline, LLM_RESPONSE_LATENCY
from src.services.tts_service import gerar_audio_edge
from src.utils.metrics import TOTAL_PROCESSING_LATENCY, ERROR_COUNT
from src.utils.file_manager import TEMP_FOLDER, generate_temp_filename

import json
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache_respostas.json')

def get_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")

api_bp = Blueprint('api', __name__)

@api_bp.route('/metrics')
def metrics():
    """Expõe as métricas do Prometheus"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@api_bp.route('/bot', methods=['POST'])
def bot():
    """Recebe a mensagem do WhatsApp (Twilio)"""
    import time
    
    msg_recebida = request.values.get('Body', '').lower()
    if len(msg_recebida) > 300:
        msg_recebida = msg_recebida[:300]
    media_url = request.values.get('MediaUrl0')
    remetente = request.values.get('From')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    total_start = time.time()

    # 1. Se o usuário mandou áudio
    if media_url:
        print(f"Áudio recebido de {remetente}")
        
        caminho_input = generate_temp_filename("ogg")
        caminho_output = generate_temp_filename("mp3")
        
        try:
            with open(caminho_input, 'wb') as f:
                f.write(requests.get(media_url, timeout=10).content)
                
            print("Enviando áudio para o Gemini...")
            arquivo_gemini = load_audio_inline(caminho_input)
            
            prompt = """
            You are a friendly English Tutor. The user is practicing English via WhatsApp audio.
            1. Listen to the user's audio.
            2. Respond naturally to the conversation in English.
            3. Keep your response concise (maximum 2 sentences).
            4. If the user makes a significant grammar mistake, gently correct it after your response.
            """
            
            t0 = time.time()
            response = model.generate_content([prompt, arquivo_gemini])
            resposta_texto = response.text.strip()
            LLM_RESPONSE_LATENCY.observe(time.time() - t0)
                
            print(f"Gemini respondeu: {resposta_texto}")
            
            asyncio.run(gerar_audio_edge(resposta_texto, caminho_output))
            
            filename = os.path.basename(caminho_output)
            url_audio_resposta = f"{request.host_url}temp/{filename}"
            
            msg.body(f"🤖 {resposta_texto}")
                
        except Exception as e:
            print(f"❌ Erro Crítico WhatsApp: {e}")
            ERROR_COUNT.labels(platform='whatsapp', error_type=type(e).__name__).inc()
            msg.body("Sorry, I had a technical problem! Try again.")
        finally:
            TOTAL_PROCESSING_LATENCY.labels(platform='whatsapp').observe(time.time() - total_start)
            from src.utils.file_manager import safe_remove_file
            safe_remove_file(caminho_input)
            
    # 2. Se for só texto
    else:
        msg.body("Mande um áudio para treinarmos sua pronúncia! 🎤")

    return str(resp)

@api_bp.route('/api/web-chat', methods=['POST'])
def web_chat():
    """Recebe o áudio gravado no navegador via FormData e retorna texto e áudio."""
    from flask import jsonify
    import time
    import traceback
    import base64

    print("\n" + "="*50)
    print("📥 Nova requisição Web recebida!")
    print("="*50)

    texto_usuario = request.form.get('text')
    
    if texto_usuario and len(texto_usuario) > 300:
        print("❌ Mensagem muito longa.")
        return jsonify({"error": "Sua mensagem excedeu o limite de 300 caracteres."}), 400

    audio_file = request.files.get('audio')
    history_text = request.form.get('history', '')

    if not texto_usuario and not audio_file:
        print("❌ Nenhum arquivo de áudio ou texto enviado")
        return jsonify({"error": "Nenhum dado enviado"}), 400

    total_start = time.time()
    caminho_input = generate_temp_filename("ogg") if audio_file else None
    caminho_output = generate_temp_filename("mp3")
    
    try:
        conteudo_gemini = []
        
        if texto_usuario:
            print(f"✅ Texto recebido: {texto_usuario}")
            
            cache_key = texto_usuario.strip().lower()
            cache_db = get_cache()
            if cache_key in cache_db:
                print("✅ Retornando resposta do CACHE!")
                TOTAL_PROCESSING_LATENCY.labels(platform='web').observe(time.time() - total_start)
                return jsonify(cache_db[cache_key])
            
            history_context = f"\nPrevious Conversation Context:\n{history_text}\n" if history_text else ""
            
            prompt = f"""
            You are a friendly English Tutor. The user is practicing English via Web text.{history_context}
            The user typed this message: "{texto_usuario}"
            
            1. Use exactly what the user typed as the "transcription" field.
            2. Respond naturally to the conversation in English (maximum 2 sentences).
            3. Identify any significant grammar mistakes in the user's text.
            4. Provide 1-2 brief study suggestions.
            5. Extract ONE interesting English vocabulary noun from the conversation. Provide it as "vocab_word". Provide a simple english definition as "vocab_meaning". Provide a short example sentence as "vocab_example".
            
            You MUST return your response in RAW JSON format with EXACTLY these keys:
            {{
                "transcription": "what the user typed",
                "response": "your verbal response",
                "errors": ["error 1 with correction", "error 2"],
                "suggestions": ["suggestion 1", "suggestion 2"],
                "vocab_word": "apple",
                "vocab_meaning": "a round fruit with red or green skin",
                "vocab_example": "I ate a sweet apple today."
            }}
            Return ONLY valid JSON.
            """
            conteudo_gemini = [prompt]
        else:
            print(f"✅ Arquivo recebido: {audio_file.filename}, tipo: {audio_file.content_type}")
            # 1. Salvar arquivo
            audio_file.save(caminho_input)
            file_size = os.path.getsize(caminho_input)
            print(f"✅ Áudio salvo em: {caminho_input} ({file_size} bytes)")
            
            if file_size == 0:
                print("❌ Arquivo de áudio está vazio!")
                return jsonify({"error": "Áudio vazio"}), 400
            
            # 2. Upload para o Gemini
            print("⏳ Enviando áudio para o Gemini...")
            t0 = time.time()
            arquivo_gemini = load_audio_inline(caminho_input, mime_type="audio/webm")
            print(f"✅ Upload concluído em {time.time() - t0:.2f}s")
            
            history_context = f"\nPrevious Conversation Context:\n{history_text}\n" if history_text else ""
            
            prompt = f"""
            You are a friendly English Tutor. The user is practicing English via Web audio.{history_context}
            1. Listen to the user's audio.
            2. Provide exactly what the user said (transcription).
            3. Respond naturally to the conversation in English (maximum 2 sentences).
            4. Identify any significant grammar mistakes.
            5. Provide 1-2 brief study suggestions.
            6. Extract ONE interesting English vocabulary noun from the conversation. Provide it as "vocab_word". Provide a simple english definition as "vocab_meaning". Provide a short example sentence as "vocab_example".
            
            You MUST return your response in RAW JSON format with EXACTLY these keys:
            {
                "transcription": "what the user said",
                "response": "your verbal response",
                "errors": ["error 1 with correction", "error 2"],
                "suggestions": ["suggestion 1", "suggestion 2"],
                "vocab_word": "apple",
                "vocab_meaning": "a round fruit with red or green skin",
                "vocab_example": "I ate a sweet apple today."
            }
            Return ONLY valid JSON.
            """
            conteudo_gemini = [prompt, arquivo_gemini]
        
        print("⏳ Gerando resposta do Gemini...")
        t0 = time.time()
        
        # Força o Gemini a retornar JSON
        generation_config = {"response_mime_type": "application/json"}
        response = model.generate_content(conteudo_gemini, generation_config=generation_config)
        
        import json
        try:
            dados = json.loads(response.text.strip())
            resposta_texto = dados.get("response", "Sorry, I couldn't generate a response.")
            transcricao = dados.get("transcription", "")
            erros = dados.get("errors", [])
            sugestoes = dados.get("suggestions", [])
            vocab_word = dados.get("vocab_word", "")
            vocab_meaning = dados.get("vocab_meaning", "")
            vocab_example = dados.get("vocab_example", "")
        except Exception as e:
            print(f"Erro ao fazer parse do JSON: {e}")
            print(f"Texto original: {response.text}")
            resposta_texto = "Sorry, I had trouble analyzing that."
            transcricao = ""
            erros = []
            sugestoes = []
            vocab_word = ""
            vocab_meaning = ""
            vocab_example = ""

        # Integração Wikipedia apenas para buscar Imagem
        wiki_image = ""
        if vocab_word:
            try:
                headers = {'User-Agent': 'TeacherSarahBot/1.0 (teacher@sarah.bot)'}
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{vocab_word}"
                wiki_resp = requests.get(wiki_url, headers=headers, timeout=3)
                if wiki_resp.status_code == 200:
                    wiki_data = wiki_resp.json()
                    wiki_image = wiki_data.get('thumbnail', {}).get('source', '')
            except Exception as e:
                print(f"Erro na Wikipedia API (Imagem): {e}")

        llm_elapsed = time.time() - t0
        LLM_RESPONSE_LATENCY.observe(llm_elapsed)
        print(f"✅ Gemini respondeu em {llm_elapsed:.2f}s: {resposta_texto}")
        
        # 4. Gerar áudio com Edge-TTS apenas para a resposta falada
        print("⏳ Gerando áudio com Edge-TTS...")
        t0 = time.time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(gerar_audio_edge(resposta_texto, caminho_output))
        finally:
            loop.close()
        print(f"✅ Áudio gerado em {time.time() - t0:.2f}s")
        
        # 5. Ler áudio gerado e converter para Base64
        audio_base64 = ""
        if os.path.exists(caminho_output):
            with open(caminho_output, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        total_elapsed = time.time() - total_start
        TOTAL_PROCESSING_LATENCY.labels(platform='web').observe(total_elapsed)
        print(f"✅ Resposta pronta em {total_elapsed:.2f}s (Áudio via Base64)!")
        print("="*50 + "\n")
        
        payload = {
            "text": resposta_texto,
            "transcription": transcricao,
            "errors": erros,
            "suggestions": sugestoes,
            "audio_base64": audio_base64,
            "vocab_word": vocab_word,
            "vocab_meaning": vocab_meaning,
            "vocab_example": vocab_example,
            "wiki_image": wiki_image
        }

        if texto_usuario:
            cache_db = get_cache()
            cache_db[cache_key] = payload
            save_cache(cache_db)
            
        return jsonify(payload)
        
    except Exception as e:
        print(f"❌ Erro Crítico Web: {e}")
        print(traceback.format_exc())
        ERROR_COUNT.labels(platform='web', error_type=type(e).__name__).inc()
        return jsonify({"error": str(e)}), 500
    finally:
        from src.utils.file_manager import safe_remove_file
        if caminho_input:
            safe_remove_file(caminho_input)
        if caminho_output:
            safe_remove_file(caminho_output)


@api_bp.route('/temp/<path:filename>')
def serve_temp(filename):
    """
    Rota para o Twilio conseguir baixar o MP3 gerado.
    Em um cenário ideal, o arquivo seria deletado logo após o Twilio fazer o download.
    """
    return send_from_directory(os.path.abspath(TEMP_FOLDER), filename)

# --- ROTAS DO FRONTEND ---
@api_bp.route('/')
def index():
    return send_from_directory(os.path.abspath('frontend'), 'index.html')

@api_bp.route('/style.css')
def style():
    return send_from_directory(os.path.abspath('frontend'), 'style.css')

@api_bp.route('/app.js')
def script():
    return send_from_directory(os.path.abspath('frontend'), 'app.js')

