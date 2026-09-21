from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CodigoInvitacion(Base):
    __tablename__ = "codigos_invitacion"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    codigo: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    usado: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    creado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    fecha_uso: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )