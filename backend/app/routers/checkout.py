# =============================================================================
# Router — Checkout
# Flujo completo: validar carrito → crear cliente → crear orden → crear pago MP
# =============================================================================
from fastapi import APIRouter, HTTPException
from app.database import get_supabase_admin
from app.models.order import CheckoutRequest, CheckoutResponse
from app.services.mercadopago import create_preference
from app.services.andreani import get_shipping_quotes
from app.config import settings

router = APIRouter(prefix="/api/checkout", tags=["Checkout"])


@router.post("", response_model=CheckoutResponse, status_code=201)
async def create_checkout(checkout: CheckoutRequest):
    """
    Crea una orden y genera el link de pago de Mercado Pago.

    Flujo:
        1. Valida los items del carrito (precios reales desde la DB)
        2. Crea o actualiza el cliente
        3. Crea la orden con estado 'pending_payment'
        4. Crea la preferencia en Mercado Pago
        5. Devuelve la URL de pago para redirigir al cliente

    El cliente paga en Mercado Pago y después MP nos notifica
    vía webhook. Ahí actualizamos el estado de la orden.
    """
    db = get_supabase_admin()

    # =========================================================================
    # 1. VALIDAR ITEMS Y CALCULAR PRECIOS
    # =========================================================================
    order_items = []
    mp_items = []
    subtotal = 0

    for item in checkout.items:
        # Obtener producto
        product_result = (
            db.table("products")
            .select("id, name, base_price, active")
            .eq("id", item.product_id)
            .eq("active", True)
            .execute()
        )

        if not product_result.data:
            raise HTTPException(
                status_code=400,
                detail=f"Producto {item.product_id} no encontrado o no disponible",
            )

        product = product_result.data[0]
        unit_price = float(product["base_price"])
        variant_name = None

        # Procesar variante
        if item.variant_id:
            variant_result = (
                db.table("product_variants")
                .select("id, name, price_modifier, stock, active")
                .eq("id", item.variant_id)
                .eq("product_id", item.product_id)
                .execute()
            )

            if not variant_result.data or not variant_result.data[0]["active"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Variante no disponible para '{product['name']}'",
                )

            variant = variant_result.data[0]
            unit_price += float(variant.get("price_modifier", 0))
            variant_name = variant["name"]

            # Verificar stock
            stock = variant.get("stock", 0)
            if stock > 0 and stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{product['name']}' ({variant['name']})",
                )

        item_subtotal = unit_price * item.quantity
        subtotal += item_subtotal

        # Para nuestra DB
        order_items.append({
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "product_name": product["name"],
            "variant_name": variant_name,
            "quantity": item.quantity,
            "unit_price": unit_price,
        })

        # Para Mercado Pago
        mp_items.append({
            "title": f"{product['name']}{f' - {variant_name}' if variant_name else ''}",
            "quantity": item.quantity,
            "unit_price": unit_price,
        })

    # =========================================================================
    # 2. CREAR O ACTUALIZAR CLIENTE
    # =========================================================================
    customer_data = checkout.customer.model_dump()

    # Buscar cliente existente por email
    existing_customer = (
        db.table("customers")
        .select("id")
        .eq("email", customer_data["email"])
        .execute()
    )

    if existing_customer.data:
        # Actualizar datos del cliente existente
        customer_id = existing_customer.data[0]["id"]
        db.table("customers").update(customer_data).eq("id", customer_id).execute()
    else:
        # Crear nuevo cliente
        new_customer = db.table("customers").insert(customer_data).execute()
        if not new_customer.data:
            raise HTTPException(status_code=500, detail="Error al crear cliente")
        customer_id = new_customer.data[0]["id"]

    # Guardar dirección
    address_data = checkout.shipping_address.model_dump()
    address_data["customer_id"] = customer_id
    address_data["is_default"] = True
    db.table("addresses").insert(address_data).execute()

    # =========================================================================
    # 3. CREAR ORDEN Y CALCULAR ENVÍO
    # =========================================================================
    shipping_cost = 0

    # Si hay un método de envío seleccionado y no es "retiro_local"
    if checkout.shipping_method and "andreani" in checkout.shipping_method:
        # Calcular peso aproximado del carrito (default a 500g si no está configurado)
        total_weight = 500 * len(order_items)
        
        quotes = get_shipping_quotes(
            zip_code=checkout.shipping_address.postal_code,
            weight_gr=total_weight
        )
        
        # Buscar la opción seleccionada por el usuario
        selected_quote = next((q for q in quotes if q["id"] == checkout.shipping_method), None)
        if selected_quote:
            shipping_cost = selected_quote["price"]

    order_data = {
        "customer_id": customer_id,
        "status": "pending_payment",
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "total": subtotal + shipping_cost,
        "shipping_address": address_data,
        "shipping_method": checkout.shipping_method,
        "notes": checkout.notes,
    }

    order_result = db.table("orders").insert(order_data).execute()

    if not order_result.data:
        raise HTTPException(status_code=500, detail="Error al crear orden")

    order = order_result.data[0]
    order_id = order["id"]
    order_number = order["order_number"]

    # Guardar items de la orden
    for oi in order_items:
        oi["order_id"] = order_id
    db.table("order_items").insert(order_items).execute()

    # Registrar en historial de estados
    db.table("order_status_history").insert({
        "order_id": order_id,
        "status": "pending_payment",
        "note": "Orden creada, pendiente de pago",
    }).execute()

    # =========================================================================
    # 4. CREAR PREFERENCIA EN MERCADO PAGO
    # =========================================================================
    try:
        mp_result = create_preference(
            order_id=order_id,
            order_number=order_number,
            items=mp_items,
            payer={
                "first_name": checkout.customer.first_name,
                "last_name": checkout.customer.last_name,
                "email": checkout.customer.email,
                "phone": checkout.customer.phone,
            },
            shipping_cost=shipping_cost,
        )
    except Exception as e:
        # Si falla MP, la orden ya está creada. Guardamos el error.
        db.table("orders").update({
            "notes": f"Error al crear pago MP: {str(e)}",
        }).eq("id", order_id).execute()
        raise HTTPException(
            status_code=502,
            detail=f"Error al conectar con Mercado Pago: {str(e)}",
        )

    # Guardar ID de preferencia de MP en la orden
    db.table("orders").update({
        "mp_preference_id": mp_result["preference_id"],
    }).eq("id", order_id).execute()

    # =========================================================================
    # 5. DEVOLVER URL DE PAGO
    # =========================================================================
    return CheckoutResponse(
        order_id=order_id,
        order_number=order_number,
        total=subtotal + shipping_cost,
        mp_init_point=mp_result["init_point"],
        mp_sandbox_init_point=mp_result.get("sandbox_init_point"),
    )
