# =============================================================================
# Router — Webhooks
# Recibe notificaciones de Mercado Pago cuando un pago cambia de estado
# =============================================================================
from fastapi import APIRouter, Request, HTTPException
from app.database import get_supabase_admin
from app.services.mercadopago import get_payment_info, mp_status_to_order_status
from app.services.email import send_order_confirmation, send_new_order_notification
from app.models.order import ORDER_STATUS_LABELS

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Webhook de Mercado Pago.

    MP nos envía notificaciones cuando:
    - Un pago se aprueba
    - Un pago queda pendiente
    - Un pago se rechaza
    - Un pago se reembolsa

    Flujo:
        1. MP envía POST con type="payment" y data.id=payment_id
        2. Consultamos los datos del pago a la API de MP
        3. Buscamos la orden por external_reference (order_id)
        4. Actualizamos el estado de la orden
        5. Si el pago fue aprobado → enviamos email de confirmación
    """
    body = await request.json()
    print(f"🔔 Webhook MP recibido: {body}")

    # MP envía distintos tipos de notificación
    # Solo nos interesan las de tipo "payment"
    notification_type = body.get("type") or body.get("topic")

    if notification_type != "payment":
        return {"status": "ignored", "reason": f"type={notification_type}"}

    # Obtener payment_id
    payment_id = None
    if "data" in body and "id" in body["data"]:
        payment_id = str(body["data"]["id"])
    elif "resource" in body:
        # Formato alternativo de MP
        payment_id = body["resource"].split("/")[-1]

    if not payment_id:
        print("⚠️  Webhook sin payment_id, ignorando")
        return {"status": "ignored", "reason": "no payment_id"}

    # =========================================================================
    # 1. OBTENER DATOS DEL PAGO DESDE MP
    # =========================================================================
    try:
        payment = get_payment_info(payment_id)
    except Exception as e:
        print(f"❌ Error al obtener pago de MP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    print(f"💳 Pago {payment_id}: status={payment['status']}, order={payment['external_reference']}")

    # =========================================================================
    # 2. BUSCAR LA ORDEN EN NUESTRA DB
    # =========================================================================
    db = get_supabase_admin()
    order_id = payment["external_reference"]

    if not order_id:
        print("⚠️  Pago sin external_reference, ignorando")
        return {"status": "ignored", "reason": "no external_reference"}

    order_result = (
        db.table("orders")
        .select("*, order_items(*)")
        .eq("id", order_id)
        .execute()
    )

    if not order_result.data:
        print(f"⚠️  Orden {order_id} no encontrada")
        return {"status": "error", "reason": "order not found"}

    order = order_result.data[0]

    # =========================================================================
    # 3. ACTUALIZAR ESTADO DE LA ORDEN
    # =========================================================================
    new_status = mp_status_to_order_status(payment["status"])
    old_status = order["status"]

    # Solo actualizamos si el estado cambia
    if new_status != old_status:
        # Actualizar orden
        db.table("orders").update({
            "status": new_status,
            "mp_payment_id": payment_id,
            "mp_status": payment["status"],
            "updated_at": "now()",
        }).eq("id", order_id).execute()

        # Registrar en historial
        db.table("order_status_history").insert({
            "order_id": order_id,
            "status": new_status,
            "note": f"Pago MP: {payment['status']} ({payment.get('status_detail', '')})",
        }).execute()

        print(f"✅ Orden {order_id} actualizada: {old_status} → {new_status}")

    # =========================================================================
    # 4. ENVIAR EMAILS SI EL PAGO FUE APROBADO
    # =========================================================================
    if payment["status"] == "approved" and old_status != "paid":
        # Obtener datos del cliente
        customer_result = (
            db.table("customers")
            .select("email, first_name, last_name")
            .eq("id", order["customer_id"])
            .execute()
        )

        if customer_result.data:
            customer = customer_result.data[0]
            customer_name = f"{customer['first_name']} {customer['last_name']}"

            # Email al cliente
            send_order_confirmation(
                to_email=customer["email"],
                customer_name=customer_name,
                order_number=order["order_number"],
                items=order.get("order_items", []),
                subtotal=float(order["subtotal"]),
                shipping_cost=float(order["shipping_cost"]),
                total=float(order["total"]),
            )

            # Email a Jacky
            send_new_order_notification(
                order_number=order["order_number"],
                customer_name=customer_name,
                total=float(order["total"]),
                items_count=len(order.get("order_items", [])),
            )

        # Descontar stock de las variantes
        for item in order.get("order_items", []):
            if item.get("variant_id"):
                # Obtener stock actual
                variant = (
                    db.table("product_variants")
                    .select("stock")
                    .eq("id", item["variant_id"])
                    .execute()
                )
                if variant.data and variant.data[0]["stock"] > 0:
                    new_stock = max(0, variant.data[0]["stock"] - item["quantity"])
                    db.table("product_variants").update({
                        "stock": new_stock,
                    }).eq("id", item["variant_id"]).execute()

    return {"status": "ok", "order_id": order_id, "new_status": new_status}
