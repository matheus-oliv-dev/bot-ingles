from prometheus_client import Histogram, Counter

# Histograms
TRANSCRIPTION_LATENCY = Histogram(
    'transcription_time_seconds',
    'Latência do passo 1 (Transcrição pelo Gemini)'
)

LLM_RESPONSE_LATENCY = Histogram(
    'llm_response_time_seconds',
    'Latência do passo 2 (Resposta do Gemini)'
)

TTS_GENERATION_LATENCY = Histogram(
    'tts_generation_time_seconds',
    'Latência do passo 3 (Geração de Áudio)',
    ['provider'] # Ex: 'openai' ou 'edge-tts'
)

TOTAL_PROCESSING_LATENCY = Histogram(
    'total_processing_time_seconds',
    'Latência total desde o recebimento até a resposta',
    ['platform'] # Ex: 'telegram' ou 'whatsapp'
)

# Counters
ERROR_COUNT = Counter(
    'bot_error_count',
    'Número de erros encontrados',
    ['platform', 'error_type']
)
