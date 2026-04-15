"""LLM 챗봇 API"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.chore import ChoreTask, TaskStatus, IntensityLevel
from app.models.family import Family, FamilyMember
from app.models.user import User
from app.services import llm as llm_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    family_id: int
    tts_target: str = ""
    tts_engine: str = ""


@router.post("/message")
async def chat_message(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """LLM 챗봇 메시지 처리 + (선택) TTS 발화"""
    family = db.get(Family, body.family_id)
    today = date.today()
    tasks = db.query(ChoreTask).filter(
        ChoreTask.family_id == body.family_id,
        ChoreTask.status == TaskStatus.PENDING,
        ChoreTask.due_date >= today,
        ChoreTask.due_date <= today + timedelta(days=7),
    ).order_by(ChoreTask.due_date).limit(15).all()
    members = db.query(FamilyMember).filter(
        FamilyMember.family_id == body.family_id
    ).all()

    context = {
        "family_name": family.name if family else "우리 가족",
        "tasks": [{"name": t.name, "id": t.id} for t in tasks],
        "members": [m.user.name if m.user else m.family_role for m in members],
    }

    result = await llm_service.chat(
        message=body.message,
        context=context,
        tts_target=body.tts_target,
        tts_engine=body.tts_engine,
    )

    # 현재 유저의 가족 멤버 찾기 (액션 처리에 필요)
    member = db.query(FamilyMember).filter(
        FamilyMember.family_id == body.family_id,
        FamilyMember.user_id == current_user.id,
    ).first()

    # ── 인텐트 기반 액션 처리 ──
    intent = result.get("intent", "")
    target_name = result.get("target", "").strip()

    if intent == "complete" and target_name:
        # 오늘 할일 중 이름이 일치하는 것 완료 처리
        task = next(
            (t for t in tasks if target_name in t.name or t.name in target_name), None
        )
        if task:
            result["action"] = {
                "type": "complete_task",
                "task_id": task.id,
                "task_name": task.name,
            }

    elif intent == "add" and target_name and member:
        # Phase 10-1: 자연어 날짜/담당자 파싱
        from app.services.llm import parse_date_from_text, parse_assignee_from_text
        from app.models.family import FamilyMember as FM
        members_list = db.query(FM).filter(FM.family_id == body.family_id).all()
        parsed_due = parse_date_from_text(body.message, today) or today
        parsed_assignee = parse_assignee_from_text(body.message, members_list, db)

        new_task = ChoreTask(
            family_id=body.family_id,
            name=target_name,
            category="기타",
            estimated_minutes=30,
            intensity=IntensityLevel.NORMAL,
            status=TaskStatus.PENDING,
            due_date=parsed_due,
            assigned_to=parsed_assignee,
            created_by=member.id,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        result["action"] = {
            "type": "add_task",
            "task_id": new_task.id,
            "task_name": new_task.name,
            "due_date": str(parsed_due),
            "assigned_to": parsed_assignee,
        }

    return result


@router.get("/health")
async def chat_health():
    """LLM 서버 연결 상태"""
    return await llm_service.health()
