"""Add assigned_to to chore_templates

Revision ID: 008
Revises: 007
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite batch mode doesn't support FK constraints easily — use plain Integer
    with op.batch_alter_table('chore_templates') as b:
        b.add_column(sa.Column('assigned_to', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('chore_templates') as b:
        b.drop_column('assigned_to')
