"""Chore 관련 Pydantic 스키마"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.chore import IntensityLevel, TaskStatus


# ── Template ──────────────────────────────────────────────────────────────────

class TemplateBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(default="기타", max_length=50)
    estimated_minutes: int = Field(default=15, ge=1, le=480)
    intensity: IntensityLevel = IntensityLevel.NORMAL
    description: Optional[str] = None
    recurrence_interval: Optional[str] = None
    recurrence_day: Optional[int] = None
    trigger_context: Optional[str] = None


class TemplateCreate(TemplateBase):
    pass


class TemplatePatch(BaseModel):
    recurrence_interval: Optional[str] = None
    recurrence_day: Optional[int] = None
    trigger_context: Optional[str] = None
    assigned_to: Optional[int] = None


class TemplateOut(TemplateBase):
    id: int
    family_id: int
    is_active: bool
    is_marketplace: bool = False
    ha_entity_id: Optional[str] = None
    trigger_context: Optional[str] = None
    assigned_to: Optional[int] = None
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(default="기타", max_length=50)
    estimated_minutes: int = Field(default=15, ge=1, le=480)
    intensity: IntensityLevel = IntensityLevel.NORMAL
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None
    template_id: Optional[int] = None
    note: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    family_id: int
    template_id: Optional[int]
    assigned_to: Optional[int]
    name: str
    category: str
    estimated_minutes: int
    intensity: IntensityLevel
    score: float
    due_date: Optional[date]
    status: TaskStatus
    note: Optional[str]
    photo_url: Optional[str] = None
    created_by: int
    created_at: datetime
    # Phase 9-1: 위임
    delegated_to: Optional[int] = None
    delegation_note: Optional[str] = None
    delegation_status: Optional[str] = None

    model_config = {"from_attributes": True}


class TaskComplete(BaseModel):
    note: Optional[str] = None
    sim_date: Optional[str] = None  # "YYYY-MM-DD", simulation only


# ── Delegation ────────────────────────────────────────────────────────────────

class DelegateRequest(BaseModel):
    delegated_to: int
    note: Optional[str] = None


# ── CompletionHistory ─────────────────────────────────────────────────────────

class HistoryOut(BaseModel):
    id: int
    task_id: int
    completed_by: int
    score_earned: float
    completed_at: datetime
    note: Optional[str]

    model_config = {"from_attributes": True}
