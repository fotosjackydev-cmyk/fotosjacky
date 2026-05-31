# =============================================================================
# Router — Categorías (Público)
# Endpoints de lectura pública para categorías
# =============================================================================
from fastapi import APIRouter, HTTPException, Query
from app.database import get_supabase_admin
from app.models.category import CategoryResponse, CategoryListResponse

router = APIRouter(prefix="/api/categories", tags=["Categorías"])


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    active_only: bool = Query(True, description="Solo categorías activas"),
):
    """
    Lista todas las categorías.
    Por defecto solo muestra las activas (para el frontend público).
    """
    db = get_supabase_admin()
    query = db.table("categories").select("*").order("position")

    if active_only:
        query = query.eq("active", True)

    result = query.execute()

    return CategoryListResponse(
        data=result.data,
        count=len(result.data),
    )


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(slug: str):
    """Obtiene una categoría por su slug."""
    db = get_supabase_admin()
    result = db.table("categories").select("*").eq("slug", slug).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return result.data[0]


@router.get("/{slug}/products")
async def get_category_products(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Lista los productos de una categoría.
    Incluye imágenes y variantes de cada producto.
    """
    db = get_supabase_admin()

    # Primero obtener la categoría
    cat_result = db.table("categories").select("id").eq("slug", slug).execute()
    if not cat_result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    category_id = cat_result.data[0]["id"]

    # Calcular offset para paginación
    offset = (page - 1) * page_size

    # Obtener productos con imágenes y variantes
    result = (
        db.table("products")
        .select("*, product_images(*), product_variants(*)")
        .eq("category_id", category_id)
        .eq("active", True)
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )

    # Contar total para paginación
    count_result = (
        db.table("products")
        .select("id", count="exact")
        .eq("category_id", category_id)
        .eq("active", True)
        .execute()
    )

    return {
        "data": _normalize_products(result.data),
        "count": count_result.count or 0,
        "page": page,
        "page_size": page_size,
    }


def _normalize_products(products: list[dict]) -> list[dict]:
    """
    Normaliza la respuesta de productos para que las relaciones
    tengan nombres consistentes (images, variants).
    """
    for product in products:
        product["images"] = product.pop("product_images", [])
        product["variants"] = product.pop("product_variants", [])
    return products
