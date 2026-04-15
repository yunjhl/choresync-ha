"""HA 통합 라우터 — 센서/자동화 조회, 서비스 호출, webhook 할일 생성"""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from app.services.ha_api import get_states, trigger_automation, call_service
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/ha", tags=["ha"])

VISIBLE_DOMAINS = {
    "sensor", "binary_sensor", "automation", "switch",
    "light", "input_boolean", "input_number", "input_select",
    "cover", "climate", "media_player", "person", "device_tracker",
    "script", "scene",
}


def _available() -> bool:
    return bool(os.environ.get("SUPERVISOR_TOKEN") or
                (os.environ.get("HA_URL") and os.environ.get("HA_TOKEN")))


@router.get("/states")
async def ha_states(current_user=Depends(get_current_user)):
    """HA 엔티티 상태 목록 (도메인별 그룹)"""
    if not _available():
        return {"available": False, "message": "HA Supervisor 연결 없음 (SUPERVISOR_TOKEN 미설정)", "groups": {}}

    states, err = await get_states()
    if err:
        raise HTTPException(502, detail=f"HA API 오류: {err}")

    groups = {}
    for entity in states:
        domain = entity["entity_id"].split(".")[0]
        if domain not in VISIBLE_DOMAINS:
            continue
        groups.setdefault(domain, []).append({
            "entity_id": entity["entity_id"],
            "state": entity["state"],
            "friendly_name": entity.get("attributes", {}).get("friendly_name", entity["entity_id"]),
            "unit": entity.get("attributes", {}).get("unit_of_measurement", ""),
            "last_changed": entity.get("last_changed", ""),
            "icon": entity.get("attributes", {}).get("icon", ""),
            "device_class": entity.get("attributes", {}).get("device_class", ""),
        })

    for domain in groups:
        groups[domain].sort(key=lambda x: x["friendly_name"])

    return {"available": True, "groups": groups, "total": len(states)}


@router.get("/automations")
async def ha_automations(current_user=Depends(get_current_user)):
    """HA 자동화 목록"""
    if not _available():
        return {"available": False, "automations": []}

    states, err = await get_states()
    if err:
        raise HTTPException(502, detail=f"HA API 오류: {err}")

    automations = []
    for entity in states:
        if not entity["entity_id"].startswith("automation."):
            continue
        attrs = entity.get("attributes", {})
        automations.append({
            "entity_id": entity["entity_id"],
            "friendly_name": attrs.get("friendly_name", entity["entity_id"]),
            "state": entity["state"],
            "last_triggered": attrs.get("last_triggered", ""),
            "mode": attrs.get("mode", ""),
        })

    automations.sort(key=lambda x: x["friendly_name"])
    return {"available": True, "automations": automations}


@router.get("/media-players")
async def ha_media_players(current_user=Depends(get_current_user)):
    """HA media_player 엔티티 목록 (TTS 대상 선택용)"""
    if not _available():
        return {"available": False, "players": []}

    states, err = await get_states()
    if err:
        return {"available": False, "players": [], "error": str(err)}

    # friendly_name 있는 것 우선, 같은 이름 중복 제거, unavailable 제외
    candidates = []
    for entity in states:
        if not entity["entity_id"].startswith("media_player."):
            continue
        if entity.get("state") == "unavailable":
            continue
        attrs = entity.get("attributes", {})
        name = attrs.get("friendly_name", "")
        candidates.append({
            "entity_id": entity["entity_id"],
            "friendly_name": name,
            "state": entity["state"],
            "has_name": bool(name),
        })
    # friendly_name 있는 것 먼저 정렬 후 중복 제거
    candidates.sort(key=lambda x: (not x["has_name"], x["friendly_name"] or x["entity_id"]))
    seen = set()
    players = []
    for c in candidates:
        display = c["friendly_name"] or c["entity_id"]
        if display in seen:
            continue
        seen.add(display)
        players.append({
            "entity_id": c["entity_id"],
            "friendly_name": display,
            "state": c["state"],
        })
    players.sort(key=lambda x: x["friendly_name"])
    return {"available": True, "players": players}


class TriggerBody(BaseModel):
    entity_id: str


@router.post("/automations/trigger")
async def ha_trigger_automation(body: TriggerBody, current_user=Depends(get_current_user)):
    """HA 자동화 수동 트리거"""
    if not _available():
        raise HTTPException(503, "HA Supervisor 연결 없음")
    result, err = await trigger_automation(body.entity_id)
    if err:
        raise HTTPException(502, detail=f"HA API 오류: {err}")
    return {"ok": True, "entity_id": body.entity_id}


