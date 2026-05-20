"""add bounty submissions

Revision ID: a1b2c3d4e5f6
Revises: 2aaee88b9760
Create Date: 2026-05-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "2aaee88b9760"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bounty_submissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("bounty_id", sa.UUID(), nullable=False),
        sa.Column("submitter_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("media_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["bounty_id"], ["bounties.id"]),
        sa.ForeignKeyConstraint(["submitter_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bounty_id", "submitter_id", name="uq_bounty_submitter"),
    )
    op.create_index(op.f("ix_bounty_submissions_bounty_id"), "bounty_submissions", ["bounty_id"], unique=False)
    op.create_index(op.f("ix_bounty_submissions_submitter_id"), "bounty_submissions", ["submitter_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bounty_submissions_submitter_id"), table_name="bounty_submissions")
    op.drop_index(op.f("ix_bounty_submissions_bounty_id"), table_name="bounty_submissions")
    op.drop_table("bounty_submissions")
