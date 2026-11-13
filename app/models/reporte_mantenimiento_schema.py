from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class ActividadMantenimientoCrear(BaseModel):
    item_numero: int | None = Field(default=None, ge=1)
    actividad: str = Field(..., min_length=1)
    estado: str = Field(..., min_length=1)
    observaciones: str | None = None


class SeccionMantenimientoCrear(BaseModel):
    orden: int | None = Field(default=None, ge=1)
    titulo: str = Field(..., min_length=1)
    actividades: list[ActividadMantenimientoCrear] = Field(..., min_length=1)


class ParteReemplazoCrear(BaseModel):
    orden: int | None = Field(default=None, ge=1)
    descripcion: str = Field(..., min_length=1)
    imagenes: list[str] = Field(default_factory=list)


class ReporteMantenimientoCrear(BaseModel):
    folio: str = Field(..., min_length=1, max_length=100)
    nombre_documento: str | None = Field(default="Reporte de Mantenimiento", max_length=255)
    cliente_id: int = Field(..., gt=0)
    tipo_mantenimiento: str = Field(..., min_length=1, max_length=255)
    unidad: str = Field(..., min_length=1, max_length=255)
    marca: str = Field(..., min_length=1, max_length=255)
    modelo: str = Field(..., min_length=1, max_length=255)
    observaciones_generales: str | None = None
    secciones: list[SeccionMantenimientoCrear] = Field(..., min_length=1)
    anexos_fotograficos: list[str] = Field(default_factory=list)
    partes_reemplazo: list[ParteReemplazoCrear] = Field(default_factory=list)


class ReporteMantenimientoActualizar(BaseModel):
    folio: str = Field(..., min_length=1, max_length=100)
    nombre_documento: str | None = Field(default="Reporte de Mantenimiento", max_length=255)
    cliente_id: int = Field(..., gt=0)
    tipo_mantenimiento: str = Field(..., min_length=1, max_length=255)
    unidad: str = Field(..., min_length=1, max_length=255)
    marca: str = Field(..., min_length=1, max_length=255)
    modelo: str = Field(..., min_length=1, max_length=255)
    observaciones_generales: str | None = None
    secciones: list[SeccionMantenimientoCrear] = Field(..., min_length=1)
    anexos_fotograficos: list[str] = Field(default_factory=list)
    partes_reemplazo: list[ParteReemplazoCrear] = Field(default_factory=list)


class ActividadMantenimientoRespuesta(BaseModel):
    id: int
    item_numero: int
    actividad: str
    estado: str
    observaciones: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SeccionMantenimientoRespuesta(BaseModel):
    id: int
    orden: int
    titulo: str
    actividades: list[ActividadMantenimientoRespuesta]

    model_config = ConfigDict(from_attributes=True)


class ParteReemplazoRespuesta(BaseModel):
    id: int
    orden: int
    descripcion: str
    imagenes: list[str] = Field(default_factory=list)


class ReporteMantenimientoListaRespuesta(BaseModel):
    id: int
    folio: str
    nombre_documento: str
    titulo_documento: str
    fecha: date
    cliente_id: int
    cliente_nombre: str
    usuario_id: int
    tipo_mantenimiento: str
    unidad: str
    marca: str
    modelo: str
    fecha_creacion: datetime
    total_secciones: int
    total_actividades: int


class ReporteMantenimientoDetalleRespuesta(BaseModel):
    id: int
    folio: str
    nombre_documento: str
    titulo_documento: str
    fecha: date
    cliente_id: int
    cliente_nombre: str
    cliente_direccion: str
    usuario_id: int
    tipo_mantenimiento: str
    unidad: str
    marca: str
    modelo: str
    observaciones_generales: str | None = None
    fecha_creacion: datetime
    secciones: list[SeccionMantenimientoRespuesta]
    anexos_fotograficos: list[str] = Field(default_factory=list)
    partes_reemplazo: list[ParteReemplazoRespuesta] = Field(default_factory=list)


class SiguienteFolioRespuesta(BaseModel):
    folio: str
