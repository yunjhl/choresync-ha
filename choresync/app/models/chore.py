"""ChoreTemplate, ChoreTask, CompletionHistory, WeeklyReport 모델"""

import enum
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IntensityLevel(str, enum.Enum):
    LIGHT = "Light"
    NORMAL = "Normal"
    HARD = "Hard"


INTENSITY_MULTIPLIER = {
    IntensityLevel.LIGHT: 1.0,
    IntensityLevel.NORMAL: 1.5,
    IntensityLevel.HARD: 2.0,
}


class TaskStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    SKIPPED = "Skipped"


class ChoreTemplate(Base):
    """재사용 가능한 할일 템플릿"""

    __tablename__ = "chore_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="기타")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    intensity: Mapped[IntensityLevel] = mapped_column(
        Enum(IntensityLevel), nullable=False, default=IntensityLevel.NORMAL
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_marketplace: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ha_entity_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    trigger_context: Mapped[str | None] = mapped_column(String(20), nullable=True)  # on_arrival / on_departure
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("family_members.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    recurrence_interval: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recurrence_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assignee_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    family = relationship("Family")
    assignee = relationship("FamilyMember", foreign_keys=[assigned_to])
    tasks = relationship("ChoreTask", back_populates="template", cascade="all, delete-orphan")


class ChoreTask(Base):
    """특정 날짜에 할당된 할일 인스턴스"""

    __tablename__ = "chore_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("chore_templates.id"), nullable=True
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="기타")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    intensity: Mapped[IntensityLevel] = mapped_column(
        Enum(IntensityLevel), nullable=False, default=IntensityLevel.NORMAL
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color_tag: Mapped[str | None] = mapped_column(String(16), nullable=True)
    calendar_visibility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Phase 9-1: 위임 시스템
    delegated_to: Mapped[int | None] = mapped_column(ForeignKey("family_members.id"), nullable=True)
    delegation_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    delegation_status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # requested/accepted/rejected

    template = relationship("ChoreTemplate", back_populates="tasks")
    assignee = relationship("FamilyMember", foreign_keys=[assigned_to])
    creator = relationship("FamilyMember", foreign_keys=[created_by])
    delegate_member = relationship("FamilyMember", foreign_keys=[delegated_to])
    history = relationship("CompletionHistory", back_populates="task", cascade="all, delete-orphan")


class CompletionHistory(Base):
    """할일 완료 기록"""

    __tablename__ = "completion_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("chore_tasks.id"), nullable=False, index=True)
    completed_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    score_earned: Mapped[float] = mapped_column(Float, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    task = relationship("ChoreTask", back_populates="history")
    member = relationship("FamilyMember")


class WeeklyReport(Base):
    """주간 리포트 저장 (매주 일요일 생성)"""

    __tablename__ = "weekly_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    achievement_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mvp_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
