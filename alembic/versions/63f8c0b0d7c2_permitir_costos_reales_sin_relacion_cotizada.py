"""permitir costos reales sin relacion cotizada

Revision ID: 63f8c0b0d7c2
Revises: c30d8a14bbf1
Create Date: 2026-10-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "63f8c0b0d7c2"
down_revision: Union[str, Sequence[str], None] = "c30d8a14bbf1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "costos_materiales_reales",
        "material_cotizacion_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "costos_mano_obra_reales",
        "mano_obra_cotizada_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "costos_gastos_extra_reales",
        "gasto_extra_cotizado_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "costos_materiales_reales",
        "material_cotizacion_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "costos_mano_obra_reales",
        "mano_obra_cotizada_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "costos_gastos_extra_reales",
        "gasto_extra_cotizado_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
