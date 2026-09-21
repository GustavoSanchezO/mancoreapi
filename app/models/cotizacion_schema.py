from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class CotizacionEstadoActualizar(BaseModel):
    estado: Literal[
        "COTIZACION",
        "ENVIADA",
        "ACEPTADA",
        "RECHAZADA",
        "CANCELADA"
    ]

class MaterialCotizacionCrear(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    material_id: int | None = Field(default=None, gt=0)


class ManoObraCotizadaCrear(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)


class GastoExtraCotizadoCrear(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)


class PartidaCotizacionCrear(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)

    materiales: list[MaterialCotizacionCrear] = Field(
        default_factory=list
    )

    mano_obra: list[ManoObraCotizadaCrear] = Field(
        default_factory=list
    )

    gastos_extra: list[GastoExtraCotizadoCrear] = Field(
        default_factory=list
    )


class CotizacionCrear(BaseModel):
    rfq: str = Field(..., min_length=1)
    fecha: date
    cliente_id: int = Field(..., gt=0)
    proyecto_id: int = Field(..., gt=0)
    tiempo_entrega_estimado: str = Field(..., min_length=1)

    partidas: list[PartidaCotizacionCrear] = Field(
        ...,
        min_length=1
    )

    nota_importante_id: int | None = None
    anexos_fotograficos: list[str] = Field(default_factory=list)



class CotizacionRespuesta(BaseModel):
    id: int
    rfq: str
    fecha: date
    cliente_id: int
    proyecto_id: int
    usuario_id: int
    tiempo_entrega_estimado: str
    estado: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    nota_importante_id: int | None = None
    nota_importante_texto: str | None = None
    anexos_fotograficos: list[str] = []

    class Config:
        from_attributes = True

class MaterialCotizacionRespuesta(BaseModel):
    id: int
    material_id: int | None
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class ManoObraCotizadaRespuesta(BaseModel):
    id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class GastoExtraCotizadoRespuesta(BaseModel):
    id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class PartidaCotizacionRespuesta(BaseModel):
    id: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal

    materiales: list[MaterialCotizacionRespuesta]
    mano_obra: list[ManoObraCotizadaRespuesta]
    gastos_extra: list[GastoExtraCotizadoRespuesta]

    class Config:
        from_attributes = True

class CotizacionDetalleRespuesta(BaseModel):
    id: int
    rfq: str
    fecha: date
    cliente_id: int
    proyecto_id: int
    usuario_id: int
    tiempo_entrega_estimado: str
    estado: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    fecha_creacion: datetime | None
    nota_importante_id: int | None = None
    nota_importante_texto: str | None = None
    anexos_fotograficos: list[str] = []

    partidas: list[PartidaCotizacionRespuesta]

class CotizacionListaRespuesta(BaseModel):
    id: int
    rfq: str
    fecha: date
    cliente_id: int
    proyecto_id: int
    usuario_id: int
    tiempo_entrega_estimado: str
    estado: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    fecha_creacion: datetime
    nota_importante_id: int | None = None
    nota_importante_texto: str | None = None

    class Config:
        from_attributes = True

class MaterialCotizacionActualizar(BaseModel):
    id: int | None = None
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    material_id: int | None = Field(default=None, gt=0)


class ManoObraCotizadaActualizar(BaseModel):
    id: int | None = None
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)


class GastoExtraCotizadoActualizar(BaseModel):
    id: int | None = None
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)


class PartidaCotizacionActualizar(BaseModel):
    id: int | None = None
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)

    materiales: list[MaterialCotizacionActualizar] = Field(
        default_factory=list
    )

    mano_obra: list[ManoObraCotizadaActualizar] = Field(
        default_factory=list
    )

    gastos_extra: list[GastoExtraCotizadoActualizar] = Field(
        default_factory=list
    )


class CotizacionActualizar(BaseModel):
    rfq: str = Field(..., min_length=1)
    fecha: date
    cliente_id: int = Field(..., gt=0)
    proyecto_id: int = Field(..., gt=0)
    tiempo_entrega_estimado: str = Field(..., min_length=1)

    partidas: list[PartidaCotizacionActualizar] = Field(
        ...,
        min_length=1
    )

    nota_importante_id: int | None = None
    anexos_fotograficos: list[str] = Field(default_factory=list)