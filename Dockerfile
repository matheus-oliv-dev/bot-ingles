# Usa a imagem oficial do Python (a versão 3.12 slim é mais leve e rápida para o Azure)
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /bot-ingles

# Copia o arquivo de dependências primeiro
COPY requirements.txt .

# Instala as dependências necessárias sem guardar cache (deixa a imagem mais leve)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do seu projeto para dentro do container
COPY . .

# Comando que será executado quando o container iniciar
CMD ["python", "bot_telegram.py"]