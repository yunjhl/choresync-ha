"""가족/구성원/초대 관련 Pydantic 스키마"""

from datetime import datetime

from pydantic import BaseModel, Field


class FamilyResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FamilySettingsResponse(BaseModel):
    tts_player: str | None = None
    tts_engine: str | None = None
    briefing_hour: int = 7
    briefing_enabled: bool = False

    model_config = {"from_attributes": True}


class UpdateFamilySettingsRequest(BaseModel):
    tts_player: str | None = None
    tts_engine: str | None = None
    briefing_hour: int | None = Field(None, ge=0, le=23)
    briefing_enabled: bool | None = None


class MemberResponse(BaseModel):
    id: int
    user_id: int
    family_id: int
    name: str = ""
    email: str = ""
    role: str
    family_role: str
    age: int | None
    joined_at: datetime

    model_config = {"from_attributes": True}


class UpdateMemberRequest(BaseModel):
    family_role: str | None = Field(None, max_length=20)
    age: int | None = None
    role: str | None = None  # Admin만 변경 가능


class CreateInvitationRequest(BaseModel):
    expires_days: int = Field(default=7, ge=1, le=30)
    invited_email: str | None = None


class InvitationResponse(BaseModel):
    id: int
    code: str
    status: str
    invited_email: str | None = None
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
