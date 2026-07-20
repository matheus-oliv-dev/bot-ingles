import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_metrics_route(client):
    """Testa se a rota /metrics retorna HTTP 200"""
    response = client.get('/metrics')
    assert response.status_code == 200

def test_index_route(client):
    """Testa se a rota principal (frontend) retorna HTTP 200"""
    response = client.get('/')
    assert response.status_code == 200
