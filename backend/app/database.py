# =============================================================================
# Fotos Jacky Backend — Conexión a Supabase
# Inicializa el cliente de Supabase para DB y Storage
# =============================================================================
from supabase import create_client, Client
from app.config import settings

# Cliente con service_role key — acceso completo (para operaciones del backend)
_supabase_admin: Client | None = None

# Cliente con anon key — acceso restringido por RLS (para operaciones públicas)
_supabase_public: Client | None = None


def get_supabase_admin() -> Client:
    """
    Retorna el cliente Supabase con permisos de administrador.
    Usa service_role key → bypasea Row Level Security.
    Usar SOLO desde el backend, nunca exponer esta key.
    """
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    return _supabase_admin


def get_supabase_public() -> Client:
    """
    Retorna el cliente Supabase con permisos públicos.
    Usa anon key → respeta Row Level Security.
    """
    global _supabase_public
    if _supabase_public is None:
        _supabase_public = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return _supabase_public
