"""add task_id to file table

Revision ID: 20260106_070400
Revises: 20251230_073232
Create Date: 2026-01-06 07:04:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260106_070400'
down_revision: Union[str, None] = '20251230_073232'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add task_id column to file table."""
    op.add_column('file', sa.Column('task_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_file_task_id'), 'file', ['task_id'], unique=False)


def downgrade() -> None:
    """Remove task_id column from file table."""
    op.drop_index(op.f('ix_file_task_id'), table_name='file')
    op.drop_column('file', 'task_id')
