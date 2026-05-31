# =============================================================================
# Servicio — Integración con Andreani
# Cotización y generación de envíos
# =============================================================================
from app.config import settings

def get_shipping_quotes(zip_code: str, weight_gr: int, volume_cm3: int = 0) -> list[dict]:
    """
    Simula una cotización a la API de Andreani.
    Cuando se configuren ANDREANI_USERNAME y ANDREANI_PASSWORD en el .env,
    esta función debe ser reemplazada por una llamada HTTP a la API REST real.
    """
    
    # Check if credentials exist
    # if settings.ANDREANI_USERNAME and settings.ANDREANI_PASSWORD:
    #     Llamada real a la API de Andreani con requests o httpx
    #     pass

    print(f"📦 Cotizando envío a CP: {zip_code} (Peso: {weight_gr}g)")

    # Cotización Mock / Simulada basada en el código postal (CP)
    # Ejemplo básico: si es CABA/GBA (CP empieza con 1) es más barato
    is_caba_gba = zip_code.startswith("1")
    
    base_price = 3500 if is_caba_gba else 5500
    
    # Pequeño recargo por peso
    weight_surcharge = (weight_gr / 1000) * 500
    
    price_standard = base_price + weight_surcharge
    price_urgent = price_standard * 1.4

    return [
        {
            "id": "andreani_estandar",
            "carrier": "Andreani",
            "method": "Estándar a Domicilio",
            "price": round(price_standard, 2),
            "estimated_days": "3 a 5 días hábiles",
        },
        {
            "id": "andreani_urgente",
            "carrier": "Andreani",
            "method": "Urgente a Domicilio",
            "price": round(price_urgent, 2),
            "estimated_days": "1 a 2 días hábiles",
        },
        {
            "id": "andreani_sucursal",
            "carrier": "Andreani",
            "method": "Retiro en Sucursal",
            "price": round(price_standard * 0.8, 2),
            "estimated_days": "2 a 4 días hábiles",
        }
    ]
