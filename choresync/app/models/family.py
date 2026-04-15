"""Family, FamilyMember, Invitation 모델"""

import enum
import secrets
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MemberRole(str, enum.Enum):
    ADMIN = "Admin"
    MEMBER = "Member"


class InvitationStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    EXPIRED = "Expired"


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    invite_code: Mapped[str] = mapped_column(
        String(20), unique=True, default=lambda: secrets.token_urlsafe(10)
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # TTS / 브리핑 설정
    tts_player: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tts_engine: Mapped[str | None] = mapped_column(String(200), nullable=True)
    briefing_hour: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    briefing_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="family", cascade="all, delete-orphan")


class FamilyMember(Base):
    __tablename__ = "family_members"
    __table_args__ = (UniqueConstraint("user_id", "family_id", name="uq_user_family"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole), default=MemberRole.MEMBER, nullable=False
    )
    family_role: Mapped[str] = mapped_column(String(20), default="기타")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="memberships")
    family = relationship("Family", back_populates="members")


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(8)
    )
    invited_by: Mapped[int] = mapped_column(ForeignKey("family_members.id"), nullable=False)
    accepted_by: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id"), nullable=True
    )
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False
    )
    invited_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    family = relationship("Family", back_populates="invitations")
