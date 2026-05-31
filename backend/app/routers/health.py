# =============================================================================
# Router — Health Check
# Endpoint simple para verificar que el backend está funcionando
# =============================================================================
import traceback
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Verifica que el backend está activo y conectado."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/health/db")
async def health_db():
    """
    Prueba la conexión a Supabase y devuelve diagnóstico detallado.
    Usar para troubleshoot problemas de conexión.
    """
    try:
        from app.database import get_supabase_admin
        db = get_supabase_admin()
        result = db.table("categories").select("id, name").limit(5).execute()
        return {
            "status": "ok",
            "supabase_url": settings.SUPABASE_URL,
            "service_key_prefix": settings.SUPABASE_SERVICE_KEY[:20] + "...",
            "categories_found": len(result.data),
            "data": result.data,
        }
    except Exception as e:
        return {
            "status": "error",
            "supabase_url": settings.SUPABASE_URL,
            "service_key_prefix": settings.SUPABASE_SERVICE_KEY[:20] + "..." if settings.SUPABASE_SERVICE_KEY else "NOT SET",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }
