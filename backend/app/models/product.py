# =============================================================================
# Modelos Pydantic — Productos
# Esquemas de validación para request/response de productos
# =============================================================================
from pydantic import BaseModel, Field
from datetime import datetime


# --- Imágenes de producto ---------------------------------------------------

class ProductImageBase(BaseModel):
    url: str
    alt: str | None = None
    position: int = 0


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    id: str

    class Config:
        from_attributes = True


# --- Variantes de producto ---------------------------------------------------

class ProductVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["A4 - Mate"])
    sku: str | None = None
    price_modifier: float = Field(0, examples=[500.00])
    stock: int = Field(0, ge=0)
    active: bool = True


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    sku: str | None = None
    price_modifier: float | None = None
    stock: int | None = Field(None, ge=0)
    active: bool | None = None


class ProductVariantResponse(ProductVariantBase):
    id: str
    product_id: str

    class Config:
        from_attributes = True


# --- Producto principal ------------------------------------------------------

class ProductBase(BaseModel):
    """Campos compartidos entre creación y respuesta."""
    name: str = Field(..., min_length=1, max_length=200, examples=["Cuadro Canvas 30x40"])
    slug: str = Field(..., min_length=1, max_length=200, examples=["cuadro-canvas-30x40"])
    description: str | None = None
    base_price: float = Field(..., gt=0, examples=[15000.00])
    sku: str | None = None
    weight_grams: int = Field(500, ge=0)
    dimensions_cm: dict | None = Field(None, examples=[{"l": 30, "w": 40, "h": 2}])
    active: bool = True
    featured: bool = False
    category_id: str | None = None


class ProductCreate(ProductBase):
    """Esquema para crear un producto. Puede incluir variantes inline."""
    variants: list[ProductVariantCreate] | None = None


class ProductUpdate(BaseModel):
    """Esquema para actualizar un producto (todos los campos opcionales)."""
    name: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    base_price: float | None = Field(None, gt=0)
    sku: str | None = None
    weight_grams: int | None = Field(None, ge=0)
    dimensions_cm: dict | None = None
    active: bool | None = None
    featured: bool | None = None
    category_id: str | None = None


class ProductResponse(ProductBase):
    """Esquema de respuesta con campos generados y relaciones."""
    id: str
    created_at: datetime
    images: list[ProductImageResponse] = []
    variants: list[ProductVariantResponse] = []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Respuesta paginada de productos."""
    data: list[ProductResponse]
    count: int
    page: int
    page_size: int
