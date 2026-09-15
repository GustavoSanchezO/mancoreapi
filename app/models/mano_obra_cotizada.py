from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ManoObraCotizada(Base):
    __tablename__ = "mano_obra_cotizada"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    partida_id: Mapped[int] = mapped_column(
        ForeignKey("partidas_cotizacion.id"),
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