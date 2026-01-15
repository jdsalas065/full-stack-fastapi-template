"""add unique constraint for submission name per user

Revision ID: 20260115_060010
Revises: 20260107_093800
Create Date: 2026-01-15 06:00:10.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20260115_060010'
down_revision: Union[str, None] = '20260107_093800'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on (name, owner_id) for submission table."""
    op.create_unique_constraint(
        'uq_submission_name_owner',
        'submission',
        ['name', 'owner_id']
    )


def downgrade() -> None:
    """Remove unique constraint on (name, owner_id) for submission table."""
    op.drop_constraint('uq_submission_name_owner', 'submission', type_='unique')
