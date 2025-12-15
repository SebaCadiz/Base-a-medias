import requests
from django.conf import settings
import datetime 
import random 
from django.http import JsonResponse # Importa si usas este archivo como views.py

API_URL = getattr(settings, "EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/")

# -------------------------------------------------------------------
# Funciones base de la API de Conversión
# -------------------------------------------------------------------

def _fetch_rates(base: str):
    """
    Función base para obtener tasas de la API.
    """
    base = (base or "USD").upper().strip()
    if not base.isalpha() or len(base) != 3:
        return {"result": "error", "error-type": "invalid_currency_code"}
    try:
        resp = requests.get(API_URL + base, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        # Devuelve un diccionario para ser consistente con el manejo de errores
        return {"result": "error", "error": f"Error conectando a API de divisas: {e}"}

def convert_currency(from_currency: str, to_currency: str, amount: float):
    """
    Realiza la conversión de divisas.
    """
    from_currency = (from_currency or "USD").upper()
    to_currency = (to_currency or "USD").upper()
    
    try:
        amount = float(amount)
    except Exception:
        return {"error": "El parámetro 'amount' no es un número válido"}

    data = _fetch_rates(from_currency)
    if data.get("result") != "success":
        return {"error": f"La moneda {from_currency} es inválida o la API no responde"}

    rates = data.get("rates", {})
    
    if to_currency not in rates:
        return {"error": f"La moneda {to_currency} no existe en la respuesta"}

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
    """
    Lista las monedas disponibles.
    """
    data = _fetch_rates(base)
    if data.get("result") != "success":
        return {"error": "No se pudo obtener la lista de monedas"}
    return {"monedas": list(data.get("rates", {}).keys())}

# -------------------------------------------------------------------
# Funciones para el Dashboard (Dinámicas)
# -------------------------------------------------------------------

def generate_dynamic_series(current_rate, days=7, fluctuation_range=0.005):
    """
    Genera 6 puntos históricos simulados en torno al valor actual (current_rate).
    El último punto (el 7mo) SIEMPRE es el valor real de 'current_rate'.
    """
    historical_values = []

    seed_value = datetime.date.today().day + datetime.date.today().month * 10   
    # Generar los 6 puntos históricos (D-6 hasta Ayer)
    for i in range(-6, 0): 
        random.seed(seed_value + i) 
        
        fluctuation = current_rate * fluctuation_range 
        change = random.uniform(-fluctuation, fluctuation)
        value = current_rate + change
        
        # Redondeo específico (Pesos chilenos/colombianos vs Sol peruano)
        if current_rate >= 10: 
            rounded_value = round(value, 2)
        else: 
            rounded_value = round(value, 4)
        
        historical_values.append(rounded_value)
            
    # [D-6, D-5, D-4, D-3, D-2, Ayer, Hoy]
    series = historical_values + [current_rate]
    
    return series


def get_mock_chart_data():
    """
    Genera etiquetas de fechas dinámicas y series de datos dinámicas (sin UF),
    ancladas a las tasas de HOY de la API.
    """
    # 1. GENERACIÓN DINÁMICA DE FECHAS (D-6 hasta Hoy)
    today = datetime.date.today()
    dates = []
    for i in range(-6, 1):
        date = today + datetime.timedelta(days=i)
        
        if i == -1:
            dates.append("Ayer")
        elif i == 0:
            dates.append("Hoy")
        else:
            # Formato D/M/AAAA (ej: 14/12/2025)
            dates.append(date.strftime("%#d/%#m/%Y")) 
            
    # 2. OBTENER TASAS REALES DE HOY
    api_data = _fetch_rates('USD')
    
    # Fallback/Valores por defecto si la API falla 
    CLP_FALLBACK = 902.00
    COP_FALLBACK = 3905.00
    PEN_FALLBACK = 3.80
    
    if api_data.get("result") == "success":
        rates = api_data.get("rates", {})
        clp_rate_hoy = rates.get("CLP", CLP_FALLBACK)
        cop_rate_hoy = rates.get("COP", COP_FALLBACK)
        pen_rate_hoy = rates.get("PEN", PEN_FALLBACK)
    else:
        # Usar Fallback si hay error
        clp_rate_hoy = CLP_FALLBACK
        cop_rate_hoy = COP_FALLBACK
        pen_rate_hoy = PEN_FALLBACK
        
    # 3. GENERACIÓN DE SERIES
    data = {
        "dates": dates,
        "series": {
            "CLP_vs_USD": generate_dynamic_series(clp_rate_hoy, fluctuation_range=0.008),
            "COP_vs_USD": generate_dynamic_series(cop_rate_hoy, fluctuation_range=0.01),
            "PEN_vs_USD": generate_dynamic_series(pen_rate_hoy, fluctuation_range=0.003),
        }
    }
    return {"result": "success", "data": data}