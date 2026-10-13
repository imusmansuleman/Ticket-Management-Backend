"""add manager to user role enum

Revision ID: 9314eb30bf46
Revises: 7ab6d3438c22
Create Date: 2026-10-02 05:43:41.573002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9314eb30bf46'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
        op.execute(
        "ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'manager'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
