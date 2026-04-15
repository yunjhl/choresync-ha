"""IoT 기기/트리거 CRUD + SSE 스트림 라우터"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_family_member, get_admin_member
from app.models.family import FamilyMember
from app.models.iot import DeviceType, IoTDevice, IoTTrigger
from app.models.user import User
from app.services.sse import event_generator

router = APIRouter(prefix="/api", tags=["iot"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DeviceCreate(BaseModel):
    name: str = Field(..., max_length=100)
    device_type: DeviceType = DeviceType.SENSOR
    mqtt_topic: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class DeviceOut(BaseModel):
    id: int
    family_id: int
    name: str
    device_type: DeviceType
    mqtt_topic: Optional[str]
    description: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}


class TriggerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    payload_match: Optional[str] = Field(None, max_length=200)
    task_name: str = Field(..., max_length=100)
    task_category: str = Field(default="IoT", max_length=50)
    task_estimated_minutes: int = Field(default=15, ge=1, le=480)


class TriggerOut(BaseModel):
    id: int
    device_id: int
    name: str
    payload_match: Optional[str]
    task_name: str
    task_category: str
    task_estimated_minutes: int
    is_active: bool
    model_config = {"from_attributes": True}


# ── Devices ───────────────────────────────────────────────────────────────────

@router.get("/families/{family_id}/devices", response_model=list[DeviceOut])
def list_devices(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    return db.query(IoTDevice).filter(IoTDevice.family_id == family_id).all()


@router.post("/families/{family_id}/devices", response_model=DeviceOut, status_code=201)
def create_device(
    family_id: int,
    body: DeviceCreate,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    device = IoTDevice(family_id=family_id, **body.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.delete("/families/{family_id}/devices/{device_id}", status_code=204)
def delete_device(
    family_id: int,
    device_id: int,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    device = db.get(IoTDevice, device_id)
    if not device or device.family_id != family_id:
        raise HTTPException(404, "기기를 찾을 수 없음")
    device.is_active = False
    db.commit()


# ── Triggers ─────────────────────────────────────────────────────────────────

@router.get("/families/{family_id}/devices/{device_id}/triggers", response_model=list[TriggerOut])
def list_triggers(
    family_id: int,
    device_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    device = db.get(IoTDevice, device_id)
    if not device or device.family_id != family_id:
        raise HTTPException(404, "기기를 찾을 수 없음")
    return db.query(IoTTrigger).filter(
        IoTTrigger.device_id == device_id, IoTTrigger.is_active.is_(True)
    ).all()


@router.post("/families/{family_id}/devices/{device_id}/triggers", response_model=TriggerOut, status_code=201)
def create_trigger(
    family_id: int,
    device_id: int,
    body: TriggerCreate,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    device = db.get(IoTDevice, device_id)
    if not device or device.family_id != family_id:
        raise HTTPException(404, "기기를 찾을 수 없음")
    trigger = IoTTrigger(device_id=device_id, **body.model_dump())
    db.add(trigger)
    db.commit()
    db.refresh(trigger)
    return trigger


# ── SSE ───────────────────────────────────────────────────────────────────────

@router.get("/sse/{family_id}/events")
async def sse_events(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SSE 스트림 — 클라이언트가 구독 유지"""
    from app.models.family import FamilyMember as FM
    member = db.query(FM).filter(
        FM.user_id == current_user.id, FM.family_id == family_id
    ).first()
    if not member:
        raise HTTPException(403, "이 가족의 구성원이 아닙니다")

    return StreamingResponse(
        event_generator(family_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
