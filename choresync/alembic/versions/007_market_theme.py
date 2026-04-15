"""Add family_size, recurrence, trigger_context fields

Revision ID: 007
Revises: 006
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # marketplace_templates: family_size, recurrence, trigger_context 추가
    with op.batch_alter_table('marketplace_templates') as b:
        b.add_column(sa.Column('family_size', sa.String(10), server_default='전체', nullable=False))
        b.add_column(sa.Column('recurrence_interval', sa.String(20), nullable=True))
        b.add_column(sa.Column('recurrence_day', sa.Integer(), nullable=True))
        b.add_column(sa.Column('trigger_context', sa.String(20), nullable=True))

    # chore_templates: trigger_context 추가
    with op.batch_alter_table('chore_templates') as b:
        b.add_column(sa.Column('trigger_context', sa.String(20), nullable=True))


def downgrade():
    with op.batch_alter_table('marketplace_templates') as b:
        b.drop_column('trigger_context')
        b.drop_column('recurrence_day')
        b.drop_column('recurrence_interval')
        b.drop_column('family_size')
    with op.batch_alter_table('chore_templates') as b:
        b.drop_column('trigger_context')
