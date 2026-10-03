"""agregar costos reales cero a ventas

Revision ID: c30d8a14bbf1
Revises: f97349596481
Create Date: 2026-10-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c30d8a14bbf1"
down_revision: Union[str, Sequence[str], None] = "b7d2d1a7c9df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO costos_materiales_reales (
            venta_id,
            material_cotizacion_id,
            descripcion,
            cantidad,
            precio_unitario,
            total,
            fecha
        )
        SELECT
            v.id,
            mc.id,
            mc.descripcion,
            0.00,
            0.00,
            0.00,
            v.fecha
        FROM ventas v
        JOIN cotizaciones c ON c.id = v.cotizacion_id
        JOIN partidas_cotizacion p ON p.cotizacion_id = c.id
        JOIN materiales_cotizacion mc ON mc.partida_id = p.id
        WHERE NOT EXISTS (
            SELECT 1
            FROM costos_materiales_reales cmr
            WHERE cmr.venta_id = v.id
              AND cmr.material_cotizacion_id = mc.id
        )
        """
    )

    op.execute(
        """
        INSERT INTO costos_mano_obra_reales (
            venta_id,
            mano_obra_cotizada_id,
            descripcion,
            cantidad,
            precio_unitario,
            total,
            fecha
        )
        SELECT
            v.id,
            moc.id,
            moc.descripcion,
            0.00,
            0.00,
            0.00,
            v.fecha
        FROM ventas v
        JOIN cotizaciones c ON c.id = v.cotizacion_id
        JOIN partidas_cotizacion p ON p.cotizacion_id = c.id
        JOIN mano_obra_cotizada moc ON moc.partida_id = p.id
        WHERE NOT EXISTS (
            SELECT 1
            FROM costos_mano_obra_reales cmor
            WHERE cmor.venta_id = v.id
              AND cmor.mano_obra_cotizada_id = moc.id
        )
        """
    )

    op.execute(
        """
        INSERT INTO costos_gastos_extra_reales (
            venta_id,
            gasto_extra_cotizado_id,
            descripcion,
            cantidad,
            precio_unitario,
            total,
            fecha
        )
        SELECT
            v.id,
            gec.id,
            gec.descripcion,
            0.00,
            0.00,
            0.00,
            v.fecha
        FROM ventas v
        JOIN cotizaciones c ON c.id = v.cotizacion_id
        JOIN partidas_cotizacion p ON p.cotizacion_id = c.id
        JOIN gastos_extra_cotizados gec ON gec.partida_id = p.id
        WHERE NOT EXISTS (
            SELECT 1
            FROM costos_gastos_extra_reales cger
            WHERE cger.venta_id = v.id
              AND cger.gasto_extra_cotizado_id = gec.id
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM costos_materiales_reales
        WHERE cantidad = 0.00
          AND precio_unitario = 0.00
          AND total = 0.00
        """
    )

    op.execute(
        """
        DELETE FROM costos_mano_obra_reales
        WHERE cantidad = 0.00
          AND precio_unitario = 0.00
          AND total = 0.00
        """
    )

    op.execute(
        """
        DELETE FROM costos_gastos_extra_reales
        WHERE cantidad = 0.00
          AND precio_unitario = 0.00
          AND total = 0.00
        """
    )
