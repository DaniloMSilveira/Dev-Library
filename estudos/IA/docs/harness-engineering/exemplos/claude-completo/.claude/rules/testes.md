---
paths:
  - "tests/**/*.py"
---

# Testes

- Um arquivo de teste por módulo, no caminho equivalente ao de `app/`. Exemplo: `app/servicos/encargos.py` é testado em `tests/servicos/test_encargos.py`.
- Use as fixtures de `tests/conftest.py`. Nenhum teste conecta no banco real.
- O nome do teste descreve o comportamento: `test_fatura_paga_com_atraso_gera_multa`.
- Não apague nem enfraqueça um teste para fazê-lo passar. Se o teste estiver errado, explique o motivo antes de mudá-lo.
