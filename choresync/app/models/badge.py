"""배지/업적 + 스트릭 모델"""
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BadgeDefinition(Base):
    """시스템 또는 가족 커스텀 배지 정의"""
    __tablename__ = "badge_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int | None] = mapped_column(ForeignKey("families.id"), nullable=True)  # None=전역
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(64), nullable=False, default="🏆")
    # badge_type: streak | category | score_total | score_monthly | task_count | first_complete | special
    badge_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # condition_json 예: {"type":"streak","days":7} | {"type":"score_total","threshold":1000}
    condition_json: Mapped[str] = mapped_column(Text, nullable=False)
    # tier: bronze | silver | gold | platinum | special
    tier: Mapped[str] = mapped_column(String(16), nullable=False, default="bronze")
    points_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    earned_badges: Mapped[list["EarnedBadge"]] = relationship(back_populates="badge_definition")


class EarnedBadge(Base):
    """사용자가 획득한 배지 기록"""
    __tablename__ = "earned_badges"
    __table_args__ = (
        UniqueConstraint("user_id", "badge_definition_id", name="uq_user_badge"),
        Index("ix_earned_badges_user_family", "user_id", "family_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    badge_definition_id: Mapped[int] = mapped_column(ForeignKey("badge_definitions.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    badge_definition: Mapped["BadgeDefinition"] = relationship(back_populates="earned_badges")


class UserStreak(Base):
    """사용자 연속 완료 스트릭"""
    __tablename__ = "user_streaks"
    __table_args__ = (
        UniqueConstraint("user_id", "family_id", name="uq_user_family_streak"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    streak_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
