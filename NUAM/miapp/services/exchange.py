import requests
from django.conf import settings

API_URL = getattr(settings, "EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/")


def _fetch_rates(base: str):
    base = (base or "USD").upper()
    resp = requests.get(API_URL + base, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data


def convert_currency(from_currency: str, to_currency: str, amount: float):
    from_currency = (from_currency or "USD").upper()
    to_currency = (to_currency or "USD").upper()
    try:
        amount = float(amount)
    except Exception:
        return {"error": "El parámetro 'amount' no es un número válido"}

    data = _fetch_rates(from_currency)
    if data.get("result") != "success":
        return {"error": f"La moneda {from_currency} no existe o la API no responde"}

    rates = data.get("rates", {})
    if to_currency not in rates:
        return {"error": f"La moneda {to_currency} no existe"}

    rate = rates[to_currency]
    result = round(amount * rate, 2)

    return {
        "from": from_currency,
        "to": to_currency,
        "rate": rate,
        "amount": amount,
        "resultado": result,
    }


def list_currencies(base: str = "USD"):
    data = _fetch_rates(base)
    if data.get("result") != "success":
        return {"error": "No se pudo obtener la lista de monedas"}
    return {"monedas": list(data.get("rates", {}).keys())}
