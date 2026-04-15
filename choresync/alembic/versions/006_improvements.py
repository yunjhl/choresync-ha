"""Add is_marketplace, ha_entity_id, wish_votes

Revision ID: 006
Revises: 005
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade():
    # chore_templates: is_marketplace, ha_entity_id 추가
    with op.batch_alter_table('chore_templates') as batch_op:
        batch_op.add_column(sa.Column('is_marketplace', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('ha_entity_id', sa.String(200), nullable=True))

    # wish_votes 테이블 생성
    op.create_table(
        'wish_votes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('wish_id', sa.Integer(), sa.ForeignKey('wishes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('family_members.id', ondelete='CASCADE'), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('voted_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('wish_id', 'member_id', name='uq_wish_vote_member'),
    )

def downgrade():
    op.drop_table('wish_votes')
    with op.batch_alter_table('chore_templates') as batch_op:
        batch_op.drop_column('ha_entity_id')
        batch_op.drop_column('is_marketplace')
