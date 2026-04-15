"""귀가/외출 presence webhook"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
import logging

from app.database import get_db
from app.models.chore import ChoreTask, ChoreTemplate, TaskStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhook", tags=["webhook"])


class PresenceEvent(BaseModel):
    person_entity: str
    state: str           # "home" or "not_home"
    family_id: int
    tts_target: str = "" # 알릴 스피커 entity


@router.post("/presence")
async def presence_webhook(body: PresenceEvent, db: Session = Depends(get_db)):
    """HA 자동화에서 귀가/외출 이벤트 수신 → TTS 알림"""
    today = date.today()

    if body.state == "home":
        # 귀가: on_arrival 할일 + 오늘 미완료 할일 알림
        pending = db.query(ChoreTask).filter(
            ChoreTask.family_id == body.family_id,
            ChoreTask.status == TaskStatus.PENDING,
            ChoreTask.due_date == today,
        ).all()

        arrival_tmpls = db.query(ChoreTemplate).filter(
            ChoreTemplate.family_id == body.family_id,
            ChoreTemplate.trigger_context == "on_arrival",
            ChoreTemplate.is_active.is_(True),
        ).all()

        arrival_names = [t.name for t in arrival_tmpls]
        pending_count = len(pending)

        if pending_count > 0 or arrival_names:
            parts = []
            if arrival_names:
                parts.append("귀가 체크: " + ", ".join(arrival_names[:3]))
            if pending_count > 0:
                parts.append(f"오늘 남은 할일 {pending_count}개")
            msg = "돌아오셨군요! " + " | ".join(parts)
        else:
            msg = "수고하셨어요! 오늘 할일 모두 완료했습니다."

    elif body.state == "not_home":
        # 외출: on_departure 체크리스트 알림
        dep_tmpls = db.query(ChoreTemplate).filter(
            ChoreTemplate.family_id == body.family_id,
            ChoreTemplate.trigger_context == "on_departure",
            ChoreTemplate.is_active.is_(True),
        ).all()
        if dep_tmpls:
            names = ", ".join([t.name for t in dep_tmpls[:4]])
            msg = f"외출 전 확인: {names}"
        else:
            msg = "안전하게 다녀오세요!"
    else:
        return {"ok": False, "msg": "unknown state"}

    logger.info("Presence webhook: %s %s → %s", body.person_entity, body.state, msg[:50])

    if body.tts_target:
        try:
            from app.services.ha_notify import ha_tts
            await ha_tts(msg, media_player=body.tts_target)
        except Exception as e:
            logger.warning("Presence TTS failed: %s", e)

    return {"ok": True, "msg": msg, "state": body.state}
