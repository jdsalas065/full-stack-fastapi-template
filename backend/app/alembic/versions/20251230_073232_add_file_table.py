"""add file table

Revision ID: 20251230_073232
Revises: 
Create Date: 2025-12-30 07:32:32.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251230_073232'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create file table."""
    op.create_table(
        'file',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('object_name', sa.String(length=500), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_user_id'), 'file', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop file table."""
    op.drop_index(op.f('ix_file_user_id'), table_name='file')
    op.drop_table('file')
