from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ImpuestoMensual(Base):
    __tablename__ = "impuestos_mensuales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    año: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    mes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total_impuestos: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "año",
            "mes",
            name="uq_impuestos_mensuales_año_mes"
        ),
    )