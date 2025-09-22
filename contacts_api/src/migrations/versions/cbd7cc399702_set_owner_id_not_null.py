"""set owner_id not null

Revision ID: cbd7cc399702
Revises: 8e02657bcf3f
Create Date: 2025-09-21 22:33:59.033005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbd7cc399702'
down_revision: Union[str, Sequence[str], None] = '8e02657bcf3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
