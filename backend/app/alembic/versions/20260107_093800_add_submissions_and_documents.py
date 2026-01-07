"""add submissions and documents tables

Revision ID: 20260107_093800
Revises: 20260106_070400
Create Date: 2026-01-07 09:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260107_093800'
down_revision: Union[str, None] = '20260106_070400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create submission and submission_document tables."""
    # Create submission table
    op.create_table(
        'submission',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('pic', sa.String(length=255), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submission_owner_id'), 'submission', ['owner_id'], unique=False)

    # Create submission_document table
    op.create_table(
        'submission_document',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('submission_id', sa.Uuid(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['submission.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submission_document_submission_id'), 'submission_document', ['submission_id'], unique=False)


def downgrade() -> None:
    """Drop submission and submission_document tables."""
    op.drop_index(op.f('ix_submission_document_submission_id'), table_name='submission_document')
    op.drop_table('submission_document')
    op.drop_index(op.f('ix_submission_owner_id'), table_name='submission')
    op.drop_table('submission')
