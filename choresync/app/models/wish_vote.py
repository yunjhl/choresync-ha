"""WishVote 모델 — 위시 투표"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WishVote(Base):
    """가족 구성원의 위시 승인/거절 투표"""

    __tablename__ = "wish_votes"
    __table_args__ = (UniqueConstraint("wish_id", "member_id", name="uq_wish_vote_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    wish_id: Mapped[int] = mapped_column(ForeignKey("wishes.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("family_members.id", ondelete="CASCADE"), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    voted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    wish = relationship("Wish", back_populates="votes")
    member = relationship("FamilyMember")
