#!/usr/bin/env bash
# Ritual de início de sessão: instala dependências e prova que o ponto de partida está saudável.
# set -euo pipefail faz qualquer falha interromper o script, em vez de passar despercebida.
set -euo pipefail

cd "$(dirname "$0")"
echo "==> Diretório: $PWD"

echo "==> Dependências"
pip install --quiet -r requirements-dev.txt

echo "==> Verificação de base"
ruff check .
pytest --quiet

echo "==> Ambiente pronto"
