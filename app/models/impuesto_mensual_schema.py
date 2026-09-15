from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ImpuestoMensualCrear(BaseModel):
    año: int = Field(..., ge=2000)
    mes: int = Field(..., ge=1, le=12)
    total_impuestos: Decimal = Field(..., ge=0)


class ImpuestoMensualActualizar(BaseModel):
    total_impuestos: Decimal = Field(..., ge=0)


class ImpuestoMensualRespuesta(BaseModel):
    id: int
    año: int
    mes: int
    total_impuestos: Decimal
    fecha_creacion: datetime

    class Config:
        from_attributes = True