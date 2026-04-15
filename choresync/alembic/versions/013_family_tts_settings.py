"""add family tts settings

Revision ID: 013_family_tts_settings
Revises: 012_invited_email
Create Date: 2026-04-15
"""
from alembic import op
import sqlalchemy as sa

revision = "013_family_tts_settings"
down_revision = "012_invited_email"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("families") as batch_op:
        batch_op.add_column(sa.Column("tts_player", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("tts_engine", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("briefing_hour", sa.Integer(), nullable=False, server_default="7"))
        batch_op.add_column(sa.Column("briefing_enabled", sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    with op.batch_alter_table("families") as batch_op:
        batch_op.drop_column("briefing_enabled")
        batch_op.drop_column("briefing_hour")
        batch_op.drop_column("tts_engine")
        batch_op.drop_column("tts_player")
