# =============================================================================
# Router — Carrito
# Validación de items del carrito contra la base de datos
# =============================================================================
from fastapi import APIRouter, HTTPException
from app.database import get_supabase_admin
from app.models.order import CartValidationRequest, CartValidationResponse, CartItemValidated

router = APIRouter(prefix="/api/cart", tags=["Carrito"])


@router.post("/validate", response_model=CartValidationResponse)
async def validate_cart(cart: CartValidationRequest):
    """
    Valida los items del carrito.
    Verifica que los productos existan, estén activos, y calcula precios reales.

    El carrito se mantiene en localStorage del browser. Este endpoint se llama
    antes del checkout para asegurar que los precios y stock son correctos.
    """
    db = get_supabase_admin()
    validated_items = []
    errors = []
    subtotal = 0

    for item in cart.items:
        # Obtener producto
        product_result = (
            db.table("products")
            .select("id, name, base_price, active")
            .eq("id", item.product_id)
            .execute()
        )

        if not product_result.data:
            errors.append(f"Producto {item.product_id} no encontrado")
            continue

        product = product_result.data[0]

        if not product["active"]:
            errors.append(f"Producto '{product['name']}' ya no está disponible")
            continue

        # Calcular precio (base + modificador de variante)
        unit_price = float(product["base_price"])
        variant_name = None
        in_stock = True

        if item.variant_id:
            variant_result = (
                db.table("product_variants")
                .select("id, name, price_modifier, stock, active")
                .eq("id", item.variant_id)
                .eq("product_id", item.product_id)
                .execute()
            )

            if not variant_result.data:
                errors.append(f"Variante no encontrada para '{product['name']}'")
                continue

            variant = variant_result.data[0]

            if not variant["active"]:
                errors.append(f"Variante '{variant['name']}' de '{product['name']}' no está disponible")
                continue

            unit_price += float(variant.get("price_modifier", 0))
            variant_name = variant["name"]

            # Verificar stock si se maneja
            if variant.get("stock", 0) > 0 and variant["stock"] < item.quantity:
                in_stock = False
                errors.append(
                    f"Stock insuficiente para '{product['name']}' ({variant['name']}). "
                    f"Disponible: {variant['stock']}, pedido: {item.quantity}"
                )

        item_subtotal = unit_price * item.quantity
        subtotal += item_subtotal

        validated_items.append(CartItemValidated(
            product_id=item.product_id,
            product_name=product["name"],
            variant_id=item.variant_id,
            variant_name=variant_name,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=item_subtotal,
            in_stock=in_stock,
        ))

    return CartValidationResponse(
        valid=len(errors) == 0,
        items=validated_items,
        subtotal=subtotal,
        errors=errors,
    )
