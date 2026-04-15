"""Phase 7: users.language + chore_tasks.photo_required + completion_history.photo_path

Revision ID: 011
Revises: 010
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as b:
        b.add_column(sa.Column("language", sa.String(8), nullable=False, server_default="ko"))

    with op.batch_alter_table("chore_tasks") as b:
        b.add_column(sa.Column("photo_required", sa.Boolean(), nullable=False, server_default="0"))

    with op.batch_alter_table("completion_history") as b:
        b.add_column(sa.Column("photo_path", sa.String(512), nullable=True))


def downgrade():
    with op.batch_alter_table("completion_history") as b:
        b.drop_column("photo_path")
    with op.batch_alter_table("chore_tasks") as b:
        b.drop_column("photo_required")
    with op.batch_alter_table("users") as b:
        b.drop_column("language")
