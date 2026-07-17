import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.api.routes import api_bp

app = Flask(__name__, static_folder="frontend")
CORS(app)
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    return "Not Found", 404

if __name__ == '__main__':
    print("🚀 Teacher Sarah (WhatsApp/Flask - Nova Arquitetura) Rodando!")
    # O metrics do Flask vai rodar na mesma porta do app Flask em /metrics
    app.run(debug=True, port=5000)
