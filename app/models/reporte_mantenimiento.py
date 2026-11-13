from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ReporteMantenimiento(Base):
    __tablename__ = "reportes_mantenimiento"
    __table_args__ = (
        UniqueConstraint("folio", "es_test", name="uq_reportes_mantenimiento_folio_test"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    folio: Mapped[str] = mapped_column(String(100), nullable=False)

    nombre_documento: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Reporte de Mantenimiento",
    )

    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False,
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    tipo_mantenimiento: Mapped[str] = mapped_column(String(255), nullable=False)

    unidad: Mapped[str] = mapped_column(String(255), nullable=False)

    marca: Mapped[str] = mapped_column(String(255), nullable=False)

    modelo: Mapped[str] = mapped_column(String(255), nullable=False)

    observaciones_generales: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    es_test: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    cliente = relationship("Cliente")

    secciones = relationship(
        "ReporteMantenimientoSeccion",
        back_populates="reporte",
        cascade="all, delete-orphan",
        order_by="ReporteMantenimientoSeccion.orden",
    )

    anexos = relationship(
        "ReporteMantenimientoAnexo",
        back_populates="reporte",
        cascade="all, delete-orphan",
        order_by="ReporteMantenimientoAnexo.orden",
    )

    partes_reemplazo = relationship(
        "ReporteMantenimientoParte",
        back_populates="reporte",
        cascade="all, delete-orphan",
        order_by="ReporteMantenimientoParte.orden",
    )


class ReporteMantenimientoSeccion(Base):
    __tablename__ = "reportes_mantenimiento_secciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reporte_id: Mapped[int] = mapped_column(
        ForeignKey("reportes_mantenimiento.id", ondelete="CASCADE"),
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)

    reporte = relationship("ReporteMantenimiento", back_populates="secciones")

    actividades = relationship(
        "ReporteMantenimientoActividad",
        back_populates="seccion",
        cascade="all, delete-orphan",
        order_by="ReporteMantenimientoActividad.item_numero",
    )


class ReporteMantenimientoActividad(Base):
    __tablename__ = "reportes_mantenimiento_actividades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    seccion_id: Mapped[int] = mapped_column(
        ForeignKey("reportes_mantenimiento_secciones.id", ondelete="CASCADE"),
        nullable=False,
    )

    item_numero: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    actividad: Mapped[str] = mapped_column(Text, nullable=False)

    estado: Mapped[str] = mapped_column(String(100), nullable=False)

    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    seccion = relationship("ReporteMantenimientoSeccion", back_populates="actividades")


class ReporteMantenimientoAnexo(Base):
    __tablename__ = "reportes_mantenimiento_anexos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reporte_id: Mapped[int] = mapped_column(
        ForeignKey("reportes_mantenimiento.id", ondelete="CASCADE"),
        nullable=False,
    )

    ruta_imagen: Mapped[str] = mapped_column(String(500), nullable=False)

    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    reporte = relationship("ReporteMantenimiento", back_populates="anexos")


class ReporteMantenimientoParte(Base):
    __tablename__ = "reportes_mantenimiento_partes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reporte_id: Mapped[int] = mapped_column(
        ForeignKey("reportes_mantenimiento.id", ondelete="CASCADE"),
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    reporte = relationship("ReporteMantenimiento", back_populates="partes_reemplazo")

    imagenes = relationship(
        "ReporteMantenimientoParteImagen",
        back_populates="parte",
        cascade="all, delete-orphan",
        order_by="ReporteMantenimientoParteImagen.orden",
    )


class ReporteMantenimientoParteImagen(Base):
    __tablename__ = "reportes_mantenimiento_parte_imagenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    parte_id: Mapped[int] = mapped_column(
        ForeignKey("reportes_mantenimiento_partes.id", ondelete="CASCADE"),
        nullable=False,
    )

    ruta_imagen: Mapped[str] = mapped_column(String(500), nullable=False)

    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    parte = relationship("ReporteMantenimientoParte", back_populates="imagenes")
