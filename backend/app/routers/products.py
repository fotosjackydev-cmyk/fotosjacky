# =============================================================================
# Router — Productos (Público)
# Endpoints de lectura pública para productos
# =============================================================================
from fastapi import APIRouter, HTTPException, Query
from app.database import get_supabase_admin
from app.models.product import ProductResponse, ProductListResponse

router = APIRouter(prefix="/api/products", tags=["Productos"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    featured: bool | None = Query(None, description="Filtrar por destacados"),
    search: str | None = Query(None, description="Buscar por nombre"),
    sort: str = Query("newest", description="Orden: newest, price_asc, price_desc"),
):
    """
    Lista productos con filtros, búsqueda y paginación.
    Incluye imágenes y variantes automáticamente.
    """
    db = get_supabase_admin()
    offset = (page - 1) * page_size

    # Construir query base
    query = (
        db.table("products")
        .select("*, product_images(*), product_variants(*)")
        .eq("active", True)
    )
    count_query = (
        db.table("products")
        .select("id", count="exact")
        .eq("active", True)
    )

    # Filtro por destacados
    if featured is not None:
        query = query.eq("featured", featured)
        count_query = count_query.eq("featured", featured)

    # Búsqueda por nombre
    if search:
        query = query.ilike("name", f"%{search}%")
        count_query = count_query.ilike("name", f"%{search}%")

    # Ordenamiento
    if sort == "price_asc":
        query = query.order("base_price", desc=False)
    elif sort == "price_desc":
        query = query.order("base_price", desc=True)
    else:  # newest
        query = query.order("created_at", desc=True)

    # Paginación
    query = query.range(offset, offset + page_size - 1)

    result = query.execute()
    count_result = count_query.execute()

    return ProductListResponse(
        data=_normalize_products(result.data),
        count=count_result.count or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ProductResponse)
async def get_product(slug: str):
    """
    Obtiene un producto por su slug.
    Incluye todas las imágenes y variantes.
    """
    db = get_supabase_admin()
    result = (
        db.table("products")
        .select("*, product_images(*), product_variants(*)")
        .eq("slug", slug)
        .eq("active", True)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product = result.data[0]
    product["images"] = product.pop("product_images", [])
    product["variants"] = product.pop("product_variants", [])

    return product


def _normalize_products(products: list[dict]) -> list[dict]:
    """Renombra las relaciones de Supabase a nombres amigables."""
    for product in products:
        product["images"] = product.pop("product_images", [])
        product["variants"] = product.pop("product_variants", [])
    return products
