# =============================================================================
# Servicio — Mercado Pago
# Integración con Checkout Pro para procesar pagos
# =============================================================================
import mercadopago
from app.config import settings


def get_mp_sdk() -> mercadopago.SDK:
    """Retorna una instancia del SDK de Mercado Pago."""
    return mercadopago.SDK(settings.MP_ACCESS_TOKEN)


def create_preference(
    order_id: str,
    order_number: int,
    items: list[dict],
    payer: dict,
    shipping_cost: float = 0,
) -> dict:
    """
    Crea una preferencia de pago en Mercado Pago (Checkout Pro).

    Flujo:
        1. Backend crea preferencia con items, payer y URLs de retorno
        2. MP devuelve init_point (URL de checkout)
        3. Frontend redirige al cliente a esa URL
        4. Cliente paga con tarjeta, débito, transferencia, efectivo, etc.
        5. MP notifica al webhook cuando el pago se confirma

    Args:
        order_id: UUID de la orden en nuestra DB
        order_number: Número legible de la orden (#0001, #0002...)
        items: Lista de items con title, quantity, unit_price
        payer: Datos del comprador (name, email, phone)
        shipping_cost: Costo del envío (se suma como item adicional)

    Returns:
        dict con init_point, sandbox_init_point, preference_id
    """
    sdk = get_mp_sdk()

    # Armar items para MP
    mp_items = []
    for item in items:
        mp_items.append({
            "title": item["title"],
            "quantity": item["quantity"],
            "unit_price": float(item["unit_price"]),
            "currency_id": "ARS",
            "description": item.get("description", ""),
        })

    # Agregar envío como item si tiene costo
    if shipping_cost > 0:
        mp_items.append({
            "title": "Envío",
            "quantity": 1,
            "unit_price": float(shipping_cost),
            "currency_id": "ARS",
        })

    # Datos del pagador
    mp_payer = {
        "name": payer.get("first_name", ""),
        "surname": payer.get("last_name", ""),
        "email": payer.get("email", ""),
    }
    if payer.get("phone"):
        mp_payer["phone"] = {
            "area_code": "",
            "number": payer["phone"],
        }

    # URLs de retorno — MP no acepta localhost
    frontend = settings.FRONTEND_URL
    is_local = "localhost" in frontend or "127.0.0.1" in frontend

    # Construir la preferencia
    preference_data = {
        "items": mp_items,
        "payer": mp_payer,
        "external_reference": order_id,
        "statement_descriptor": "FOTOS JACKY",
        "metadata": {
            "order_id": order_id,
            "order_number": order_number,
        },
    }

    # Solo agregar back_urls y auto_return si el frontend tiene URL pública
    if not is_local:
        preference_data["back_urls"] = {
            "success": f"{frontend}/orden-confirmada?order_id={order_id}",
            "failure": f"{frontend}/checkout?error=payment_failed",
            "pending": f"{frontend}/orden-pendiente?order_id={order_id}",
        }
        preference_data["auto_return"] = "approved"

    # Solo agregar notification_url si el backend tiene URL pública
    if settings.BACKEND_URL and "localhost" not in settings.BACKEND_URL:
        preference_data["notification_url"] = f"{settings.BACKEND_URL}/api/webhooks/mercadopago"

    # Crear la preferencia en MP
    result = sdk.preference().create(preference_data)

    if result["status"] != 201:
        error_detail = result.get("response", {})
        print(f"❌ MP Error {result['status']}: {error_detail}")
        raise Exception(f"MP status {result['status']}: {error_detail}")

    response = result["response"]

    return {
        "preference_id": response["id"],
        "init_point": response["init_point"],
        "sandbox_init_point": response.get("sandbox_init_point", ""),
    }


def get_payment_info(payment_id: str) -> dict:
    """
    Obtiene información de un pago desde Mercado Pago.
    Usado por el webhook para verificar el estado del pago.

    Returns:
        dict con status, status_detail, external_reference, transaction_amount, etc.
    """
    sdk = get_mp_sdk()
    result = sdk.payment().get(payment_id)

    if result["status"] != 200:
        raise Exception(f"Error al obtener pago {payment_id}: {result}")

    payment = result["response"]

    return {
        "id": str(payment["id"]),
        "status": payment["status"],  # approved, pending, rejected, etc.
        "status_detail": payment.get("status_detail", ""),
        "external_reference": payment.get("external_reference", ""),  # order_id
        "transaction_amount": payment.get("transaction_amount", 0),
        "currency_id": payment.get("currency_id", "ARS"),
        "payment_method_id": payment.get("payment_method_id", ""),
        "payment_type_id": payment.get("payment_type_id", ""),
        "payer_email": payment.get("payer", {}).get("email", ""),
    }


# --- Mapeo de estados MP → nuestros estados ---

MP_STATUS_MAP = {
    "approved": "paid",
    "authorized": "paid",
    "pending": "pending_payment",
    "in_process": "pending_payment",
    "in_mediation": "pending_payment",
    "rejected": "cancelled",
    "cancelled": "cancelled",
    "refunded": "refunded",
    "charged_back": "refunded",
}


def mp_status_to_order_status(mp_status: str) -> str:
    """Convierte un estado de MP al estado de nuestra orden."""
    return MP_STATUS_MAP.get(mp_status, "pending_payment")
