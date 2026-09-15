from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class Cliente(BaseModel):
    nombre_empresa: str = Field(..., min_length=1)
    direccion: str = Field(..., min_length=1)


class Partida(BaseModel):
    descripcion: str = Field(..., min_length=1)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)


class Proyecto(BaseModel):
    nombre: str = Field(..., min_length=1)
    descripcion_corta: str = Field(..., min_length=1)


# Aquí metemos el modelo final de la cotización,
# que es el que vamos a usar en la ruta /generar/cotizacion
class Cotizacion(BaseModel):
    rfq: str = Field(..., min_length=1)
    fecha: date
    tiempo_entrega_estimado: str = Field(..., min_length=1)

    cliente: Cliente
    proyecto: Proyecto
    partidas: list[Partida]