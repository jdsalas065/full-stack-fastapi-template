"""add chat conversation and message tables

Revision ID: 20260322_120000
Revises: 20260115_060010
Create Date: 2026-03-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260322_120000"
down_revision: Union[str, None] = "20260115_060010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat conversation and message tables."""
    op.create_table(
        "chat_conversation",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_conversation_owner_id"),
        "chat_conversation",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "chat_message",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chat_message_conversation_id"),
        "chat_message",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_message_role"),
        "chat_message",
        ["role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_message_status"),
        "chat_message",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Drop chat conversation and message tables."""
    op.drop_index(op.f("ix_chat_message_status"), table_name="chat_message")
    op.drop_index(op.f("ix_chat_message_role"), table_name="chat_message")
    op.drop_index(op.f("ix_chat_message_conversation_id"), table_name="chat_message")
    op.drop_table("chat_message")

    op.drop_index(
        op.f("ix_chat_conversation_owner_id"),
        table_name="chat_conversation",
    )
    op.drop_table("chat_conversation")
