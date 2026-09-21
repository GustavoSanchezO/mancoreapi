from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class NotaImportante(Base):
    __tablename__ = "notas_importantes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    es_test: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
