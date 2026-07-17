import os
import asyncio
import edge_tts
from openai import AsyncOpenAI
from dotenv import load_dotenv
from src.utils.metrics import TTS_GENERATION_LATENCY

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Async client for OpenAI to not block the event loop
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

async def gerar_audio_openai(texto, arquivo_saida):
    """Gera áudio usando OpenAI TTS-1"""
    if not openai_client:
        print("Erro: OPENAI_API_KEY não configurada.")
        return
        
    with TTS_GENERATION_LATENCY.labels(provider='openai').time():
        try:
            response = await openai_client.audio.speech.create(
                model="tts-1", 
                voice="shimmer", 
                input=texto,
                speed=0.85
            )
            response.stream_to_file(arquivo_saida)
        except Exception as e:
            print(f"Erro OpenAI TTS: {e}")

async def gerar_audio_edge(texto, arquivo_saida):
    """Gera áudio usando Edge-TTS (Vozes Microsoft) - Gratuito"""
    with TTS_GENERATION_LATENCY.labels(provider='edge-tts').time():
        try:
            communicate = edge_tts.Communicate(texto, "en-US-AriaNeural")
            await communicate.save(arquivo_saida)
        except Exception as e:
            print(f"Erro Edge TTS: {e}")
