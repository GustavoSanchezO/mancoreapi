from pydantic import BaseModel, Field


class ClienteCrear(BaseModel):
    nombre_empresa: str = Field(..., min_length=1)
    direccion: str = Field(..., min_length=1)


class ClienteActualizar(BaseModel):
    nombre_empresa: str | None = Field(
        default=None,
        min_length=1
    )
    direccion: str | None = Field(
        default=None,
        min_length=1
    )


class ClienteRespuesta(BaseModel):
    id: int
    nombre_empresa: str
    direccion: str
    activo: bool

    class Config:
        from_attributes = True