# =============================================================================
# Modelos Pydantic — Órdenes
# Esquemas para el checkout, órdenes y sus items
# =============================================================================
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.customer import CustomerCreate, AddressCreate


# --- Items del carrito / orden ------------------------------------------------

class CartItem(BaseModel):
    """Un item del carrito enviado desde el frontend."""
    product_id: str
    variant_id: str | None = None
    quantity: int = Field(..., ge=1, le=50)


class CartValidationRequest(BaseModel):
    """Request para validar un carrito completo."""
    items: list[CartItem] = Field(..., min_length=1)


class CartItemValidated(BaseModel):
    """Item del carrito con precio validado por el backend."""
    product_id: str
    product_name: str
    variant_id: str | None = None
    variant_name: str | None = None
    quantity: int
    unit_price: float
    subtotal: float
    in_stock: bool = True


class CartValidationResponse(BaseModel):
    """Respuesta de validación del carrito."""
    valid: bool
    items: list[CartItemValidated]
    subtotal: float
    errors: list[str] = []


# --- Checkout ----------------------------------------------------------------

class CheckoutRequest(BaseModel):
    """
    Request completo de checkout.
    Incluye items del carrito, datos del cliente y dirección de envío.
    """
    items: list[CartItem] = Field(..., min_length=1)
    customer: CustomerCreate
    shipping_address: AddressCreate
    shipping_method: str = Field("standard", examples=["standard", "express"])
    notes: str | None = None


class CheckoutResponse(BaseModel):
    """
    Respuesta del checkout.
    Incluye la URL de pago de Mercado Pago para redirigir al cliente.
    """
    order_id: str
    order_number: int
    total: float
    mp_init_point: str  # URL de Mercado Pago para pagar
    mp_sandbox_init_point: str | None = None  # URL sandbox para testing


# --- Órdenes -----------------------------------------------------------------

class OrderItemResponse(BaseModel):
    """Item individual de una orden."""
    product_name: str
    variant_name: str | None = None
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Respuesta pública de una orden (para el cliente)."""
    id: str
    order_number: int
    status: str
    subtotal: float
    shipping_cost: float
    total: float
    shipping_method: str | None = None
    shipping_tracking: str | None = None
    items: list[OrderItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class OrderAdminResponse(OrderResponse):
    """Respuesta extendida para el admin (incluye datos del cliente)."""
    customer_email: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    shipping_address: dict | None = None
    mp_payment_id: str | None = None
    mp_status: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class OrderStatusUpdate(BaseModel):
    """Request para actualizar el estado de una orden (admin)."""
    status: str = Field(..., examples=["paid", "preparing", "shipped", "delivered", "cancelled"])
    note: str | None = None
    shipping_tracking: str | None = None


# --- Mapeo de estados legibles ------------------------------------------------

ORDER_STATUS_LABELS = {
    "pending_payment": "⏳ Pendiente de pago",
    "paid": "💳 Pagado",
    "preparing": "📦 Preparando",
    "shipped": "🚚 Enviado",
    "delivered": "✅ Entregado",
    "cancelled": "❌ Cancelado",
    "refunded": "↩️ Reembolsado",
}
