"""포인트 상점 모델 — RewardItem, RewardPurchase"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RewardItem(Base):
    """상점에서 구매 가능한 보상 아이템"""
    __tablename__ = "reward_items"
    __table_args__ = (
        Index("ix_reward_items_family_active", "family_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(64), nullable=False, default="🎁")
    point_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)  # -1=무제한
    max_per_user: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)  # -1=무제한
    # category: general | privilege | activity | item
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="general")
    linked_wish_id: Mapped[int | None] = mapped_column(ForeignKey("wishes.id"), nullable=True)
    # available_for: all | child | adult
    available_for: Mapped[str] = mapped_column(String(16), nullable=False, default="all")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    purchases: Mapped[list["RewardPurchase"]] = relationship(back_populates="reward_item")


class RewardPurchase(Base):
    """포인트 상점 구매 기록"""
    __tablename__ = "reward_purchases"
    __table_args__ = (
        Index("ix_reward_purchases_family_status", "family_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_item_id: Mapped[int] = mapped_column(ForeignKey("reward_items.id"), nullable=False)
    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    # status: pending | approved | rejected | fulfilled
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fulfilled_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    reward_item: Mapped["RewardItem"] = relationship(back_populates="purchases")
