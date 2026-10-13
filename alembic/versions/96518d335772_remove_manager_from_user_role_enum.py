"""remove manager from user role enum

Revision ID: 96518d335772
Revises: 93e00dbe82ba
Create Date: 2026-10-06 18:40:47.334258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96518d335772'
down_revision: Union[str, Sequence[str], None] = '93e00dbe82ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the existing enum
    op.execute(
        "ALTER TYPE user_role RENAME TO user_role_old"
    )

    # Create the new enum without manager
    op.execute(
        "CREATE TYPE user_role AS ENUM "
        "('admin', 'engineer', 'employee')"
    )

    # Convert users.role from the old enum to the new enum
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE user_role
        USING role::text::user_role
        """
    )

    # Old enum is no longer needed
    op.execute(
        "DROP TYPE user_role_old"
    )


def upgrade() -> None:
    # Rename the existing enum
    op.execute(
        "ALTER TYPE user_role RENAME TO user_role_old"
    )

    # Create the new enum without manager
    op.execute(
        "CREATE TYPE user_role AS ENUM "
        "('admin', 'engineer', 'employee')"
    )

    # Convert users.role from the old enum to the new enum
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE user_role
        USING role::text::user_role
        """
    )

    # Old enum is no longer needed
    op.execute(
        "DROP TYPE user_role_old"
    )
