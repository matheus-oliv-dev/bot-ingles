import os
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv("DB_PASSWORD", ""), 
    'database': 'bot_ingles',
    'pool_name': 'mypool',
    'pool_size': 5
}

# Criando o pool de conexões (Thread-safe)
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
except Exception as e:
    print(f"Erro ao inicializar pool do MySQL: {e}")
    connection_pool = None

def get_connection():
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except Exception as e:
            print(f"Erro ao obter conexão do pool: {e}")
    return None

def salvar_no_banco(user_text, bot_text):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO conversas (data, user_text, bot_text) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datetime.now(), user_text, bot_text))
            conn.commit()
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
        finally:
            conn.close() # Retorna ao pool

def ler_ultimas_conversas(limite=3):
    dados = []
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_text, bot_text FROM conversas ORDER BY id DESC LIMIT %s", (limite,))
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao ler banco: {e}")
        finally:
            conn.close() # Retorna ao pool
    return dados
