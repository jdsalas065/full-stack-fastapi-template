"""add submission and submission_document tables

Revision ID: 20260107_092100
Revises: 20260106_070400
Create Date: 2026-01-07 09:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260107_092100'
down_revision: Union[str, None] = '20260106_070400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add submission and submission_document tables."""
    
    # Create submission table
    op.create_table(
        'submission',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submission_user_id'), 'submission', ['user_id'], unique=False)
    op.create_index(op.f('ix_submission_task_id'), 'submission', ['task_id'], unique=True)
    
    # Create submission_document table
    op.create_table(
        'submissiondocument',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('submission_id', sa.String(length=255), nullable=False),
        sa.Column('file_id', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['submission.id'], ),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissiondocument_submission_id'), 'submissiondocument', ['submission_id'], unique=False)
    op.create_index(op.f('ix_submissiondocument_file_id'), 'submissiondocument', ['file_id'], unique=False)


def downgrade() -> None:
    """Remove submission and submission_document tables."""
    
    # Drop submission_document table
    op.drop_index(op.f('ix_submissiondocument_file_id'), table_name='submissiondocument')
    op.drop_index(op.f('ix_submissiondocument_submission_id'), table_name='submissiondocument')
    op.drop_table('submissiondocument')
    
    # Drop submission table
    op.drop_index(op.f('ix_submission_task_id'), table_name='submission')
    op.drop_index(op.f('ix_submission_user_id'), table_name='submission')
    op.drop_table('submission')
