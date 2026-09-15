from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CostoMaterialRealCrear(BaseModel):
    venta_id: int = Field(..., gt=0)
    material_cotizacion_id: int = Field(..., gt=0)
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    fecha: date


class CostoMaterialRealRespuesta(BaseModel):
    id: int
    venta_id: int
    material_cotizacion_id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal
    fecha: date

    class Config:
        from_attributes = True

class CostoMaterialRealActualizar(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    fecha: date