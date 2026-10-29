# Progresso

Uma entrada por sessão, da mais recente para a mais antiga. Cada entrada diz o que foi feito, como foi verificado e o próximo passo, para a sessão seguinte começar sem reconstruir o contexto.

## 2026-10-27

- Feature: FAT-002, em andamento.
- Feito: cálculo da multa em `app/servicos/encargos.py` e testes do pagamento em dia.
- Verificação: `pytest tests/servicos/test_encargos.py` passou; o caso de pagamento após o vencimento ainda não tem teste.
- Próximo passo: escrever o teste de pagamento atrasado e ajustar a rota `POST /faturas/{id}/pagamento`.

## 2026-10-21

- Feature: FAT-001, concluída.
- Feito: emissão de fatura com itens e cálculo do total.
- Verificação: passos de `verificacao` executados e anotados em `evidencia`; revisão sem achados graves.
- Próximo passo: iniciar FAT-002.
