"""Phase 10-3: WeeklyReport 테이블 추가"""

from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "weekly_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False, index=True),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False, default=0),
        sa.Column("total_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("achievement_pct", sa.Integer(), nullable=False, default=0),
        sa.Column("mvp_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("weekly_reports")
