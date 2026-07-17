import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from prometheus_client import start_http_server

# Força o terminal do Windows a aceitar emojis e caracteres UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from src.bot.handlers import start, handle_voice_message

load_dotenv()
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN_TELEGRAM or not GOOGLE_API_KEY:
    print("❌ ERRO CRÍTICO: Chaves de API não encontradas no .env!")
    exit(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

if __name__ == '__main__':
    # Inicia o servidor de métricas do Prometheus na porta 8001
    print("📊 Iniciando servidor de métricas do Prometheus na porta 8001...")
    try:
        start_http_server(8001)
    except Exception as e:
        print(f"Erro ao subir Prometheus: {e}")
        
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    print("🚀 Teacher Sarah (Telegram - Nova Arquitetura) Rodando!")
    app.run_polling()
