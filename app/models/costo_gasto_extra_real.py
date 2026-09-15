from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CostoGastoExtraReal(Base):
    __tablename__ = "costos_gastos_extra_reales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    venta_id: Mapped[int] = mapped_column(
        ForeignKey("ventas.id"),
        nullable=False
    )

    gasto_extra_cotizado_id: Mapped[int] = mapped_column(
        ForeignKey("gastos_extra_cotizados.id"),
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )