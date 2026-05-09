"""add hnsw index

Revision ID: d238b772c6f9
Revises: c3822e85e68e
Create Date: 2026-05-09 12:12:57.840004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd238b772c6f9'
down_revision: Union[str, Sequence[str], None] = 'c3822e85e68e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE INDEX IF NOT EXISTS ix_media_items_embedding_hnsw ON media_items USING hnsw (embedding vector_cosine_ops);")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_media_items_embedding_hnsw;")
    pass
