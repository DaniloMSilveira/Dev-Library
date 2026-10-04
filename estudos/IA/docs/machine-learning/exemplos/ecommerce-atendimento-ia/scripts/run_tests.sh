#!/bin/bash
# Projeto Desenvolvido na Data Science Academy
set -e
echo "Executando testes..."

echo ""
echo "=== API Tests ==="
cd api && python -m pytest tests/ -v --tb=short && cd ..

echo ""
echo "=== Backend Tests ==="
cd backend && python -m pytest tests/ -v --tb=short && cd ..

echo ""
echo "Todos os testes passaram!"
