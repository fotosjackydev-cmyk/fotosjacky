# =============================================================================
# Fotos Jacky Backend — Configuración Central
# Lee variables de entorno desde .env
# =============================================================================
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuración centralizada de la aplicación."""

    # --- Supabase ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))

    # --- Admin ---
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")

    # --- App ---
    APP_NAME: str = os.getenv("APP_NAME", "Fotos Jacky")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5500")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5500,http://localhost:3000"
    ).split(",")

    # --- Storage ---
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "product-images")

    # --- Mercado Pago ---
    MP_ACCESS_TOKEN: str = os.getenv("MP_ACCESS_TOKEN", "")

    # --- Emails (Resend) ---
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "Fotos Jacky <noreply@fotosjacky.com>")

    # --- Andreani ---
    ANDREANI_USERNAME: str = os.getenv("ANDREANI_USERNAME", "")
    ANDREANI_PASSWORD: str = os.getenv("ANDREANI_PASSWORD", "")
    ANDREANI_CLIENT: str = os.getenv("ANDREANI_CLIENT", "")

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

settings = Settings()