class ServiceBody(BaseModel):
    domain: str
    service: str
    data: dict = {}


@router.post("/service")
async def ha_call_service(body: ServiceBody, current_user=Depends(get_current_user)):
    """HA 서비스 호출 (switch.turn_on 등)"""
    if not _available():
        raise HTTPException(503, "HA Supervisor 연결 없음")
    result, err = await call_service(body.domain, body.service, body.data)
    if err:
        raise HTTPException(502, detail=f"HA API 오류: {err}")
    return {"ok": True}


# ── Webhook: HA automation → ChoreSync 할일 자동 생성 ──────────────────────

class WebhookTaskBody(BaseModel):
    task_name: str
    category: str = "IoT/HA 자동화"
    estimated_minutes: int = 15
    note: str | None = None


@router.post("/webhook/{invite_code}/task", status_code=201)
async def webhook_create_task(invite_code: str, body: WebhookTaskBody):
    """
    HA automation에서 인증 없이 호출 가능한 webhook.
    invite_code로 family 식별 → ChoreTask 자동 생성 + SSE 알림.
    """
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.family import Family
    from app.models.chore import ChoreTask, IntensityLevel
    from app.services.chore import calc_score
    from app.services.sse import broadcast

    db: Session = SessionLocal()
    try:
        family = db.query(Family).filter(Family.invite_code == invite_code).first()
        if not family:
            raise HTTPException(404, "유효하지 않은 초대 코드")

        task = ChoreTask(
            family_id=family.id,
            name=body.task_name,
            category=body.category,
            estimated_minutes=body.estimated_minutes,
            intensity=IntensityLevel.NORMAL,
            score=calc_score(body.estimated_minutes, IntensityLevel.NORMAL),
            created_by=1,  # 시스템 생성
            note=body.note,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        broadcast(family.id, "task_created", {
            "task_id": task.id,
            "name": task.name,
            "source": "ha_webhook",
        })

        return {
            "task_id": task.id,
            "task_name": task.name,
            "family_id": family.id,
            "score": task.score,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()


@router.get("/webhook/{invite_code}/yaml", response_class=PlainTextResponse)
async def webhook_yaml(
    invite_code: str,
    entity_id: str = "",
    to_state: str = "",
    task_name: str = "할일",
    category: str = "IoT/HA 자동화",
    estimated_minutes: int = 15,
):
    """
    HA automation YAML + rest_command 설정 자동 생성 (복사용).
    """
    from app.database import SessionLocal
    from app.models.family import Family

    db = SessionLocal()
    try:
        family = db.query(Family).filter(Family.invite_code == invite_code).first()
        if not family:
            raise HTTPException(404, "유효하지 않은 초대 코드")
    finally:
        db.close()

    # HA addon이 어떤 IP에서 접근 가능한지 SUPERVISOR_TOKEN 여부로 판단
    sup = os.environ.get("SUPERVISOR_TOKEN")
    # HA addon URL: 같은 HA 내에서 localhost or supervisor
    webhook_url = f"http://homeassistant.local:8099/api/ha/webhook/{invite_code}/task"

    trigger_block = ""
    if entity_id and to_state:
        trigger_block = f"""trigger:
  - platform: state
    entity_id: {entity_id}
    to: "{to_state}"
"""
    elif entity_id:
        trigger_block = f"""trigger:
  - platform: state
    entity_id: {entity_id}
"""
    else:
        trigger_block = """trigger:
  - platform: state
    entity_id: sensor.your_sensor
    to: "your_state"
"""

    yaml_text = f"""# ── HA automation YAML ─────────────────────────────────────────────
alias: "{task_name} — ChoreSync 자동 생성"
description: "ChoreSync webhook으로 '{task_name}' 할일을 자동 생성합니다"
{trigger_block}
action:
  - service: rest_command.choresync_create_task
    data:
      task_name: "{task_name}"
      category: "{category}"
      estimated_minutes: {estimated_minutes}

mode: single

# ── configuration.yaml 에 추가할 rest_command ───────────────────────
# (한 번만 추가하면 모든 ChoreSync webhook에서 재사용 가능)
#
# rest_command:
#   choresync_create_task:
#     url: "{webhook_url}"
#     method: POST
#     content_type: "application/json"
#     payload: >-
#       {{"task_name": "{{{{ task_name }}}}", "category": "{{{{ category }}}}", "estimated_minutes": {{{{ estimated_minutes }}}}}}
#
# ── 설정 후 HA 재시작 필요 ──────────────────────────────────────────
# 1. configuration.yaml 에 위 rest_command 블록 추가
# 2. HA 설정 > 서버 제어 > 재시작
# 3. 위 automation YAML을 자동화 편집기에 붙여넣기
"""
    return yaml_text


# ── TTS 엔진 목록 ──────────────────────────────────────────────────────────────

@router.get("/tts-entities")
async def ha_tts_entities(current_user=Depends(get_current_user)):
    """tts.* 도메인 엔티티 목록 반환 (TTS 엔진 선택용)"""
    if not _available():
        return {"available": False, "entities": []}
    states, err = await get_states()
    if err:
        return {"available": False, "entities": [], "error": str(err)}
    entities = []
    for entity in states:
        if not entity["entity_id"].startswith("tts."):
            continue
        attrs = entity.get("attributes", {})
        entities.append({
            "entity_id": entity["entity_id"],
            "friendly_name": attrs.get("friendly_name", entity["entity_id"]),
        })
    return {"available": True, "entities": entities}


# ── HA 연동 템플릿 관리 ────────────────────────────────────────────────────────

@router.get("/templates/{family_id}")
async def ha_list_templates(family_id: int, current_user=Depends(get_current_user)):
    """가족의 ChoreTemplate 목록 (ha_entity_id 포함)"""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.chore import ChoreTemplate
    db: Session = SessionLocal()
    try:
        templates = db.query(ChoreTemplate).filter(
            ChoreTemplate.family_id == family_id,
            ChoreTemplate.is_active.is_(True),
            ChoreTemplate.is_marketplace.is_(False),
        ).all()
        return [{
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "estimated_minutes": t.estimated_minutes,
            "ha_entity_id": t.ha_entity_id,
            "recurrence_interval": t.recurrence_interval,
        } for t in templates]
    finally:
        db.close()


class TemplateLinkBody(BaseModel):
    template_id: int | None = None
    entity_id: str
    task_name: str | None = None
    category: str = "IoT/HA 자동화"
    estimated_minutes: int = 15
    recurrence_interval: str | None = None


@router.post("/templates/{family_id}/link")
async def ha_link_template(family_id: int, body: TemplateLinkBody, current_user=Depends(get_current_user)):
    """기존 템플릿에 ha_entity_id 연결하거나 새 템플릿을 생성해서 연결"""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.chore import ChoreTemplate
    from app.models.family import FamilyMember
    db: Session = SessionLocal()
    try:
        if body.template_id:
            tmpl = db.get(ChoreTemplate, body.template_id)
            if not tmpl or tmpl.family_id != family_id:
                raise HTTPException(404, "템플릿을 찾을 수 없음")
            tmpl.ha_entity_id = body.entity_id
            db.commit()
            db.refresh(tmpl)
            return {"template_id": tmpl.id, "name": tmpl.name, "ha_entity_id": tmpl.ha_entity_id, "action": "linked"}
        else:
            first_member = db.query(FamilyMember).filter(
                FamilyMember.family_id == family_id,
                FamilyMember.is_active.is_(True),
            ).first()
            if not first_member:
                raise HTTPException(404, "가족 구성원 없음")
            name = body.task_name or body.entity_id.split(".")[-1].replace("_", " ")
            tmpl = ChoreTemplate(
                family_id=family_id,
                created_by=first_member.id,
                name=name,
                category=body.category,
                estimated_minutes=body.estimated_minutes,
                ha_entity_id=body.entity_id,
                is_marketplace=False,
                recurrence_interval=body.recurrence_interval,
            )
            db.add(tmpl)
            db.commit()
            db.refresh(tmpl)
            return {"template_id": tmpl.id, "name": tmpl.name, "ha_entity_id": tmpl.ha_entity_id, "action": "created"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()

@router.get("/notify-entities")
async def ha_notify_entities(current_user=Depends(get_current_user)):
    """HA notify.mobile_app_* 엔티티 목록 반환"""
    from app.services.ha_notify import ha_get_notify_entities
    entities = await ha_get_notify_entities()
    return {"entities": entities}


class MobilePushTestBody(BaseModel):
    entity: str

@router.post("/mobile-push-test")
async def ha_mobile_push_test(body: MobilePushTestBody, current_user=Depends(get_current_user)):
    """HA 모바일 앱 테스트 푸시 발송"""
    from app.services.ha_notify import ha_mobile_push
    ok = await ha_mobile_push(body.entity, "ChoreSync 테스트 알림입니다!", title="ChoreSync 테스트")
    if not ok:
        raise HTTPException(502, "알림 전송 실패 — HA 연결 또는 엔티티 확인 필요")
    return {"status": "sent"}