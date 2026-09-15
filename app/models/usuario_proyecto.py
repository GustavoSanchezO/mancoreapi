from sqlalchemy import Column, ForeignKey, Table
from app.database.base import Base

usuario_proyecto = Table(
    "usuario_proyecto",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id"), primary_key=True),
    Column("proyecto_id", ForeignKey("proyectos.id"), primary_key=True)
)
