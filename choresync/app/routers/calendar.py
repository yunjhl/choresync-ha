"""달력 API — 할일 날짜별 조회 + 일정 변경"""
import calendar as cal_lib
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_family_member
from app.models.chore import ChoreTask, ChoreTemplate, INTENSITY_MULTIPLIER, TaskStatus
from app.models.family import FamilyMember
from app.models.user import User

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

CATEGORY_COLORS = {
    "주방": "#f97316", "청소": "#06b6d4", "세탁": "#8b5cf6",
    "장보기": "#10b981", "요리": "#ef4444", "아이돌봄": "#f59e0b",
    "기타": "#6b7280",
}


def _recurrence_dates(tmpl: ChoreTemplate, first_day: date, last_day: date) -> list:
    """반복 템플릿에서 해당 월에 해당하는 날짜 목록 생성"""
    dates = []
    interval = tmpl.recurrence_interval
    rec_day = tmpl.recurrence_day  # weekly: 0=월~6=일, monthly: 1~31

    if interval == "daily":
        d = first_day
        while d <= last_day:
            dates.append(d)
            d += timedelta(days=1)
    elif interval in ("weekly", "biweekly"):
        step = 7 if interval == "weekly" else 14
        if rec_day is not None:
            # rec_day 요일의 첫 날부터 step씩
            d = first_day
            while d.weekday() != rec_day and d <= last_day:
                d += timedelta(days=1)
            while d <= last_day:
                dates.append(d)
                d += timedelta(days=step)
        else:
            d = first_day
            while d <= last_day:
                dates.append(d)
                d += timedelta(days=step)
    elif interval == "monthly":
        day_of_month = rec_day or 1
        try:
            vdate = date(first_day.year, first_day.month, day_of_month)
            if first_day <= vdate <= last_day:
                dates.append(vdate)
        except ValueError:
            pass  # 해당 월에 없는 날짜 (e.g. 2월 31일)
    return dates


