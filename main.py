import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.api.routes import api_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per day", "3 per minute"],
    storage_uri="memory://"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Você atingiu o limite de mensagens temporário."), 429

app.register_blueprint(api_bp)

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return "Not Found", 404

if __name__ == '__main__':
    print("🚀 Teacher Sarah (WhatsApp/Flask - Nova Arquitetura) Rodando!")
    # O metrics do Flask vai rodar na mesma porta do app Flask em /metrics
    app.run(debug=True, port=5000)
