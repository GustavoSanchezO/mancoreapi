from pydantic import BaseModel, Field


class ProyectoCrear(BaseModel):
    nombre: str = Field(..., min_length=1)
    descripcion: str = Field(..., min_length=1)
    cliente_id: int = Field(..., gt=0)


class ProyectoActualizar(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1
    )
    descripcion: str | None = Field(
        default=None,
        min_length=1
    )
    cliente_id: int | None = Field(
        default=None,
        gt=0
    )


class ProyectoRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: str
    cliente_id: int
    estado: str

    class Config:
        from_attributes = True