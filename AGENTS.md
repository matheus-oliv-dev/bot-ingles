# AGENTS.md

## Visão Geral do Projeto
API REST em Python com Flask para o bot do WhatsApp ("Teacher Sarah") e frontend Web.
Integra com OpenAI/Gemini e Twilio.

## Antes de escrever código
1. Confirme o diretório base (`c:\Users\mathe\bot-ingles`).
2. Leia `progress.md` e `feature_list.json` (estado atual e feature ativa).
3. Revise commits recentes (se houver git disponível): `git log --oneline -5`.
4. Execute `.\init.bat` (lint + testes) para o Windows.

Se o baseline já estiver quebrado, corrija os erros de Lint ou Testes antes de implementar novas features.

## Restrições obrigatórias
- Siga os padrões do Flake8 para manter a sanidade e consistência do código (limite de 150 caracteres onde possível, espaçamento correto).
- Não commite credenciais no código; use `os.getenv()`.
- Respostas do Gemini na Web DEVEM ser retornadas em formato JSON válido, escapando chaves `{{` `}}` em f-strings onde apropriado.

## Documentos Temáticos
- Arquitetura (`docs/architecture.md`) — Entendimento dos serviços Flask, Twilio e LLMs.
- Padrões de Teste (`docs/testing.md`) — Referência ao escrever e rodar testes no `pytest`.

## Definição de concluído (Definition of Done)
Uma feature só está concluída quando:
- O comportamento alvo foi implementado.
- `.\init.bat` passa (lint + testes sem erros).
- `feature_list.json` é atualizado com o status ("passing") e evidência do sucesso.
- `progress.md` é atualizado com os passos concluídos e os próximos.

## Fim de sessão
1. Atualizar `feature_list.json` (status + evidência).
2. Atualizar `progress.md` (o que foi feito, bloqueios, próximo passo).
3. Commit descritivo quando o repositório estiver em estado seguro.
4. Garantir que a próxima sessão deve conseguir rodar `.\init.bat` com sucesso imediatamente.
