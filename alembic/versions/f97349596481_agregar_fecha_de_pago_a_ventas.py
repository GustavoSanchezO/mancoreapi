"""agregar fecha de pago a ventas

Revision ID: f97349596481
Revises: cf7ed5a79eb4
Create Date: 2026-09-11 19:19:58.954574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f97349596481'
down_revision: Union[str, Sequence[str], None] = 'cf7ed5a79eb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'ventas',
        sa.Column(
            'fecha_pago',
            sa.Date(),
            nullable=True
        )
    )

    op.execute(
        "UPDATE ventas SET fecha_pago = fecha"
    )

    op.alter_column(
        'ventas',
        'fecha_pago',
        nullable=False
    )


def downgrade() -> None:
    op.drop_column(
        'ventas',
        'fecha_pago'
    )