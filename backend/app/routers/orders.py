# =============================================================================
# Router — Órdenes (Público)
# Consulta de estado de orden para el cliente
# =============================================================================
from fastapi import APIRouter, HTTPException
from app.database import get_supabase_admin
from app.models.order import OrderResponse, OrderItemResponse, ORDER_STATUS_LABELS

router = APIRouter(prefix="/api/orders", tags=["Órdenes"])


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """
    Obtiene el estado de una orden.
    Endpoint público que el cliente usa desde la página de confirmación.
    """
    db = get_supabase_admin()

    # Obtener orden
    order_result = (
        db.table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_result.data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order = order_result.data[0]

    # Obtener items de la orden
    items_result = (
        db.table("order_items")
        .select("product_name, variant_name, quantity, unit_price")
        .eq("order_id", order_id)
        .execute()
    )

    order["items"] = items_result.data

    return order


@router.get("/{order_id}/status")
async def get_order_status(order_id: str):
    """
    Obtiene solo el estado actual de una orden (lightweight).
    Útil para polling desde el frontend.
    """
    db = get_supabase_admin()

    result = (
        db.table("orders")
        .select("id, order_number, status, shipping_tracking, updated_at")
        .eq("id", order_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order = result.data[0]
    order["status_label"] = ORDER_STATUS_LABELS.get(order["status"], order["status"])

    return order


@router.get("/{order_id}/history")
async def get_order_history(order_id: str):
    """
    Obtiene el historial de estados de una orden.
    Muestra la línea de tiempo completa.
    """
    db = get_supabase_admin()

    # Verificar que la orden existe
    order_exists = db.table("orders").select("id").eq("id", order_id).execute()
    if not order_exists.data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    result = (
        db.table("order_status_history")
        .select("status, note, created_at")
        .eq("order_id", order_id)
        .order("created_at", desc=False)
        .execute()
    )

    # Agregar labels legibles
    for entry in result.data:
        entry["status_label"] = ORDER_STATUS_LABELS.get(entry["status"], entry["status"])

    return {"order_id": order_id, "history": result.data}
