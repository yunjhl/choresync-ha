"""Phase 9-1: ChoreTask 위임 컬럼 추가"""

from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013_family_tts_settings"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    existing = [row[1] for row in conn.execute(sa.text("PRAGMA table_info(chore_tasks)")).fetchall()]
    if "delegated_to" not in existing:
        op.add_column("chore_tasks", sa.Column("delegated_to", sa.Integer(), sa.ForeignKey("family_members.id"), nullable=True))
    if "delegation_note" not in existing:
        op.add_column("chore_tasks", sa.Column("delegation_note", sa.Text(), nullable=True))
    if "delegation_status" not in existing:
        op.add_column("chore_tasks", sa.Column("delegation_status", sa.String(20), nullable=True))


def downgrade():
    op.drop_column("chore_tasks", "delegation_status")
    op.drop_column("chore_tasks", "delegation_note")
    op.drop_column("chore_tasks", "delegated_to")
