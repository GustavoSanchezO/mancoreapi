from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    nombre_empresa: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    direccion: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )