import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.utils.metrics import TRANSCRIPTION_LATENCY, LLM_RESPONSE_LATENCY

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def load_audio_inline(caminho_arquivo, mime_type="audio/ogg"):
    """
    Carrega o áudio como bytes para enviar inline no generate_content.
    Isso evita usar a Files API (genai.upload_file) que requer um tipo
    diferente de autenticação.
    """
    with open(caminho_arquivo, "rb") as f:
        audio_bytes = f.read()
    return {"mime_type": mime_type, "data": audio_bytes}

@TRANSCRIPTION_LATENCY.time()
def passo_1_transcrever(arquivo_gemini):
    """
    Passo 1: Apenas ouve e escreve. Sem contexto, sem personalidade.
    """
    prompt = """
    You are a professional Transcriber tool.
    Task: Transcribe the audio file exactly word for word.
    Rules: 
    - Do NOT reply to the content.
    - Do NOT add labels like "Speaker:" or "Transcription:".
    - Just output the raw text.
    """
    try:
        response = model.generate_content([prompt, arquivo_gemini])
        return response.text.strip()
    except Exception as e:
        print(f"Erro Transcrição: {e}")
        return "(Audio error)"

@LLM_RESPONSE_LATENCY.time()
def passo_2_responder(texto_usuario, historico=""):
    """
    Passo 2: Pega o texto limpo e gera a resposta da Sarah.
    """
    prompt = f"""
    HISTORY CONTEXT:
    {historico}
    
    CURRENT INPUT:
    Student: "{texto_usuario}"
    
    YOUR ROLE:
    You are 'Sarah', a friendly English Teacher (A2/B1 level).
    
    TASK:
    Respond to the Student's input naturally.
    - Keep it concise (max 2 sentences).
    - If the student made a grammar mistake, correct it gently at the end.
    - Do NOT format as JSON. Just give me the plain text response.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro Resposta: {e}")
        return "I'm having trouble thinking right now."
