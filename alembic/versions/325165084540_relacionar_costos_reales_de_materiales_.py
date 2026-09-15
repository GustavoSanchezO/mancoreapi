"""relacionar costos reales de materiales con ventas

Revision ID: 325165084540
Revises: f97349596481
Create Date: 2026-09-11 19:43:10.496163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '325165084540'
down_revision: Union[str, Sequence[str], None] = 'f97349596481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'costos_materiales_reales',
        sa.Column(
            'venta_id',
            sa.Integer(),
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_column(
        'costos_materiales_reales',
        'venta_id'
    )