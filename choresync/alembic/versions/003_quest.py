"""Phase 3: quest, wish tables

Revision ID: 003_quest
Revises: 002_chore
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "003_quest"
down_revision = "002_chore"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "quests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reward_points", sa.Float, nullable=False, server_default="10"),
        sa.Column(
            "status",
            sa.Enum("Open", "Accepted", "PendingConfirm", "Completed", "Cancelled", name="queststatus"),
            nullable=False,
            server_default="Open",
        ),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("accepted_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column("confirmed_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column("deadline", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_quests_family_id", "quests", ["family_id"])

    op.create_table(
        "wishes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("point_cost", sa.Float, nullable=False, server_default="10"),
        sa.Column(
            "status",
            sa.Enum("Pending", "Approved", "Fulfilled", "Cancelled", name="wishstatus"),
            nullable=False,
            server_default="Pending",
        ),
        sa.Column("requested_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("approved_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column("fulfilled_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("fulfilled_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_wishes_family_id", "wishes", ["family_id"])


def downgrade():
    op.drop_index("ix_wishes_family_id", "wishes")
    op.drop_table("wishes")
    op.drop_index("ix_quests_family_id", "quests")
    op.drop_table("quests")
