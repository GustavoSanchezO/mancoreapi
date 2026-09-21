from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CotizacionDB(Base):
    __tablename__ = "cotizaciones"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    rfq: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False
    )

    proyecto_id: Mapped[int] = mapped_column(
        ForeignKey("proyectos.id"),
        nullable=False
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False
    )

    tiempo_entrega_estimado: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="COTIZACION"
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

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    es_test: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    nota_importante_id: Mapped[int] = mapped_column(
        ForeignKey("notas_importantes.id"),
        nullable=True
    )

    nota_importante_texto: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    anexos = relationship(
        "AnexoFotografico",
        back_populates="cotizacion",
        cascade="all, delete-orphan"
    )