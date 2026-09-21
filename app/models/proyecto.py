from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from sqlalchemy.orm import relationship
from typing import List


class Proyecto(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    estado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="COTIZACION"
    )

    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        secondary="usuario_proyecto",
        back_populates="proyectos"
    )