import os
import uuid

import tempfile

# Pasta central para arquivos temporários usando diretório do SO (necessário para Vercel Serverless)
TEMP_FOLDER = tempfile.gettempdir()

def generate_temp_filename(extension="ogg"):
    """
    Gera um nome de arquivo único para evitar colisões.
    """
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}.{extension}"
    return os.path.join(TEMP_FOLDER, filename)

def safe_remove_file(filepath):
    """
    Remove o arquivo se ele existir.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Erro ao remover arquivo {filepath}: {e}")