@router.get("/events")
def get_calendar_events(
    family_id: int,
    year: int,
    month: int,
    member_id: Optional[int] = None,
    category: Optional[str] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """월별 할일 목록 (달력 이벤트 형식) — 실제 Task + 반복 템플릿 가상 이벤트 포함"""
    first_day = date(year, month, 1)
    last_day = date(year, month, cal_lib.monthrange(year, month)[1])

    # ── 1. 실제 ChoreTask 인스턴스 조회 ──
    query = db.query(ChoreTask).filter(
        ChoreTask.family_id == family_id,
        ChoreTask.due_date >= first_day,
        ChoreTask.due_date <= last_day,
        ChoreTask.calendar_visibility.is_(True),
    )
    if member_id:
        query = query.filter(ChoreTask.assigned_to == member_id)
    if category:
        query = query.filter(ChoreTask.category == category)

    tasks = query.order_by(ChoreTask.due_date).all()

    # 중복 방지용: (template_id, due_date) 쌍
    existing_pairs = {(t.template_id, t.due_date) for t in tasks if t.template_id}

    def _assignee_name(assigned_to_id):
        if not assigned_to_id:
            return ""
        m = db.get(FamilyMember, assigned_to_id)
        if not m:
            return ""
        u = db.get(User, m.user_id)
        return u.name if u else ""

    events = []
    for t in tasks:
        color = t.color_tag or CATEGORY_COLORS.get(t.category, "#6b7280")
        events.append({
            "id": t.id,
            "title": t.name,
            "start": str(t.due_date),
            "end": str(t.due_date),
            "color": color,
            "status": t.status.value,
            "category": t.category,
            "assignee": _assignee_name(t.assigned_to),
            "score": t.score,
            "is_virtual": False,
        })

    # ── 2. 반복 템플릿 → 가상 이벤트 생성 ──
    templates = db.query(ChoreTemplate).filter(
        ChoreTemplate.family_id == family_id,
        ChoreTemplate.is_active.is_(True),
        ChoreTemplate.recurrence_interval.isnot(None),
    ).all()

    for tmpl in templates:
        if member_id and tmpl.assigned_to != member_id:
            continue
        if category and tmpl.category != category:
            continue

        color = CATEGORY_COLORS.get(tmpl.category, "#6b7280")
        mult = INTENSITY_MULTIPLIER.get(tmpl.intensity, 1.5)
        score = round(tmpl.estimated_minutes / 5 * mult, 1)
        aname = _assignee_name(tmpl.assigned_to)

        for vdate in _recurrence_dates(tmpl, first_day, last_day):
            if (tmpl.id, vdate) in existing_pairs:
                continue  # 이미 실제 Task 있음
            events.append({
                "id": f"tmpl-{tmpl.id}-{vdate}",
                "title": tmpl.name,
                "start": str(vdate),
                "end": str(vdate),
                "color": color,
                "status": "Pending",
                "category": tmpl.category,
                "assignee": aname,
                "score": score,
                "is_virtual": True,
                "template_id": tmpl.id,
            })

    return sorted(events, key=lambda e: e["start"])


@router.get("/events/{event_date}")
def get_day_tasks(
    family_id: int,
    event_date: date,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """특정 날짜 할일 목록 (사이드패널용) — 실제 Task + 반복 템플릿 가상 이벤트 포함"""
    tasks = db.query(ChoreTask).filter(
        ChoreTask.family_id == family_id,
        ChoreTask.due_date == event_date,
    ).order_by(ChoreTask.status).all()

    existing_template_ids = {t.template_id for t in tasks if t.template_id}

    def _assignee_name(assigned_to_id):
        if not assigned_to_id:
            return ""
        m = db.get(FamilyMember, assigned_to_id)
        if not m:
            return ""
        u = db.get(User, m.user_id)
        return u.name if u else ""

    result = []
    for t in tasks:
        result.append({
            "id": t.id, "name": t.name, "category": t.category,
            "status": t.status.value, "score": t.score,
            "assignee": _assignee_name(t.assigned_to), "note": t.note,
            "color": t.color_tag or CATEGORY_COLORS.get(t.category, "#6b7280"),
            "is_virtual": False,
        })

    # 반복 템플릿에서 해당 날짜에 맞는 가상 이벤트 추가
    templates = db.query(ChoreTemplate).filter(
        ChoreTemplate.family_id == family_id,
        ChoreTemplate.is_active.is_(True),
        ChoreTemplate.recurrence_interval.isnot(None),
    ).all()
    for tmpl in templates:
        if tmpl.id in existing_template_ids:
            continue
        # 이 날짜가 반복 패턴에 맞는지 확인
        interval = tmpl.recurrence_interval
        rec_day = tmpl.recurrence_day
        matches = False
        if interval == "daily":
            matches = True
        elif interval in ("weekly", "biweekly"):
            if rec_day is not None:
                matches = (event_date.weekday() == rec_day)
            else:
                matches = True
        elif interval == "monthly":
            day_of_month = rec_day or 1
            matches = (event_date.day == day_of_month)
        if not matches:
            continue
        mult = INTENSITY_MULTIPLIER.get(tmpl.intensity, 1.5)
        result.append({
            "id": f"tmpl-{tmpl.id}-{event_date}",
            "name": tmpl.name, "category": tmpl.category,
            "status": "Pending",
            "score": round(tmpl.estimated_minutes / 5 * mult, 1),
            "assignee": _assignee_name(tmpl.assigned_to), "note": None,
            "color": CATEGORY_COLORS.get(tmpl.category, "#6b7280"),
            "is_virtual": True, "template_id": tmpl.id,
        })
    return result


@router.post("/events/{task_id}/reschedule")
def reschedule_task(
    family_id: int,
    task_id: int,
    new_due_date: date,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """할일 날짜 변경"""
    task = db.query(ChoreTask).filter(
        ChoreTask.id == task_id, ChoreTask.family_id == family_id
    ).first()
    if not task:
        raise HTTPException(404, "할일을 찾을 수 없습니다")
    task.due_date = new_due_date
    db.commit()
    return {"id": task.id, "new_due_date": str(new_due_date)}


@router.get("/month-summary")
def month_summary(
    family_id: int,
    year: int,
    month: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """월별 통계 요약 (달력 헤더용)"""
    first_day = date(year, month, 1)
    last_day = date(year, month, cal_lib.monthrange(year, month)[1])
    tasks = db.query(ChoreTask).filter(
        ChoreTask.family_id == family_id,
        ChoreTask.due_date >= first_day,
        ChoreTask.due_date <= last_day,
    ).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    return {
        "year": year, "month": month, "total": total,
        "completed": completed, "pending": total - completed,
        "completion_rate": round(completed / total * 100, 1) if total else 0,
    }

