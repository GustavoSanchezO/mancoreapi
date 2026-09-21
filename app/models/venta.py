from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    cotizacion_id: Mapped[int] = mapped_column(
        ForeignKey("cotizaciones.id"),
        unique=True,
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    iva: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDIENTE"
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    fecha_pago: Mapped[date] = mapped_column(
    Date,
    nullable=False
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