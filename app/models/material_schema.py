from pydantic import BaseModel, Field


class MaterialCrear(BaseModel):
    nombre: str = Field(..., min_length=1)
    unidad: str = Field(..., min_length=1)
    codigo: str | None = None


class MaterialActualizar(BaseModel):
    nombre: str = Field(..., min_length=1)
    unidad: str = Field(..., min_length=1)
    codigo: str | None = None


class MaterialRespuesta(BaseModel):
    id: int
    nombre: str
    unidad: str
    codigo: str | None
    activo: bool

    class Config:
        from_attributes = True