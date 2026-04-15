"""통계 집계 캐시 모델"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class StatsCache(Base):
    """APScheduler 매시간 갱신되는 통계 캐시"""
    __tablename__ = "stats_cache"
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", "stat_type", "period_key", name="uq_stats_cache"),
        Index("ix_stats_cache_lookup", "family_id", "stat_type", "period_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)  # None=가족 전체
    # stat_type: heatmap | weekly_chart | category_breakdown | family_ranking | balance
    stat_type: Mapped[str] = mapped_column(String(64), nullable=False)
    # period_key: "2026-W15" | "2026-04" | "2026" | "all_time"
    period_key: Mapped[str] = mapped_column(String(32), nullable=False)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
