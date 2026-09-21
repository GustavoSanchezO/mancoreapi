from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from sqlalchemy.orm import relationship
from typing import List


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    rol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="EMPLEADO"
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    ultimo_acceso: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    proyectos: Mapped[List["Proyecto"]] = relationship(
        "Proyecto",
        secondary="usuario_proyecto",
        back_populates="usuarios"
    )