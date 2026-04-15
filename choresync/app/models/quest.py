"""Quest, Wish 모델 — 상태머신 기반"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestStatus(str, enum.Enum):
    OPEN = "Open"
    ACCEPTED = "Accepted"
    PENDING_CONFIRM = "PendingConfirm"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class WishStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"


class Quest(Base):
    """가족 미션 — 완료 시 포인트 지급"""

    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reward_points: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    status: Mapped[QuestStatus] = mapped_column(
        Enum(QuestStatus), nullable=False, default=QuestStatus.OPEN
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    accepted_by: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    confirmed_by: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    creator = relationship("FamilyMember", foreign_keys=[created_by])
    acceptor = relationship("FamilyMember", foreign_keys=[accepted_by])
    confirmer = relationship("FamilyMember", foreign_keys=[confirmed_by])


class Wish(Base):
    """위시리스트 — 포인트로 잠금 해제"""

    __tablename__ = "wishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    point_cost: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    status: Mapped[WishStatus] = mapped_column(
        Enum(WishStatus), nullable=False, default=WishStatus.PENDING
    )
    requested_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    fulfilled_by: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    requester = relationship("FamilyMember", foreign_keys=[requested_by])
    approver = relationship("FamilyMember", foreign_keys=[approved_by])
    fulfiller = relationship("FamilyMember", foreign_keys=[fulfilled_by])
    votes = relationship("WishVote", back_populates="wish", cascade="all, delete-orphan")
