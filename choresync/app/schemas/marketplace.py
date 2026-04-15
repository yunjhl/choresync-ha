"""마켓플레이스 Pydantic 스키마"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.chore import IntensityLevel


class MarketplaceTemplateOut(BaseModel):
    id: int
    name: str
    category: str
    estimated_minutes: int
    intensity: IntensityLevel
    description: str | None
    import_count: int
    family_size: str = "전체"
    recurrence_interval: str | None = None
    recurrence_day: int | None = None
    trigger_context: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    assignee_type: str | None = None  # "adult_only" | "child_assist" | "child_independent" | None
    points: float = 0.0        # 계산값: round(minutes/5 × multiplier, 1)
    is_imported: bool = False  # 현재 가족이 이미 추가했는지
    created_at: datetime
    model_config = {"from_attributes": True}


class MarketplaceTemplateCreate(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(default="기타", max_length=50)
    estimated_minutes: int = Field(default=15, ge=1, le=480)
    intensity: IntensityLevel = IntensityLevel.NORMAL
    description: str | None = None
    family_size: str = Field(default="전체", max_length=20)
    recurrence_interval: str | None = None
    recurrence_day: int | None = None
    trigger_context: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    assignee_type: str | None = None
