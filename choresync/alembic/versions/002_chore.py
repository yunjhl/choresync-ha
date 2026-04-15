"""Phase 2: chore tables

Revision ID: 002_chore
Revises: 001_init
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "002_chore"
down_revision = "001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chore_templates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="기타"),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column(
            "intensity",
            sa.Enum("Light", "Normal", "Hard", name="intensitylevel"),
            nullable=False,
            server_default="Normal",
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_chore_templates_family_id", "chore_templates", ["family_id"])

    op.create_table(
        "chore_tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("template_id", sa.Integer, sa.ForeignKey("chore_templates.id"), nullable=True),
        sa.Column("assigned_to", sa.Integer, sa.ForeignKey("family_members.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="기타"),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column(
            "intensity",
            sa.Enum("Light", "Normal", "Hard", name="intensitylevel"),
            nullable=False,
            server_default="Normal",
        ),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column(
            "status",
            sa.Enum("Pending", "Completed", "Skipped", name="taskstatus"),
            nullable=False,
            server_default="Pending",
        ),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_chore_tasks_family_id", "chore_tasks", ["family_id"])

    op.create_table(
        "completion_history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("task_id", sa.Integer, sa.ForeignKey("chore_tasks.id"), nullable=False),
        sa.Column("completed_by", sa.Integer, sa.ForeignKey("family_members.id"), nullable=False),
        sa.Column("score_earned", sa.Float, nullable=False),
        sa.Column("completed_at", sa.DateTime, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
    )
    op.create_index("ix_completion_history_task_id", "completion_history", ["task_id"])


def downgrade():
    op.drop_index("ix_completion_history_task_id", "completion_history")
    op.drop_table("completion_history")
    op.drop_index("ix_chore_tasks_family_id", "chore_tasks")
    op.drop_table("chore_tasks")
    op.drop_index("ix_chore_templates_family_id", "chore_templates")
    op.drop_table("chore_templates")
