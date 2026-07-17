from flask import Flask
from flask_cors import CORS
from src.api.routes import api_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    print("🚀 Teacher Sarah (WhatsApp/Flask - Nova Arquitetura) Rodando!")
    # O metrics do Flask vai rodar na mesma porta do app Flask em /metrics
    app.run(debug=True, port=5000)
