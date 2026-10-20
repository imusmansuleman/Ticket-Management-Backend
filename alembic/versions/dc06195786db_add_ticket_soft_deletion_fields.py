"""add ticket soft deletion fields

Revision ID: dc06195786db
Revises: 96518d335772
Create Date: 2026-10-19 19:23:11.229816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc06195786db'
down_revision: Union[str, Sequence[str], None] = '96518d335772'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'tickets',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False
        )
    )

    op.add_column(
        'tickets',
        sa.Column(
            'deleted_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        'tickets',
        sa.Column(
            'deleted_by_id',
            sa.BigInteger(),
            nullable=True
        )
    )

    op.create_foreign_key(
        'fk_tickets_deleted_by_id',
        'tickets',
        'users',
        ['deleted_by_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_tickets_deleted_by_id',
        'tickets',
        type_='foreignkey'
    )

    op.drop_column('tickets', 'deleted_by_id')
    op.drop_column('tickets', 'deleted_at')
    op.drop_column('tickets', 'is_deleted')
