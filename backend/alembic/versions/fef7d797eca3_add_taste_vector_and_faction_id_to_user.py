"""add taste_vector and faction_id to user

Revision ID: fef7d797eca3
Revises: 1c86d0497009
Create Date: 2026-05-09 14:03:22.684122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'fef7d797eca3'
down_revision: Union[str, Sequence[str], None] = '1c86d0497009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('taste_vector', pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True))
    op.add_column('users', sa.Column('faction_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'faction_id')
    op.drop_column('users', 'taste_vector')
