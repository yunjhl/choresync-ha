"""템플릿 마켓플레이스 모델"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.chore import IntensityLevel


class MarketplaceTemplate(Base):
    __tablename__ = "marketplace_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="기타")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    intensity: Mapped[IntensityLevel] = mapped_column(Enum(IntensityLevel), nullable=False, default=IntensityLevel.NORMAL)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_by_family_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    import_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    family_size: Mapped[str] = mapped_column(String(20), nullable=False, default="전체")
    recurrence_interval: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recurrence_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trigger_context: Mapped[str | None] = mapped_column(String(20), nullable=True)  # on_arrival / on_departure
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 최소 수행 연령
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 최대 수행 연령 (None=제한없음)
    assignee_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # adult_only / child_assist / child_independent / None
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
