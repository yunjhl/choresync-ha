"""가족/구성원/초대 API"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_member, get_current_user, get_family_member
from app.models.family import FamilyMember, Invitation, InvitationStatus, MemberRole
from app.models.user import User
from app.schemas.family import (
    CreateInvitationRequest,
    FamilyResponse,
    InvitationResponse,
    MemberResponse,
    UpdateMemberRequest,
)

router = APIRouter(prefix="/api", tags=["families"])

# ─── 가족 TTS/브리핑 설정 ───


@router.get("/families/{family_id}/settings")
def get_family_settings(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """가족 TTS/브리핑 설정 조회"""
    from app.models.family import Family
    family = db.get(Family, family_id)
    if not family:
        raise HTTPException(404, "가족을 찾을 수 없음")
    return {
        "tts_player": family.tts_player,
        "tts_engine": family.tts_engine,
        "briefing_hour": family.briefing_hour,
        "briefing_enabled": family.briefing_enabled,
    }


@router.patch("/families/{family_id}/settings")
def update_family_settings(
    family_id: int,
    req: dict,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    """가족 TTS/브리핑 설정 저장 (Admin만)"""
    from app.models.family import Family
    family = db.get(Family, family_id)
    if not family:
        raise HTTPException(404, "가족을 찾을 수 없음")

    if "tts_player" in req:
        family.tts_player = req["tts_player"] or None
    if "tts_engine" in req:
        family.tts_engine = req["tts_engine"] or None
    if "briefing_hour" in req and req["briefing_hour"] is not None:
        h = int(req["briefing_hour"])
        if 0 <= h <= 23:
            family.briefing_hour = h
    if "briefing_enabled" in req and req["briefing_enabled"] is not None:
        family.briefing_enabled = bool(req["briefing_enabled"])

    db.commit()
    db.refresh(family)

    # 스케줄러 잡 재등록
    try:
        from app.services.scheduler import reschedule_briefing
        reschedule_briefing(family)
    except Exception:
        pass

    return {
        "tts_player": family.tts_player,
        "tts_engine": family.tts_engine,
        "briefing_hour": family.briefing_hour,
        "briefing_enabled": family.briefing_enabled,
    }


@router.post("/families/{family_id}/briefing/trigger")
async def trigger_briefing(
    family_id: int,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    """아침 브리핑 TTS를 즉시 발화 (테스트용, Admin만)"""
    from app.models.family import Family
    family = db.get(Family, family_id)
    if not family:
        raise HTTPException(404, "가족을 찾을 수 없음")
    if not family.tts_player:
        raise HTTPException(400, "TTS 스피커가 설정되지 않음")
    import asyncio
    from app.services.scheduler import _async_briefing
    asyncio.create_task(_async_briefing(family_id))
    return {"message": "브리핑 실행 요청됨"}


@router.get("/families", response_model=list[FamilyResponse])
def list_families(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내가 속한 가족 목록"""
    memberships = db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).all()
    return [m.family for m in memberships]


@router.get("/families/{family_id}/my-member")
def get_my_member(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
):
    """현재 로그인 유저의 가족 멤버 ID 반환"""
    return {"id": member.id, "role": member.role, "user_id": member.user_id}


