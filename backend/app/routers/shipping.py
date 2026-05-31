# =============================================================================
# Router — Envíos
# Endpoints para obtener cotizaciones
# =============================================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.andreani import get_shipping_quotes

router = APIRouter(prefix="/api/shipping", tags=["Shipping"])

class QuoteRequest(BaseModel):
    zip_code: str
    weight_gr: int = 500
    volume_cm3: int = 0

class ShippingOption(BaseModel):
    id: str
    carrier: str
    method: str
    price: float
    estimated_days: str

@router.post("/quote", response_model=list[ShippingOption])
async def quote_shipping(request: QuoteRequest):
    """
    Obtiene opciones de envío disponibles para un código postal.
    """
    if not request.zip_code:
        raise HTTPException(status_code=400, detail="El código postal es requerido")
        
    quotes = get_shipping_quotes(
        zip_code=request.zip_code, 
        weight_gr=request.weight_gr,
        volume_cm3=request.volume_cm3
    )
    
    return quotes
