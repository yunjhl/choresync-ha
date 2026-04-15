"""할일 관리 API 라우터"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import os
import uuid
import aiofiles

from app.database import get_db
from app.dependencies import get_family_member, get_admin_member
from app.models.chore import ChoreTask, ChoreTemplate, TaskStatus
from app.models.family import FamilyMember
from app.schemas.chore import (
    DelegateRequest, HistoryOut, TaskComplete, TaskCreate, TaskOut,
    TemplateCreate, TemplatePatch, TemplateOut,
)
from app.services.chore import calc_score, complete_task

router = APIRouter(prefix="/api/families/{family_id}", tags=["tasks"])


# ── Templates ─────────────────────────────────────────────────────────────────

@router.get("/templates", response_model=list[TemplateOut])
def list_templates(
    family_id: int,
    include_marketplace: bool = False,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    q = db.query(ChoreTemplate).filter(
        ChoreTemplate.family_id == family_id,
        ChoreTemplate.is_active.is_(True),
    )
    if not include_marketplace:
        q = q.filter(ChoreTemplate.is_marketplace.is_(False))
    return q.all()


@router.post("/templates", response_model=TemplateOut, status_code=201)
def create_template(
    family_id: int,
    body: TemplateCreate,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    tmpl = ChoreTemplate(
        family_id=family_id,
        created_by=member.id,
        **body.model_dump(),
    )
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(
    family_id: int,
    template_id: int,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    tmpl = db.get(ChoreTemplate, template_id)
    if not tmpl or tmpl.family_id != family_id:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없음")
    tmpl.is_active = False
    db.commit()


@router.patch("/templates/{template_id}", response_model=TemplateOut)
def patch_template(
    family_id: int,
    template_id: int,
    body: TemplatePatch,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """임포트된 템플릿 반복주기/담당자/귀가연동 수정"""
    tmpl = db.get(ChoreTemplate, template_id)
    if not tmpl or tmpl.family_id != family_id or not tmpl.is_active:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없음")
    patch_data = body.model_dump(exclude_unset=True)
    for k, v in patch_data.items():
        setattr(tmpl, k, v)
    db.commit()
    db.refresh(tmpl)
    return tmpl


# ── Tasks ─────────────────────────────────────────────────────────────────────

@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    family_id: int,
    task_status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[date] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    q = db.query(ChoreTask).filter(ChoreTask.family_id == family_id)
    if task_status:
        q = q.filter(ChoreTask.status == task_status)
    if assigned_to:
        q = q.filter(ChoreTask.assigned_to == assigned_to)
    if due_date:
        q = q.filter(ChoreTask.due_date == due_date)
    return q.order_by(ChoreTask.due_date.asc().nulls_last(), ChoreTask.id.desc()).all()


@router.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(
    family_id: int,
    body: TaskCreate,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    score = calc_score(body.estimated_minutes, body.intensity)
    task = ChoreTask(
        family_id=family_id,
        created_by=member.id,
        score=score,
        **body.model_dump(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/tasks/{task_id}/complete", response_model=HistoryOut)
def complete_task_endpoint(
    family_id: int,
    task_id: int,
    body: TaskComplete,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없음")
    history = complete_task(task, member, db, note=body.note, sim_date=getattr(body, 'sim_date', None))
    db.commit()
    db.refresh(history)

    # Phase 8-4: 완료 칭찬 TTS (fire-and-forget)
    try:
        import asyncio, random
        from app.models.family import Family
        family = db.get(Family, family_id)
        if family and family.tts_player:
            PRAISE = [
                "{name}님, {task} 완료! +{score}포인트 획득!",
                "훌륭해요! {task} 끝났어요. {name}님 최고!",
                "{task} 완료됐어요. {name}님 덕분에 집이 깨끗해지고 있어요!",
            ]
            from app.models.user import User
            user = db.get(User, member.user_id)
            name = user.name if user else "님"
            tmpl = random.choice(PRAISE)
            text = tmpl.format(name=name, task=task.name, score=history.score_earned)
            if task.intensity == "hard":
                text += " 어려운 할일인데 정말 잘하셨어요!"
            from app.services.ha_notify import ha_tts
            asyncio.create_task(ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or ""))
    except Exception:
        pass

    return history


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    family_id: int,
    task_id: int,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없음")
    db.delete(task)
    db.commit()


# ── Delegation ────────────────────────────────────────────────────────────────

@router.post("/tasks/{task_id}/delegate", response_model=TaskOut)
def delegate_task(
    family_id: int,
    task_id: int,
    body: DelegateRequest,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """할일 위임 요청"""
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없음")
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="완료된 할일은 위임할 수 없습니다")

    # 위임 대상 유효성 확인
    target = db.get(FamilyMember, body.delegated_to)
    if not target or target.family_id != family_id:
        raise HTTPException(status_code=404, detail="위임 대상 구성원을 찾을 수 없음")

    task.delegated_to = body.delegated_to
    task.delegation_note = body.note
    task.delegation_status = "requested"
    db.commit()
    db.refresh(task)

    # SSE 알림
    try:
        from app.services.sse import broadcast
        broadcast(family_id, "task_delegated", {
            "task_id": task_id,
            "task_name": task.name,
            "from_member": member.id,
            "to_member": body.delegated_to,
        })
    except Exception:
        pass

    # TTS 알림 (대상자에게)
    try:
        import asyncio
        from app.models.family import Family
        from app.models.user import User
        family = db.get(Family, family_id)
        if family and family.tts_player:
            from_user = db.get(User, member.user_id)
            from_name = from_user.name if from_user else "누군가"
            text = f"{from_name}님이 {task.name} 할일을 부탁했어요!"
            from app.services.ha_notify import ha_tts
            asyncio.create_task(ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or ""))
    except Exception:
        pass

    return task


@router.post("/tasks/{task_id}/delegate/accept", response_model=TaskOut)
def accept_delegation(
    family_id: int,
    task_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """위임 수락 — 담당자를 본인으로 변경"""
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없음")
    if task.delegation_status != "requested":
        raise HTTPException(status_code=400, detail="위임 요청 상태가 아닙니다")
    if task.delegated_to != member.id:
        raise HTTPException(status_code=403, detail="본인에게 위임된 할일이 아닙니다")

    task.assigned_to = member.id
    task.delegation_status = "accepted"
    db.commit()
    db.refresh(task)

    try:
        from app.services.sse import broadcast
        broadcast(family_id, "delegation_accepted", {"task_id": task_id, "task_name": task.name, "member_id": member.id})
    except Exception:
        pass

    return task


@router.post("/tasks/{task_id}/delegate/reject", response_model=TaskOut)
def reject_delegation(
    family_id: int,
    task_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """위임 거절"""
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(status_code=404, detail="할일을 찾을 수 없음")
    if task.delegation_status != "requested":
        raise HTTPException(status_code=400, detail="위임 요청 상태가 아닙니다")
    if task.delegated_to != member.id:
        raise HTTPException(status_code=403, detail="본인에게 위임된 할일이 아닙니다")

    task.delegation_status = "rejected"
    db.commit()
    db.refresh(task)

    try:
        from app.services.sse import broadcast
        broadcast(family_id, "delegation_rejected", {"task_id": task_id, "task_name": task.name, "member_id": member.id})
    except Exception:
        pass

    return task


# ── Photo Upload ──────────────────────────────────────────────────────────────

@router.post("/tasks/{task_id}/photo")
async def upload_photo(
    family_id: int,
    task_id: int,
    file: UploadFile = File(...),
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    task = db.get(ChoreTask, task_id)
    if not task or task.family_id != family_id:
        raise HTTPException(404, "할일을 찾을 수 없음")

    upload_dir = f"app/static/uploads/{family_id}"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    if not ext:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{upload_dir}/{filename}"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    task.photo_url = f"/static/uploads/{family_id}/{filename}"
    db.commit()
    return {"photo_url": task.photo_url}


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[HistoryOut])
def list_history(
    family_id: int,
    page: int = 1,
    limit: int = 20,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    from app.models.chore import CompletionHistory as CH
    offset = (page - 1) * limit
    return (
        db.query(CH)
        .join(ChoreTask, CH.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id)
        .order_by(CH.completed_at.desc())
        .offset(offset).limit(limit).all()
    )


@router.get("/members/{member_id}/history", response_model=list[HistoryOut])
def member_history(
    family_id: int,
    member_id: int,
    page: int = 1,
    limit: int = 20,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    from app.models.chore import CompletionHistory as CH
    offset = (page - 1) * limit
    return (
        db.query(CH)
        .join(ChoreTask, CH.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id, CH.completed_by == member_id)
        .order_by(CH.completed_at.desc())
        .offset(offset).limit(limit).all()
    )


# ── TTS ───────────────────────────────────────────────────────────────────────

@router.post("/tts", status_code=200)
async def tts_announce(
    family_id: int,
    body: dict,
    member: FamilyMember = Depends(get_family_member),
):
    from app.services.ha_notify import ha_tts
    text = body.get("text", "")
    if not text:
        raise HTTPException(400, "text 필드가 필요합니다")
    media_player = body.get("media_player", "")
    tts_engine = body.get("tts_engine", "")
    success = await ha_tts(text, media_player=media_player, tts_engine=tts_engine)
    return {"success": success}
