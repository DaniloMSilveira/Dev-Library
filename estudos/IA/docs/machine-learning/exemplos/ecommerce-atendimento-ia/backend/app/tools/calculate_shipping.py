# Projeto Desenvolvido na Data Science Academy

"""Tool calculate_shipping — Calcula frete estimado por estado brasileiro."""

from langchain_core.tools import tool

FREE_SHIPPING_THRESHOLD = 299.0

SHIPPING_TABLE = {
    "SP": {"price": 15.90, "days": "3-5"},
    "RJ": {"price": 18.90, "days": "3-5"},
    "MG": {"price": 19.90, "days": "4-5"},
    "ES": {"price": 19.90, "days": "4-5"},
    "PR": {"price": 22.90, "days": "4-6"},
    "SC": {"price": 24.90, "days": "4-6"},
    "RS": {"price": 26.90, "days": "5-6"},
    "DF": {"price": 24.90, "days": "4-6"},
    "GO": {"price": 26.90, "days": "5-7"},
    "MT": {"price": 29.90, "days": "5-7"},
    "MS": {"price": 27.90, "days": "5-7"},
    "BA": {"price": 29.90, "days": "5-8"},
    "PE": {"price": 32.90, "days": "6-8"},
    "CE": {"price": 34.90, "days": "6-8"},
    "MA": {"price": 36.90, "days": "7-8"},
    "PB": {"price": 33.90, "days": "6-8"},
    "RN": {"price": 34.90, "days": "6-8"},
    "AL": {"price": 33.90, "days": "6-8"},
    "SE": {"price": 32.90, "days": "6-8"},
    "PI": {"price": 36.90, "days": "7-8"},
    "AM": {"price": 44.90, "days": "8-12"},
    "PA": {"price": 39.90, "days": "7-10"},
    "AC": {"price": 49.90, "days": "10-12"},
    "RO": {"price": 42.90, "days": "8-10"},
    "RR": {"price": 49.90, "days": "10-12"},
    "AP": {"price": 47.90, "days": "9-12"},
    "TO": {"price": 34.90, "days": "6-8"},
}


@tool
async def dsa_calculate_shipping(state: str, total: float) -> str:
    """Calcula o frete estimado para um estado brasileiro. Frete grátis para compras acima de R$299."""
    state_upper = state.upper().strip()

    # Regra de negócio: frete grátis acima de R$299 — no código (não no LLM) para consistência
    if total >= FREE_SHIPPING_THRESHOLD:
        shipping_info = SHIPPING_TABLE.get(state_upper)
        days = shipping_info["days"] if shipping_info else "5-10"
        return f"Frete GRÁTIS para {state_upper}! Prazo estimado: {days} dias úteis."

    shipping_info = SHIPPING_TABLE.get(state_upper)
    
    if not shipping_info:
        return (
            f"Estado '{state}' não reconhecido. "
            "Use a sigla do estado (ex: SP, RJ, MG). "
            "Frete grátis para compras acima de R$299,00."
        )

    return (
        f"Frete para {state_upper}: R${shipping_info['price']:,.2f}\n"
        f"Prazo estimado: {shipping_info['days']} dias úteis\n"
        f"Dica: frete grátis para compras acima de R$299,00!"
    )


