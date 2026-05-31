# =============================================================================
# Middleware — Autenticación JWT
# Protege los endpoints de administración
# =============================================================================
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.config import settings

# Esquema de seguridad Bearer Token
security = HTTPBearer()

# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Datos dentro del JWT."""
    username: str
    exp: datetime


class LoginRequest(BaseModel):
    """Esquema del request de login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Respuesta del login exitoso."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de una contraseña."""
    return pwd_context.hash(password)


def create_access_token(username: str) -> tuple[str, datetime]:
    """
    Crea un JWT firmado con el username y expiración.
    Retorna (token, fecha_expiracion).
    """
    expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.JWT_EXPIRATION_HOURS
    )
    payload = {
        "sub": username,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, expires


def authenticate_admin(username: str, password: str) -> bool:
    """
    Verifica credenciales de admin.
    En esta versión simple, compara contra variables de entorno.
    """
    return (
        username.strip().lower() == settings.ADMIN_USERNAME.strip().lower()
        and password == settings.ADMIN_PASSWORD
    )


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency de FastAPI que protege endpoints de admin.
    Usar como: Depends(require_admin)
    Retorna el username si el token es válido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verificar que el usuario sigue siendo admin válido
    if username != settings.ADMIN_USERNAME:
        raise credentials_exception

    return username
