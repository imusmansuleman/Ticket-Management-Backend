"""convert ticket category to enum

Revision ID: 93e00dbe82ba
Revises: dfe848cce6d5
Create Date: 2026-10-06 02:21:17.499526

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93e00dbe82ba'
down_revision: Union[str, Sequence[str], None] = 'dfe848cce6d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ticket_category = postgresql.ENUM(
        "hardware",
        "software",
        "network",
        "access",
        "other",
        name="ticket_category"
    )

    ticket_category.create(
        op.get_bind(),
        checkfirst=True
    )

    op.drop_constraint(
        "tickets_category_id_fkey",
        "tickets",
        type_="foreignkey"
    )

    op.drop_column(
        "tickets",
        "category_id"
    )

    op.add_column(
        "tickets",
        sa.Column(
            "category",
            ticket_category,
            nullable=False
        )
    )

    op.drop_table("categories")


def downgrade() -> None:
    # Remove the enum-backed category column
    op.drop_column(
        "tickets",
        "category"
    )

    # Recreate the categories lookup table
    op.create_table(
        "categories",
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
            unique=True
        )
    )

    # Recreate category_id on tickets
    op.add_column(
        "tickets",
        sa.Column(
            "category_id",
            sa.BigInteger(),
            nullable=False
        )
    )

    # Recreate the foreign key
    op.create_foreign_key(
        "tickets_category_id_fkey",
        "tickets",
        "categories",
        ["category_id"],
        ["id"]
    )

    # Remove the PostgreSQL enum type
    ticket_category = postgresql.ENUM(
        "hardware",
        "software",
        "network",
        "access",
        "other",
        name="ticket_category"
    )

    ticket_category.drop(
        op.get_bind(),
        checkfirst=True
    )