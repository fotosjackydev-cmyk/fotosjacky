# =============================================================================
# Fotos Jacky Backend — Entry Point
# FastAPI application con CORS, routers y documentación
# =============================================================================
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle de la app: se ejecuta al iniciar y al apagar.
    Útil para inicializar conexiones, verificar config, etc.
    """
    # --- Startup ---
    print(f"🚀 {settings.APP_NAME} Backend iniciando...")
    print(f"   Entorno: {settings.APP_ENV}")
    print(f"   Supabase: {settings.SUPABASE_URL[:30]}..." if settings.SUPABASE_URL else "   ⚠️  SUPABASE_URL no configurada")
    print(f"   Mercado Pago: {'✅ configurado' if settings.MP_ACCESS_TOKEN else '⚠️  MP_ACCESS_TOKEN no configurado'}")
    print(f"   Emails: {'✅ Resend configurado' if settings.RESEND_API_KEY else '⚠️  RESEND_API_KEY no configurado'}")
    print(f"   CORS: {settings.CORS_ORIGINS}")
    print(f"   📋 Admin panel: http://localhost:8000/admin/")
    yield
    # --- Shutdown ---
    print(f"👋 {settings.APP_NAME} Backend apagándose...")


# Crear la app
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description=(
        "Backend API para el ecommerce de Fotos Jacky. "
        "Gestión de productos, categorías, órdenes y pagos."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",      # ReDoc
)

# --- CORS ---
# Permite que el frontend (en otro dominio) haga requests al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registrar Routers ---
from app.routers import health, categories, products, admin, cart, checkout, orders, webhooks, shipping

# Fase 1 — Productos y Categorías
app.include_router(health.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(admin.router)

# Fase 2 y 3 — Carrito, Checkout, Órdenes, Pagos y Envíos
app.include_router(cart.router)
app.include_router(shipping.router)
app.include_router(checkout.router)
app.include_router(orders.router)
app.include_router(webhooks.router)


# --- Root endpoint ---
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con info de la API."""
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "admin": "/admin/",
        "checkout_enabled": bool(settings.MP_ACCESS_TOKEN),
    }


# --- Admin Panel (archivos estáticos) ---
admin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin")
if os.path.exists(admin_dir):
    app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin")
