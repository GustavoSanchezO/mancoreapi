"""crear tablas reportes mantenimiento

Revision ID: 8f3c9b2e1a40
Revises: 63f8c0b0d7c2
Create Date: 2026-11-12 16:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f3c9b2e1a40"
down_revision: Union[str, Sequence[str], None] = "63f8c0b0d7c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reportes_mantenimiento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("folio", sa.String(length=100), nullable=False),
        sa.Column("nombre_documento", sa.String(length=255), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("tipo_mantenimiento", sa.String(length=255), nullable=False),
        sa.Column("unidad", sa.String(length=255), nullable=False),
        sa.Column("marca", sa.String(length=255), nullable=False),
        sa.Column("modelo", sa.String(length=255), nullable=False),
        sa.Column("observaciones_generales", sa.Text(), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("es_test", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("folio", "es_test", name="uq_reportes_mantenimiento_folio_test"),
    )

    op.create_table(
        "reportes_mantenimiento_secciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporte_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["reporte_id"], ["reportes_mantenimiento.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reportes_mantenimiento_actividades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seccion_id", sa.Integer(), nullable=False),
        sa.Column("item_numero", sa.Integer(), nullable=False),
        sa.Column("actividad", sa.Text(), nullable=False),
        sa.Column("estado", sa.String(length=100), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["seccion_id"], ["reportes_mantenimiento_secciones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reportes_mantenimiento_anexos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporte_id", sa.Integer(), nullable=False),
        sa.Column("ruta_imagen", sa.String(length=500), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["reporte_id"], ["reportes_mantenimiento.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reportes_mantenimiento_partes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporte_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["reporte_id"], ["reportes_mantenimiento.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reportes_mantenimiento_parte_imagenes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parte_id", sa.Integer(), nullable=False),
        sa.Column("ruta_imagen", sa.String(length=500), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["parte_id"], ["reportes_mantenimiento_partes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reportes_mantenimiento_parte_imagenes")
    op.drop_table("reportes_mantenimiento_partes")
    op.drop_table("reportes_mantenimiento_anexos")
    op.drop_table("reportes_mantenimiento_actividades")
    op.drop_table("reportes_mantenimiento_secciones")
    op.drop_table("reportes_mantenimiento")
