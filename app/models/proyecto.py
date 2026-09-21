from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario



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

    usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    es_test: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        secondary="usuario_proyecto",
        back_populates="proyectos"
    )