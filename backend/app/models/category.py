# =============================================================================
# Modelos Pydantic — Categorías
# Esquemas de validación para request/response de categorías
# =============================================================================
from pydantic import BaseModel, Field
from datetime import datetime


class CategoryBase(BaseModel):
    """Campos compartidos entre creación y respuesta."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Cuadros"])
    slug: str = Field(..., min_length=1, max_length=100, examples=["cuadros"])
    description: str | None = Field(None, examples=["Cuadros en canvas y madera"])
    image_url: str | None = None
    position: int = Field(0, ge=0)
    active: bool = True


class CategoryCreate(CategoryBase):
    """Esquema para crear una categoría."""
    pass


class CategoryUpdate(BaseModel):
    """Esquema para actualizar una categoría (todos los campos opcionales)."""
    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = None
    position: int | None = Field(None, ge=0)
    active: bool | None = None


class CategoryResponse(CategoryBase):
    """Esquema de respuesta con campos generados por la DB."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Respuesta paginada de categorías."""
    data: list[CategoryResponse]
    count: int
