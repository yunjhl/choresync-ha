"""add invited_email to invitations

Revision ID: 012_invited_email
Revises: 011_phase7_i18n_photo
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = "012_invited_email"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.add_column(sa.Column("invited_email", sa.String(255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.drop_column("invited_email")
