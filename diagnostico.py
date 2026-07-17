"""
Script de Diagnóstico Completo
Testa cada componente da pipeline isoladamente.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 DIAGNÓSTICO COMPLETO DO BOT-INGLES")
print("=" * 60)

# ============================================
# TESTE 1: Variáveis de Ambiente
# ============================================
print("\n--- TESTE 1: Variáveis de Ambiente ---")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"  GOOGLE_API_KEY: {'✅ Presente (' + GOOGLE_API_KEY[:10] + '...)' if GOOGLE_API_KEY else '❌ AUSENTE'}")
print(f"  OPENAI_API_KEY: {'✅ Presente (' + OPENAI_API_KEY[:10] + '...)' if OPENAI_API_KEY else '⚠️ Ausente (opcional para web)'}")

# ============================================
# TESTE 2: Importações dos módulos
# ============================================
print("\n--- TESTE 2: Importações ---")
try:
    import google.generativeai as genai
    print("  ✅ google.generativeai importado")
except ImportError as e:
    print(f"  ❌ google.generativeai FALHOU: {e}")
    sys.exit(1)

try:
    import edge_tts
    print("  ✅ edge_tts importado")
except ImportError as e:
    print(f"  ❌ edge_tts FALHOU: {e}")

try:
    from prometheus_client import Histogram
    print("  ✅ prometheus_client importado")
except ImportError as e:
    print(f"  ❌ prometheus_client FALHOU: {e}")

try:
    from flask_cors import CORS
    print("  ✅ flask_cors importado")
except ImportError as e:
    print(f"  ❌ flask_cors FALHOU: {e}")

# ============================================
# TESTE 3: Conexão com o Gemini
# ============================================
print("\n--- TESTE 3: Conexão com o Gemini (texto puro) ---")
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    t0 = time.time()
    response = model.generate_content("Say 'Hello, the connection works!' in exactly those words.")
    elapsed = time.time() - t0
    
    print(f"  ✅ Gemini respondeu em {elapsed:.2f}s: {response.text.strip()}")
except Exception as e:
    print(f"  ❌ Gemini FALHOU: {e}")

# ============================================
# TESTE 4: Upload de áudio para o Gemini
# ============================================
print("\n--- TESTE 4: Upload de arquivo para o Gemini ---")

# Criar um arquivo de áudio de teste mínimo usando Edge-TTS
test_audio_path = "temp/test_diagnostic.mp3"
os.makedirs("temp", exist_ok=True)

try:
    print("  ⏳ Gerando áudio de teste com Edge-TTS...")
    t0 = time.time()
    
    async def gerar_teste():
        communicate = edge_tts.Communicate("Hello, this is a test.", "en-US-ChristopherNeural")
        await communicate.save(test_audio_path)
    
    asyncio.run(gerar_teste())
    elapsed = time.time() - t0
    
    file_size = os.path.getsize(test_audio_path)
    print(f"  ✅ Áudio de teste gerado em {elapsed:.2f}s ({file_size} bytes)")
except Exception as e:
    print(f"  ❌ Edge-TTS FALHOU: {e}")
    # Sem áudio de teste, não dá pra continuar os testes 5 e 6
    print("\n⚠️ Sem áudio de teste, pulando testes de upload.")
    print("=" * 60)
    sys.exit(1)

try:
    print("  ⏳ Fazendo upload para o Gemini...")
    t0 = time.time()
    arquivo = genai.upload_file(test_audio_path)
    elapsed = time.time() - t0
    print(f"  ✅ Upload concluído em {elapsed:.2f}s (Nome: {arquivo.name})")
except Exception as e:
    print(f"  ❌ Upload FALHOU: {e}")

# ============================================
# TESTE 5: Gemini processar áudio
# ============================================
print("\n--- TESTE 5: Gemini processar áudio ---")
try:
    prompt = "Listen to this audio and respond naturally in English. Keep it to 1 sentence."
    
    t0 = time.time()
    response = model.generate_content([prompt, arquivo])
    elapsed = time.time() - t0
    
    print(f"  ✅ Gemini processou áudio em {elapsed:.2f}s: {response.text.strip()}")
except Exception as e:
    print(f"  ❌ Processamento de áudio FALHOU: {e}")

# ============================================
# TESTE 6: Upload com mime_type forçado (como a rota web faz)
# ============================================
print("\n--- TESTE 6: Upload com mime_type='audio/ogg' (simulando browser) ---")
try:
    t0 = time.time()
    arquivo2 = genai.upload_file(test_audio_path, mime_type="audio/ogg")
    elapsed = time.time() - t0
    print(f"  ✅ Upload com mime_type='audio/ogg' em {elapsed:.2f}s")
    
    response2 = model.generate_content([prompt, arquivo2])
    print(f"  ✅ Gemini processou com mime forçado: {response2.text.strip()}")
except Exception as e:
    print(f"  ❌ Upload com mime_type FALHOU: {e}")

# ============================================
# TESTE 7: Testar a rota Flask diretamente
# ============================================
print("\n--- TESTE 7: Teste da rota Flask /api/web-chat ---")
try:
    import requests as req
    
    with open(test_audio_path, 'rb') as f:
        t0 = time.time()
        r = req.post(
            'http://127.0.0.1:5000/api/web-chat',
            files={'audio': ('test.ogg', f, 'audio/ogg')}
        )
        elapsed = time.time() - t0
    
    print(f"  Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ Rota funcionou em {elapsed:.2f}s!")
        print(f"     Texto: {data.get('text', 'N/A')}")
        print(f"     Áudio URL: {data.get('audio_url', 'N/A')}")
    else:
        print(f"  ❌ Rota retornou erro: {r.text}")
except req.exceptions.ConnectionError:
    print("  ⚠️ Flask não está rodando (ConnectionRefused). Inicie o main.py primeiro.")
except Exception as e:
    print(f"  ❌ Teste da rota FALHOU: {e}")

# Cleanup
try:
    os.remove(test_audio_path)
except:
    pass

print("\n" + "=" * 60)
print("🏁 DIAGNÓSTICO FINALIZADO!")
print("=" * 60)
