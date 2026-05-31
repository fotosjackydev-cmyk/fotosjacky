# =============================================================================
# Router — Administración
# Endpoints protegidos para gestionar productos, categorías e imágenes
# =============================================================================
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.database import get_supabase_admin
from app.middleware.auth import (
    require_admin,
    authenticate_admin,
    create_access_token,
    LoginRequest,
    TokenResponse,
)
from app.models.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductVariantCreate,
    ProductVariantUpdate,
)
from app.models.order import OrderStatusUpdate, ORDER_STATUS_LABELS
from app.services.storage import upload_product_image, delete_image
from app.services.email import send_order_shipped
import json

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# =============================================================================
# AUTH
# =============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login de administrador. Devuelve un JWT Bearer token.
    """
    if not authenticate_admin(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
        )

    token, expires = create_access_token(request.username)
    expires_in = int((expires - __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    )).total_seconds())

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
    )


# =============================================================================
# DASHBOARD
# =============================================================================

@router.get("/dashboard")
async def get_dashboard(admin: str = Depends(require_admin)):
    """
    Métricas básicas para el dashboard del admin.
    """
    db = get_supabase_admin()

    # Contar productos
    products_result = db.table("products").select("id", count="exact").execute()
    # Contar categorías
    categories_result = db.table("categories").select("id", count="exact").execute()

    # Contar órdenes por estado
    orders_result = db.table("orders").select("id", count="exact").execute()
    pending_orders = db.table("orders").select("id", count="exact").eq("status", "paid").execute()

    return {
        "total_products": products_result.count or 0,
        "total_categories": categories_result.count or 0,
        "total_orders": orders_result.count or 0,
        "pending_dispatch": pending_orders.count or 0,
        "admin_user": admin,
    }


# =============================================================================
# CRUD CATEGORÍAS
# =============================================================================

@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreate,
    admin: str = Depends(require_admin),
):
    """Crea una nueva categoría."""
    db = get_supabase_admin()

    # Verificar que el slug no exista
    existing = db.table("categories").select("id").eq("slug", category.slug).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese slug")

    result = db.table("categories").insert(category.model_dump()).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear categoría")

    return result.data[0]


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    updates: CategoryUpdate,
    admin: str = Depends(require_admin),
):
    """Actualiza una categoría existente."""
    db = get_supabase_admin()

    # Filtrar campos None (no enviados)
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    result = (
        db.table("categories")
        .update(update_data)
        .eq("id", category_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return result.data[0]


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    admin: str = Depends(require_admin),
):
    """Elimina una categoría (soft delete: la desactiva)."""
    db = get_supabase_admin()

    result = (
        db.table("categories")
        .update({"active": False})
        .eq("id", category_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return {"message": "Categoría desactivada correctamente"}


# =============================================================================
# CRUD PRODUCTOS
# =============================================================================

@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    admin: str = Depends(require_admin),
):
    """
    Crea un nuevo producto.
    Opcionalmente puede incluir variantes inline.
    """
    db = get_supabase_admin()

    # Verificar que el slug no exista
    existing = db.table("products").select("id").eq("slug", product.slug).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Ya existe un producto con ese slug")

    # Separar variantes del producto principal
    variants_data = product.variants
    product_data = product.model_dump(exclude={"variants"})

    # Crear producto
    result = db.table("products").insert(product_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear producto")

    product_id = result.data[0]["id"]

    # Crear variantes si se enviaron
    created_variants = []
    if variants_data:
        for variant in variants_data:
            variant_dict = variant.model_dump()
            variant_dict["product_id"] = product_id
            v_result = db.table("product_variants").insert(variant_dict).execute()
            if v_result.data:
                created_variants.append(v_result.data[0])

    # Armar respuesta completa
    response = result.data[0]
    response["images"] = []
    response["variants"] = created_variants

    return response


@router.get("/products")
async def admin_list_products(
    admin: str = Depends(require_admin),
    page: int = 1,
    page_size: int = 50,
    include_inactive: bool = True,
):
    """
    Lista todos los productos (incluyendo inactivos) para el panel admin.
    """
    db = get_supabase_admin()
    offset = (page - 1) * page_size

    query = (
        db.table("products")
        .select("*, product_images(*), product_variants(*), categories(name)")
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
    )

    if not include_inactive:
        query = query.eq("active", True)

    result = query.execute()

    # Normalizar relaciones
    for product in result.data:
        product["images"] = product.pop("product_images", [])
        product["variants"] = product.pop("product_variants", [])
        cat = product.pop("categories", None)
        product["category_name"] = cat["name"] if cat else None

    return {
        "data": result.data,
        "page": page,
        "page_size": page_size,
    }


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    updates: ProductUpdate,
    admin: str = Depends(require_admin),
):
    """Actualiza un producto existente."""
    db = get_supabase_admin()

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    result = (
        db.table("products")
        .update(update_data)
        .eq("id", product_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Obtener producto completo con relaciones
    full = (
        db.table("products")
        .select("*, product_images(*), product_variants(*)")
        .eq("id", product_id)
        .execute()
    )

    product = full.data[0]
    product["images"] = product.pop("product_images", [])
    product["variants"] = product.pop("product_variants", [])

    return product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    admin: str = Depends(require_admin),
):
    """Elimina un producto (soft delete)."""
    db = get_supabase_admin()

    result = (
        db.table("products")
        .update({"active": False})
        .eq("id", product_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"message": "Producto desactivado correctamente"}


# =============================================================================
# VARIANTES
# =============================================================================

@router.post("/products/{product_id}/variants")
async def add_variant(
    product_id: str,
    variant: ProductVariantCreate,
    admin: str = Depends(require_admin),
):
    """Agrega una variante a un producto existente."""
    db = get_supabase_admin()

    # Verificar que el producto existe
    product = db.table("products").select("id").eq("id", product_id).execute()
    if not product.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    variant_data = variant.model_dump()
    variant_data["product_id"] = product_id

    result = db.table("product_variants").insert(variant_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear variante")

    return result.data[0]


@router.put("/products/{product_id}/variants/{variant_id}")
async def update_variant(
    product_id: str,
    variant_id: str,
    updates: ProductVariantUpdate,
    admin: str = Depends(require_admin),
):
    """Actualiza una variante."""
    db = get_supabase_admin()

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    result = (
        db.table("product_variants")
        .update(update_data)
        .eq("id", variant_id)
        .eq("product_id", product_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    return result.data[0]


@router.delete("/products/{product_id}/variants/{variant_id}")
async def delete_variant(
    product_id: str,
    variant_id: str,
    admin: str = Depends(require_admin),
):
    """Elimina una variante permanentemente."""
    db = get_supabase_admin()

    result = (
        db.table("product_variants")
        .delete()
        .eq("id", variant_id)
        .eq("product_id", product_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    return {"message": "Variante eliminada correctamente"}


# =============================================================================
# IMÁGENES
# =============================================================================

@router.post("/products/{product_id}/images")
async def upload_image(
    product_id: str,
    file: UploadFile = File(...),
    alt: str = Form(""),
    position: int = Form(0),
    admin: str = Depends(require_admin),
):
    """
    Sube una imagen para un producto.
    La imagen se almacena en Supabase Storage.
    """
    db = get_supabase_admin()

    # Verificar que el producto existe
    product = db.table("products").select("id").eq("id", product_id).execute()
    if not product.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Usar: {', '.join(allowed_types)}",
        )

    # Subir a Supabase Storage
    try:
        image_url = await upload_product_image(file, product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")

    # Guardar referencia en la DB
    image_data = {
        "product_id": product_id,
        "url": image_url,
        "alt": alt or file.filename,
        "position": position,
    }
    result = db.table("product_images").insert(image_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al guardar referencia de imagen")

    return result.data[0]


@router.delete("/products/{product_id}/images/{image_id}")
async def remove_image(
    product_id: str,
    image_id: str,
    admin: str = Depends(require_admin),
):
    """Elimina una imagen de un producto."""
    db = get_supabase_admin()

    # Obtener la imagen para borrarla del storage
    img = (
        db.table("product_images")
        .select("*")
        .eq("id", image_id)
        .eq("product_id", product_id)
        .execute()
    )

    if not img.data:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Borrar del storage
    try:
        await delete_image(img.data[0]["url"])
    except Exception:
        pass  # Si falla el borrado del storage, seguimos igual

    # Borrar de la DB
    db.table("product_images").delete().eq("id", image_id).execute()

    return {"message": "Imagen eliminada correctamente"}


# =============================================================================
# GESTIÓN DE ÓRDENES
# =============================================================================

@router.get("/orders")
async def admin_list_orders(
    admin: str = Depends(require_admin),
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    """
    Lista todas las órdenes con datos del cliente.
    Filtro opcional por estado.
    """
    db = get_supabase_admin()
    offset = (page - 1) * page_size

    query = (
        db.table("orders")
        .select("*, order_items(*), customers(email, first_name, last_name, phone)")
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
    )

    if status:
        query = query.eq("status", status)

    result = query.execute()

    # Normalizar y enriquecer datos
    for order in result.data:
        customer = order.pop("customers", None)
        order["items"] = order.pop("order_items", [])
        order["customer_email"] = customer["email"] if customer else None
        order["customer_name"] = (
            f"{customer['first_name']} {customer['last_name']}"
            if customer else None
        )
        order["customer_phone"] = customer["phone"] if customer else None
        order["status_label"] = ORDER_STATUS_LABELS.get(order["status"], order["status"])

    return {
        "data": result.data,
        "page": page,
        "page_size": page_size,
    }


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    update: OrderStatusUpdate,
    admin: str = Depends(require_admin),
):
    """
    Actualiza el estado de una orden.
    Si se marca como 'shipped' y se incluye tracking, envía email al cliente.
    """
    db = get_supabase_admin()

    # Verificar que la orden existe
    order_result = (
        db.table("orders")
        .select("*, customers(email, first_name, last_name)")
        .eq("id", order_id)
        .execute()
    )

    if not order_result.data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order = order_result.data[0]
    old_status = order["status"]

    # Preparar datos de actualización
    update_data = {
        "status": update.status,
        "updated_at": "now()",
    }
    if update.shipping_tracking:
        update_data["shipping_tracking"] = update.shipping_tracking

    # Actualizar orden
    db.table("orders").update(update_data).eq("id", order_id).execute()

    # Registrar en historial
    db.table("order_status_history").insert({
        "order_id": order_id,
        "status": update.status,
        "note": update.note or f"Estado actualizado por admin: {old_status} → {update.status}",
    }).execute()

    # Enviar email si se marcó como enviado
    if update.status == "shipped" and update.shipping_tracking:
        customer = order.get("customers")
        if customer:
            send_order_shipped(
                to_email=customer["email"],
                customer_name=f"{customer['first_name']} {customer['last_name']}",
                order_number=order["order_number"],
                tracking_number=update.shipping_tracking,
                shipping_method=order.get("shipping_method", "andreani"),
            )

    return {
        "message": f"Orden actualizada: {old_status} → {update.status}",
        "order_id": order_id,
        "new_status": update.status,
        "status_label": ORDER_STATUS_LABELS.get(update.status, update.status),
    }


@router.get("/orders/{order_id}")
async def admin_get_order(
    order_id: str,
    admin: str = Depends(require_admin),
):
    """Obtiene detalle completo de una orden para el admin."""
    db = get_supabase_admin()

    result = (
        db.table("orders")
        .select("*, order_items(*), customers(email, first_name, last_name, phone, dni)")
        .eq("id", order_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order = result.data[0]
    customer = order.pop("customers", None)
    order["items"] = order.pop("order_items", [])
    order["customer_email"] = customer["email"] if customer else None
    order["customer_name"] = (
        f"{customer['first_name']} {customer['last_name']}"
        if customer else None
    )
    order["customer_phone"] = customer.get("phone") if customer else None
    order["customer_dni"] = customer.get("dni") if customer else None
    order["status_label"] = ORDER_STATUS_LABELS.get(order["status"], order["status"])

    # Obtener historial
    history = (
        db.table("order_status_history")
        .select("status, note, created_at")
        .eq("order_id", order_id)
        .order("created_at", desc=False)
        .execute()
    )
    order["history"] = history.data

    return order
