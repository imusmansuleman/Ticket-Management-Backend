"""add indexes

Revision ID: dfe848cce6d5
Revises: 42dcaba1c8e0
Create Date: 2026-10-03 00:27:46.529487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfe848cce6d5'
down_revision: Union[str, Sequence[str], None] = '42dcaba1c8e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_tickets_created_by_id",
        "tickets",
        ["created_by_id"]
    )

    op.create_index(
        "ix_tickets_assignee_id",
        "tickets",
        ["assignee_id"]
    )

    op.create_index(
        "ix_comments_ticket_id",
        "comments",
        ["ticket_id"]
    )

    op.create_index(
        "ix_comments_author_id",
        "comments",
        ["author_id"]
    )

    op.create_index(
        "ix_comment_reactions_comment_id",
        "comment_reactions",
        ["comment_id"]
    )

    op.create_index(
        "ix_comment_reactions_user_id",
        "comment_reactions",
        ["user_id"]
    )

    op.create_index(
        "ix_ticket_history_ticket_id",
        "ticket_history",
        ["ticket_id"]
    )

    op.create_index(
        "ix_ticket_history_changed_by_id",
        "ticket_history",
        ["changed_by_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ticket_history_changed_by_id",
        table_name="ticket_history"
    )

    op.drop_index(
        "ix_ticket_history_ticket_id",
        table_name="ticket_history"
    )

    op.drop_index(
        "ix_comment_reactions_user_id",
        table_name="comment_reactions"
    )

    op.drop_index(
        "ix_comment_reactions_comment_id",
        table_name="comment_reactions"
    )

    op.drop_index(
        "ix_comments_author_id",
        table_name="comments"
    )

    op.drop_index(
        "ix_comments_ticket_id",
        table_name="comments"
    )

    op.drop_index(
        "ix_tickets_assignee_id",
        table_name="tickets"
    )

    op.drop_index(
        "ix_tickets_created_by_id",
        table_name="tickets"
    )