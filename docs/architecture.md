# Architecture Documentation

## Overview
Teacher Sarah (bot-ingles) é uma aplicação Flask que serve duas plataformas principais:
1. Um Web-Chat interativo (frontend HTML/JS em `frontend/` e endpoint `/api/web-chat` em `src/api/routes.py`).
2. Uma integração com o WhatsApp através do Twilio (endpoint `/bot` em `src/api/routes.py`).

## Core Components
- **API (routes.py):** Rotas principais e orquestração (recebe mensagens, envia para a IA e retorna).
- **Gemini Service (`src/services/gemini_service.py`):** Encapsula chamadas ao Google Gemini. Transcreve áudios enviados pelo usuário, analisa gramática, gera respostas da professora e extrai vocabulário via prompts JSON precisos.
- **TTS Service (`src/services/tts_service.py`):** Converte a resposta em texto da IA de volta para áudio (Edge-TTS).
- **File Manager (`src/utils/file_manager.py`):** Lida com criação de arquivos temporários (`temp/`) necessários durante o processamento de áudio.
- **Metrics (`src/utils/metrics.py`):** Expõe dados via Prometheus Client (como latência de processamento e LLM) na rota `/metrics`.

## Rate Limiting
Utiliza `Flask-Limiter` em `main.py` baseado no IP para prevenir spam. O limite foi ajustado para permitir conversas longas e naturais sem estourar as cotas grátis das APIs consumidas (Gemini).