@router.get("/families/{family_id}/members", response_model=list[MemberResponse])
def list_members(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """가족 구성원 목록"""
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    result = []
    for m in members:
        user = db.get(User, m.user_id)
        result.append(
            MemberResponse(
                id=m.id,
                user_id=m.user_id,
                family_id=m.family_id,
                name=user.name if user else "",
                email=user.email if user else "",
                role=m.role.value,
                family_role=m.family_role,
                age=m.age,
                joined_at=m.joined_at,
            )
        )
    return result


@router.patch("/members/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    req: UpdateMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """구성원 정보 수정"""
    target = db.get(FamilyMember, member_id)
    if not target:
        raise HTTPException(status_code=404, detail="구성원을 찾을 수 없음")

    # 본인이거나 Admin만 수정 가능
    caller = (
        db.query(FamilyMember)
        .filter(FamilyMember.user_id == current_user.id, FamilyMember.family_id == target.family_id)
        .first()
    )
    if not caller:
        raise HTTPException(status_code=403, detail="이 가족의 구성원이 아닙니다")

    is_self = caller.id == target.id
    is_admin = caller.role == MemberRole.ADMIN

    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    if req.family_role is not None:
        target.family_role = req.family_role
    if req.age is not None:
        target.age = req.age
    if req.role is not None and is_admin:
        target.role = MemberRole(req.role)

    db.commit()
    db.refresh(target)

    user = db.get(User, target.user_id)
    return MemberResponse(
        id=target.id,
        user_id=target.user_id,
        family_id=target.family_id,
        name=user.name if user else "",
        email=user.email if user else "",
        role=target.role.value,
        family_role=target.family_role,
        age=target.age,
        joined_at=target.joined_at,
    )


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """구성원 삭제 (Admin만)"""
    target = db.get(FamilyMember, member_id)
    if not target:
        raise HTTPException(status_code=404, detail="구성원을 찾을 수 없음")

    admin = get_admin_member(target.family_id, current_user, db)

    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="자기 자신을 삭제할 수 없습니다")

    db.delete(target)
    db.commit()


# ─── 초대 ───


@router.get("/families/{family_id}/invitations", response_model=list[InvitationResponse])
def list_invitations(
    family_id: int,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    return (
        db.query(Invitation)
        .filter(Invitation.family_id == family_id)
        .order_by(Invitation.created_at.desc())
        .all()
    )


@router.post(
    "/families/{family_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    family_id: int,
    req: CreateInvitationRequest,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    invitation = Invitation(
        family_id=family_id,
        invited_by=admin.id,
        invited_email=getattr(req, 'invited_email', None),
        expires_at=datetime.now(timezone.utc) + timedelta(days=req.expires_days),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


@router.delete(
    "/families/{family_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_invitation(
    family_id: int,
    invitation_id: int,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    invitation = db.get(Invitation, invitation_id)
    if not invitation or invitation.family_id != family_id:
        raise HTTPException(status_code=404, detail="초대를 찾을 수 없음")
    db.delete(invitation)
    db.commit()


# ─── 초대 코드 직접 합류 ───


@router.get("/families/invite/{code}")
def get_invite_info(code: str, db: Session = Depends(get_db)):
    """초대 코드 정보 조회 (인증 불필요)"""
    from app.models.family import Family

    family = db.query(Family).filter(Family.invite_code == code).first()
    if not family:
        raise HTTPException(404, "유효하지 않은 초대 코드")

    member_count = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).count()
    return {"family_id": family.id, "family_name": family.name, "member_count": member_count}


@router.post("/families/join/{code}")
def join_by_invite_code(
    code: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """초대 코드로 가족 합류"""
    from app.models.family import Family

    family = db.query(Family).filter(Family.invite_code == code).first()
    if not family:
        raise HTTPException(404, "유효하지 않은 초대 코드")

    existing = (
        db.query(FamilyMember)
        .filter(
            FamilyMember.user_id == current_user.id,
            FamilyMember.family_id == family.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(409, "이미 이 가족의 구성원입니다")

    member = FamilyMember(
        user_id=current_user.id,
        family_id=family.id,
        role=MemberRole.MEMBER,
        family_role=body.get("family_role", "기타"),
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"message": "합류 완료", "family_id": family.id}


# ─── 템플릿 팩 재시드 ───


@router.post("/families/{family_id}/templates/seed-pack")
def seed_template_pack(
    family_id: int,
    body: dict,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    from app.seed_templates import VALID_PACKS, reseed_templates

    pack = body.get("pack", "공통")
    if pack not in VALID_PACKS:
        from fastapi import HTTPException
        raise HTTPException(400, f"유효하지 않은 팩: {pack}. 가능: {VALID_PACKS}")

    count = reseed_templates(family_id, admin.id, db, pack=pack)
    return {"message": f"{pack} 팩으로 {count}개 템플릿 시드 완료", "count": count, "pack": pack}


# ─── 가족 레벨 시스템 (Phase 9-2) ───

FAMILY_LEVELS = [
    (0,     1, "새내기 가족"),
    (500,   2, "알콩달콩"),
    (1500,  3, "호흡 맞추는 중"),
    (3000,  4, "팀워크 UP"),
    (5000,  5, "드림팀 가족"),
    (8000,  6, "집안일 고수"),
    (12000, 7, "청소 마스터"),
    (16000, 8, "완벽한 가정"),
    (20000, 9, "전설의 가족"),
    (30000, 10, "레전드 가족"),
]

def _calc_level(total_score: float):
    level, name = 1, "새내기 가족"
    for threshold, lv, nm in FAMILY_LEVELS:
        if total_score >= threshold:
            level, name = lv, nm
        else:
            break
    # next level
    next_threshold = None
    for threshold, lv, nm in FAMILY_LEVELS:
        if threshold > total_score:
            next_threshold = threshold
            break
    progress = 0
    if next_threshold:
        prev = max(t for t, _, _ in FAMILY_LEVELS if t <= total_score)
        span = next_threshold - prev
        progress = int((total_score - prev) / span * 100) if span > 0 else 100
    else:
        progress = 100
    return level, name, next_threshold, progress


@router.get("/families/{family_id}/level")
def get_family_level(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """가족 레벨 및 누적 점수 조회"""
    from sqlalchemy import func
    from app.models.chore import CompletionHistory, ChoreTask
    total = db.query(func.sum(CompletionHistory.score_earned)).join(
        ChoreTask, CompletionHistory.task_id == ChoreTask.id
    ).filter(ChoreTask.family_id == family_id).scalar() or 0
    total = float(total)
    level, name, next_score, progress = _calc_level(total)
    return {
        "level": level,
        "level_name": name,
        "total_score": round(total, 1),
        "next_level_score": next_score,
        "progress_pct": progress,
    }


# ─── 주간 리포트 (Phase 10-3) ───

@router.get("/families/{family_id}/weekly-report")
def get_weekly_report(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """이번 주(최근 7일) 가족 완료 요약 조회"""
    from datetime import timedelta
    from sqlalchemy import func
    from app.models.chore import CompletionHistory, ChoreTask
    from app.models.family import Family

    family = db.get(Family, family_id)
    since = datetime.now(timezone.utc) - timedelta(days=7)

    # 전체 완료 건수 + 점수
    total_count = db.query(func.count(CompletionHistory.id)).join(
        ChoreTask, CompletionHistory.task_id == ChoreTask.id
    ).filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since).scalar() or 0

    total_score = db.query(func.sum(CompletionHistory.score_earned)).join(
        ChoreTask, CompletionHistory.task_id == ChoreTask.id
    ).filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since).scalar() or 0

    # 구성원별 완료 수
    rows = db.query(
        CompletionHistory.completed_by, func.count(CompletionHistory.id).label("cnt")
    ).join(ChoreTask, CompletionHistory.task_id == ChoreTask.id).filter(
        ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since
    ).group_by(CompletionHistory.completed_by).all()

    # MVP 찾기
    mvp_name = None
    if rows:
        mvp_mid = max(rows, key=lambda r: r.cnt).completed_by
        mvp_member = db.get(FamilyMember, mvp_mid)
        if mvp_member:
            user = db.get(User, mvp_member.user_id)
            if user:
                mvp_name = user.name

    # 이번 주 태스크 목표 (이번 주 생성된 것)
    week_tasks = db.query(func.count(ChoreTask.id)).filter(
        ChoreTask.family_id == family_id,
        ChoreTask.due_date >= (datetime.now(timezone.utc) - timedelta(days=7)).date(),
    ).scalar() or 0
    achievement_pct = round(total_count / week_tasks * 100) if week_tasks > 0 else 0

    return {
        "family_name": family.name if family else "",
        "total_count": total_count,
        "total_score": round(float(total_score), 1),
        "achievement_pct": achievement_pct,
        "mvp_name": mvp_name,
        "week_tasks": week_tasks,
    }


# ─── 반복 패턴 감지 제안 (Phase 10-2) ───

KO_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


@router.get("/families/{family_id}/suggestions")
def get_pattern_suggestions(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """지난 4주 완료 이력을 분석해 반복 패턴 제안 목록을 반환한다."""
    from datetime import timedelta
    from sqlalchemy import func
    from app.models.chore import CompletionHistory, ChoreTask, ChoreTemplate

    since = datetime.now(timezone.utc) - timedelta(weeks=4)
    histories = (
        db.query(CompletionHistory, ChoreTask)
        .join(ChoreTask, CompletionHistory.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since)
        .all()
    )

    # 할일 이름 + 요일 → 완료 횟수
    from collections import defaultdict
    pattern: dict[tuple, int] = defaultdict(int)
    for hist, task in histories:
        wd = hist.completed_at.weekday()
        pattern[(task.name, wd)] += 1

    # 기존 recurring 템플릿 이름 수집 (중복 제안 방지)
    existing = {
        t.name for t in db.query(ChoreTemplate).filter(
            ChoreTemplate.family_id == family_id,
            ChoreTemplate.recurrence_interval.isnot(None),
        ).all()
    }

    suggestions = []
    for (name, wd), count in pattern.items():
        if count >= 3 and name not in existing:
            suggestions.append({
                "id": f"{name}_{wd}",
                "task_name": name,
                "weekday": wd,
                "weekday_ko": KO_WEEKDAYS[wd],
                "count": count,
                "message": f"매주 {KO_WEEKDAYS[wd]}요일 {name}을(를) 하시네요. 정기 할일로 등록할까요?",
            })

    suggestions.sort(key=lambda x: -x["count"])
    return {"suggestions": suggestions[:10]}


@router.post("/families/{family_id}/suggestions/accept")
def accept_pattern_suggestion(
    family_id: int,
    req: dict,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    """패턴 제안을 수락해 주간 반복 템플릿으로 등록한다."""
    from app.models.chore import ChoreTemplate, IntensityLevel
    task_name = req.get("task_name")
    weekday = req.get("weekday")
    if not task_name or weekday is None:
        raise HTTPException(400, "task_name과 weekday 필요")

    # 이미 있으면 스킵
    from app.models.chore import ChoreTemplate
    exists = db.query(ChoreTemplate).filter(
        ChoreTemplate.family_id == family_id,
        ChoreTemplate.name == task_name,
        ChoreTemplate.recurrence_interval == "weekly",
    ).first()
    if exists:
        return {"message": "이미 등록된 반복 템플릿", "template_id": exists.id}

    tmpl = ChoreTemplate(
        family_id=family_id,
        name=task_name,
        category="기타",
        estimated_minutes=30,
        intensity=IntensityLevel.NORMAL,
        recurrence_interval="weekly",
        recurrence_day=weekday,
        created_by=admin.id,
        is_active=True,
    )
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return {"message": f"'{task_name}' 주간 반복 템플릿 등록 완료", "template_id": tmpl.id}


@router.get("/families/{family_id}/templates/packs")
def list_template_packs(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
):
    from app.seed_templates import VALID_PACKS, FAMILY_PACKS

    return {
        "packs": [
            {"name": p, "template_count": len(FAMILY_PACKS[p])}
            for p in VALID_PACKS
        ]
    }

