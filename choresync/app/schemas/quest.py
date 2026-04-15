"""Quest, Wish Pydantic 스키마"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.quest import QuestStatus, WishStatus


# ── Quest ─────────────────────────────────────────────────────────────────────

class QuestCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    reward_points: float = Field(default=10.0, ge=0)
    deadline: Optional[datetime] = None


class QuestOut(BaseModel):
    id: int
    family_id: int
    title: str
    description: Optional[str]
    reward_points: float
    status: QuestStatus
    created_by: int
    accepted_by: Optional[int]
    confirmed_by: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Wish ──────────────────────────────────────────────────────────────────────

class WishCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    point_cost: float = Field(default=0.0, ge=0)  # 0이면 투표로 결정


class WishOut(BaseModel):
    id: int
    family_id: int
    title: str
    description: Optional[str]
    point_cost: float
    status: WishStatus
    requested_by: int
    approved_by: Optional[int]
    fulfilled_by: Optional[int]
    created_at: datetime
    fulfilled_at: Optional[datetime]
    vote_count: int = 0
    approve_count: int = 0
    reject_count: int = 0
    my_vote: Optional[bool] = None

    model_config = {"from_attributes": True}


class WishVoteCreate(BaseModel):
    approved: bool
    comment: Optional[str] = None


class WishVoteOut(BaseModel):
    id: int
    wish_id: int
    member_id: int
    approved: bool
    comment: Optional[str]
    voted_at: datetime

    model_config = {"from_attributes": True}
