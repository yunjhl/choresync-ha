"""Add recurrence, photo_url, marketplace

Revision ID: 005
Revises: 004_iot
Create Date: 2026-04-12
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004_iot'
branch_labels = None
depends_on = None

def upgrade():
    # ChoreTemplate에 recurrence 필드 추가
    with op.batch_alter_table('chore_templates') as batch_op:
        batch_op.add_column(sa.Column('recurrence_interval', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('recurrence_day', sa.Integer(), nullable=True))

    # ChoreTask에 photo_url 추가
    with op.batch_alter_table('chore_tasks') as batch_op:
        batch_op.add_column(sa.Column('photo_url', sa.String(500), nullable=True))

    # marketplace_templates 테이블 생성
    op.create_table(
        'marketplace_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='기타'),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('intensity', sa.String(10), nullable=False, server_default='Normal'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('submitted_by_family_id', sa.Integer(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('import_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

def downgrade():
    op.drop_table('marketplace_templates')
    with op.batch_alter_table('chore_tasks') as batch_op:
        batch_op.drop_column('photo_url')
    with op.batch_alter_table('chore_templates') as batch_op:
        batch_op.drop_column('recurrence_day')
        batch_op.drop_column('recurrence_interval')
