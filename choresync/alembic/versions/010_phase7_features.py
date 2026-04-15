"""Phase 7: 달력 컬럼 + 배지/업적 + 포인트상점 + 통계캐시 + 대시보드레이아웃

Revision ID: 010
Revises: 009
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade():
    # 1. chore_tasks 에 달력 컬럼 추가
    with op.batch_alter_table("chore_tasks") as b:
        b.add_column(sa.Column("color_tag", sa.String(16), nullable=True))
        b.add_column(sa.Column("calendar_visibility", sa.Boolean(), nullable=False, server_default="1"))

    # 2. badge_definitions
    op.create_table(
        "badge_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(64), nullable=False, server_default="🏆"),
        sa.Column("badge_type", sa.String(32), nullable=False),
        sa.Column("condition_json", sa.Text(), nullable=False),
        sa.Column("tier", sa.String(16), nullable=False, server_default="bronze"),
        sa.Column("points_bonus", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # 3. earned_badges
    op.create_table(
        "earned_badges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("badge_definition_id", sa.Integer(), sa.ForeignKey("badge_definitions.id"), nullable=False),
        sa.Column("earned_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("context_json", sa.Text(), nullable=True),
        sa.Column("notified", sa.Boolean(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "badge_definition_id", name="uq_user_badge"),
    )
    op.create_index("ix_earned_badges_user_family", "earned_badges", ["user_id", "family_id"])

    # 4. user_streaks
    op.create_table(
        "user_streaks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_completion_date", sa.Date(), nullable=True),
        sa.Column("streak_start_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "family_id", name="uq_user_family_streak"),
    )

    # 5. reward_items
    op.create_table(
        "reward_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(64), nullable=False, server_default="🎁"),
        sa.Column("point_cost", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="-1"),
        sa.Column("max_per_user", sa.Integer(), nullable=False, server_default="-1"),
        sa.Column("category", sa.String(32), nullable=False, server_default="general"),
        sa.Column("linked_wish_id", sa.Integer(), sa.ForeignKey("wishes.id"), nullable=True),
        sa.Column("available_for", sa.String(16), nullable=False, server_default="all"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_index("ix_reward_items_family_active", "reward_items", ["family_id", "is_active"])

    # 6. reward_purchases
    op.create_table(
        "reward_purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reward_item_id", sa.Integer(), sa.ForeignKey("reward_items.id"), nullable=False),
        sa.Column("points_spent", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("purchased_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("fulfilled_at", sa.DateTime(), nullable=True),
        sa.Column("fulfilled_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_reward_purchases_family_status", "reward_purchases", ["family_id", "status"])

    # 7. stats_cache
    op.create_table(
        "stats_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("stat_type", sa.String(64), nullable=False),
        sa.Column("period_key", sa.String(32), nullable=False),
        sa.Column("data_json", sa.Text(), nullable=False),
        sa.Column("computed_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("family_id", "user_id", "stat_type", "period_key", name="uq_stats_cache"),
    )
    op.create_index("ix_stats_cache_lookup", "stats_cache", ["family_id", "stat_type", "period_key"])

    # 8. dashboard_layouts
    op.create_table(
        "dashboard_layouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("layout_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade():
    op.drop_table("dashboard_layouts")
    op.drop_index("ix_stats_cache_lookup", "stats_cache")
    op.drop_table("stats_cache")
    op.drop_index("ix_reward_purchases_family_status", "reward_purchases")
    op.drop_table("reward_purchases")
    op.drop_index("ix_reward_items_family_active", "reward_items")
    op.drop_table("reward_items")
    op.drop_table("user_streaks")
    op.drop_index("ix_earned_badges_user_family", "earned_badges")
    op.drop_table("earned_badges")
    op.drop_table("badge_definitions")
    with op.batch_alter_table("chore_tasks") as b:
        b.drop_column("calendar_visibility")
        b.drop_column("color_tag")
