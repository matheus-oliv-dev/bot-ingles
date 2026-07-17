import os
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import google.generativeai as genai

from src.services.gemini_service import passo_1_transcrever, passo_2_responder
from src.services.tts_service import gerar_audio_openai
from src.db.database import salvar_no_banco, ler_ultimas_conversas
from src.utils.metrics import TOTAL_PROCESSING_LATENCY, ERROR_COUNT
from src.utils.file_manager import generate_temp_filename, safe_remove_file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Teacher Sarah (Nova Arquitetura) is ready!")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

    # Inicia o timer para medir a latência total do Telegram
    timer = TOTAL_PROCESSING_LATENCY.labels(platform='telegram').time()
    
    caminho = generate_temp_filename(extension="ogg")
    caminho_resposta = generate_temp_filename(extension="mp3")
    
    try:
        # 1. Baixar Áudio
        file = await context.bot.get_file(update.message.voice.file_id)
        await file.download_to_drive(caminho)
        
        loop = asyncio.get_running_loop()
        
        # Faz upload para a infra do Google usando run_in_executor para não bloquear
        def upload():
            return genai.upload_file(caminho)
        arquivo_gemini = await loop.run_in_executor(None, upload)
        
        # 2. PASSO 1: TRANSCRIÇÃO PURA
        transcricao = await loop.run_in_executor(None, lambda: passo_1_transcrever(arquivo_gemini))
        print(f"🗣️ Texto detectado: {transcricao}")

        if not transcricao or transcricao == "(Audio error)":
            await update.message.reply_text("I couldn't hear you clearly.")
            timer.observe_duration() # encerra o timer
            return

        # 3. PASSO 2: CÉREBRO DA SARAH
        # Puxando o histórico
        ultimas = await loop.run_in_executor(None, lambda: ler_ultimas_conversas(3))
        historico = ""
        if ultimas:
            for u, b in reversed(ultimas):
                historico += f"Student: {u}\nSarah: {b}\n"
                
        resposta = await loop.run_in_executor(None, lambda: passo_2_responder(transcricao, historico))
        print(f"🤖 Sarah respondeu: {resposta}")
        
        # Salva no Banco
        await loop.run_in_executor(None, lambda: salvar_no_banco(transcricao, resposta))

        # 4. Gera Áudio e Envia
        await context.bot.send_chat_action(chat_id=chat_id, action="upload_voice")
        await gerar_audio_openai(resposta, caminho_resposta)
        
        with open(caminho_resposta, 'rb') as voice_file:
            await update.message.reply_voice(voice=voice_file)
        
        msg_legenda = (
            f"🗣️ <i>{transcricao}</i>\n\n"
            f"🤖 <b>Sarah:</b> <span class='tg-spoiler'>{resposta}</span>"
        )
        await update.message.reply_text(msg_legenda, parse_mode=ParseMode.HTML)

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
        ERROR_COUNT.labels(platform='telegram', error_type=type(e).__name__).inc()
        await update.message.reply_text("Technical error. Try again.")
    finally:
        # Encerra o timer total
        timer.observe_duration()
        # Limpa os arquivos temporários criados
        safe_remove_file(caminho)
        safe_remove_file(caminho_resposta)
