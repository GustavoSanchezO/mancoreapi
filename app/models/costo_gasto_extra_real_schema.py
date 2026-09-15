from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CostoGastoExtraRealCrear(BaseModel):
    venta_id: int = Field(..., gt=0)
    gasto_extra_cotizado_id: int = Field(..., gt=0)
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    fecha: date


class CostoGastoExtraRealActualizar(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    fecha: date


class CostoGastoExtraRealRespuesta(BaseModel):
    id: int
    venta_id: int
    gasto_extra_cotizado_id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal
    fecha: date

    class Config:
        from_attributes = True