"""Add age_min, age_max, assignee_type to marketplace and chore templates

Revision ID: 009
Revises: 008
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('marketplace_templates') as b:
        b.add_column(sa.Column('age_min', sa.Integer(), nullable=True))
        b.add_column(sa.Column('age_max', sa.Integer(), nullable=True))
        b.add_column(sa.Column('assignee_type', sa.String(20), nullable=True))

    with op.batch_alter_table('chore_templates') as b:
        b.add_column(sa.Column('age_min', sa.Integer(), nullable=True))
        b.add_column(sa.Column('age_max', sa.Integer(), nullable=True))
        b.add_column(sa.Column('assignee_type', sa.String(20), nullable=True))


def downgrade():
    with op.batch_alter_table('marketplace_templates') as b:
        b.drop_column('assignee_type')
        b.drop_column('age_max')
        b.drop_column('age_min')

    with op.batch_alter_table('chore_templates') as b:
        b.drop_column('assignee_type')
        b.drop_column('age_max')
        b.drop_column('age_min')
