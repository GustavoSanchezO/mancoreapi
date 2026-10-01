"""add nombre_archivo to cotizaciones

Revision ID: b7d2d1a7c9df
Revises: a2847d08dbec
Create Date: 2026-09-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used as Alembic revision ids.
revision: str = 'b7d2d1a7c9df'
down_revision: Union[str, Sequence[str], None] = 'a2847d08dbec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'cotizaciones',
        sa.Column('nombre_archivo', sa.String(length=255), nullable=True)
    )
    op.execute(
        sa.text(
            """
            UPDATE cotizaciones
            SET nombre_archivo = 'RFQ REQ ' || rfq
            WHERE nombre_archivo IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_column('cotizaciones', 'nombre_archivo')
