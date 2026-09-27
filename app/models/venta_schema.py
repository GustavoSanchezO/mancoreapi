from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from app.models.cotizacion_schema import (
    PartidaCotizacionRespuesta
)

class VentaCrear(BaseModel):
    cotizacion_id: int = Field(..., gt=0)
    fecha: date
    fecha_pago: date


class VentaRespuesta(BaseModel):
    id: int
    cotizacion_id: int
    fecha: date
    fecha_pago: date
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class VentaDetalleRespuesta(BaseModel):
    id: int
    cotizacion_id: int
    fecha: date
    fecha_pago: date
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class VentaClienteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre_empresa: str
    direccion: str


class VentaProyectoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    descripcion: str
    estado: str


class VentaCotizacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rfq: str
    fecha: date
    tiempo_entrega_estimado: str
    estado: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    partidas: list[PartidaCotizacionRespuesta]


class VentaDetalleCompletoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cotizacion_id: int
    fecha: date
    fecha_pago: date
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    fecha_creacion: datetime

    cliente: VentaClienteRespuesta
    proyecto: VentaProyectoRespuesta
    cotizacion: VentaCotizacionRespuesta

class VentaEstadoActualizar(BaseModel):
    estado: Literal[
        "PENDIENTE",
        "PAGADA",
        "CANCELADA"
    ]

class VentaRentabilidadCostosRespuesta(BaseModel):
    materiales: Decimal
    mano_obra: Decimal
    gastos_extra: Decimal
    impuesto: Decimal
    costo_total: Decimal


class VentaRentabilidadRespuesta(BaseModel):
    venta_id: int
    fecha: date
    estado: str

    ingreso: Decimal

    costos: VentaRentabilidadCostosRespuesta

    utilidad: Decimal
    margen_porcentaje: Decimal
class VentaActualizar(BaseModel):
    fecha: date | None = None
    fecha_pago: date | None = None
