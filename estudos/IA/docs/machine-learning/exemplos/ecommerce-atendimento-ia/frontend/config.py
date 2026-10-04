# Projeto Desenvolvido na Data Science Academy
"""Configuração centralizada do frontend."""

import os
import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Constantes de negócio
FREE_SHIPPING_THRESHOLD = 299.0
STANDARD_SHIPPING_COST = 29.90
MAX_PRODUCT_PRICE = 15000
HTTP_TIMEOUT = 10.0
CHAT_TIMEOUT = 30.0

# follow_redirects: FastAPI redireciona URLs com barra final (307)
http = httpx.Client(base_url=API_URL, timeout=HTTP_TIMEOUT, follow_redirects=True)
