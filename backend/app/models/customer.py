# =============================================================================
# Modelos Pydantic — Clientes
# Esquemas para datos del comprador durante el checkout
# =============================================================================
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class CustomerBase(BaseModel):
    """Datos del cliente para el checkout."""
    email: EmailStr = Field(..., examples=["maria@gmail.com"])
    first_name: str = Field(..., min_length=1, max_length=100, examples=["María"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["López"])
    phone: str = Field(..., min_length=6, max_length=50, examples=["+5491155551234"])
    dni: str | None = Field(None, max_length=20, examples=["30123456"])


class CustomerCreate(CustomerBase):
    """Esquema para crear un cliente durante el checkout."""
    pass


class CustomerResponse(CustomerBase):
    """Respuesta con datos del cliente."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AddressCreate(BaseModel):
    """Dirección de envío para el checkout."""
    street: str = Field(..., min_length=1, max_length=200, examples=["Av. Corrientes"])
    street_number: str = Field(..., min_length=1, max_length=20, examples=["1234"])
    floor_apt: str | None = Field(None, max_length=50, examples=["3° B"])
    city: str = Field(..., min_length=1, max_length=100, examples=["Buenos Aires"])
    province: str = Field(..., min_length=1, max_length=100, examples=["CABA"])
    postal_code: str = Field(..., min_length=4, max_length=10, examples=["1043"])
