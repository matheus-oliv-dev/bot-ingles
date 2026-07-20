# Testing Documentation

## Setup & Running
Utilizamos o `pytest` para testes unitários e de integração.
Para rodar todos os testes na sua máquina local, basta executar:
```bash
pytest tests/
```
Ou simplesmente rodar `.\init.bat` que já lida com o Lint (flake8) junto com os testes.

## Padrões de Escrita de Testes
- Todos os arquivos de teste devem residir dentro do diretório `tests/` e iniciar com `test_`.
- As funções de teste devem descrever claramente o comportamento validado em seu docstring.
- Utilizamos a fixture `client` (disponível em `tests/test_app.py`) para testes de requisições HTTP da API.
- Mocking: Em testes futuros que envolvam APIs externas (como a do Twilio, ou Google Gemini), as requisições devem ser "mockadas" usando `unittest.mock.patch` para evitar bater em cotas de API reais e garantir que os testes rodem rapidamente de forma independente.
