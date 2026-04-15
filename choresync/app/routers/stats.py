"""통계 API — 가족/개인 점수, 히트맵, 랭킹"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_family_member
from app.models.chore import CompletionHistory, ChoreTask
from app.models.family import FamilyMember
from app.models.quest import Quest, QuestStatus
from app.models.user import User
from app.services.wish import get_member_score

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/families/{family_id}/stats")
def family_stats(
    family_id: int,
    days: int = 30,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()

    member_stats = []
    for m in members:
        user = db.get(User, m.user_id)
        task_completions = (
            db.query(func.count(CompletionHistory.id), func.sum(CompletionHistory.score_earned))
            .filter(CompletionHistory.completed_by == m.id, CompletionHistory.completed_at >= since)
            .first()
        )
        quest_completions = (
            db.query(func.count(Quest.id), func.sum(Quest.reward_points))
            .filter(Quest.accepted_by == m.id, Quest.status == QuestStatus.COMPLETED, Quest.completed_at >= since)
            .first()
        )
        member_stats.append({
            "member_id": m.id,
            "name": user.name if user else str(m.id),
            "task_count": task_completions[0] or 0,
            "task_score": round(float(task_completions[1] or 0), 2),
            "quest_count": quest_completions[0] or 0,
            "quest_score": round(float(quest_completions[1] or 0), 2),
            "total_score": get_member_score(m, db),
        })

    daily_raw = (
        db.query(
            func.date(CompletionHistory.completed_at).label("day"),
            func.count(CompletionHistory.id).label("count"),
            func.sum(CompletionHistory.score_earned).label("score"),
        )
        .join(ChoreTask, CompletionHistory.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since)
        .group_by(func.date(CompletionHistory.completed_at))
        .order_by(func.date(CompletionHistory.completed_at))
        .all()
    )
    daily_trend = [
        {"day": str(row.day), "count": row.count, "score": round(float(row.score or 0), 2)}
        for row in daily_raw
    ]
    return {"family_id": family_id, "period_days": days, "members": member_stats, "daily_trend": daily_trend}


@router.get("/families/{family_id}/stats/heatmap")
def family_heatmap(
    family_id: int,
    year: Optional[int] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """365일 일별 완료 히트맵 데이터"""
    if year is None:
        year = datetime.now(timezone.utc).year
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)

    rows = (
        db.query(
            func.date(CompletionHistory.completed_at).label("day"),
            func.count(CompletionHistory.id).label("count"),
        )
        .join(ChoreTask, CompletionHistory.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= start, CompletionHistory.completed_at <= end)
        .group_by(func.date(CompletionHistory.completed_at))
        .all()
    )
    data = {str(row.day): row.count for row in rows}
    return {"year": year, "data": data}


@router.get("/families/{family_id}/stats/ranking")
def family_ranking(
    family_id: int,
    period: str = "weekly",
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """주간/월간 구성원 랭킹"""
    now = datetime.now(timezone.utc)
    if period == "weekly":
        since = now - timedelta(days=now.weekday())
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # monthly
        since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    ranking = []
    for m in members:
        user = db.get(User, m.user_id)
        result = (
            db.query(func.count(CompletionHistory.id), func.sum(CompletionHistory.score_earned))
            .filter(CompletionHistory.completed_by == m.id, CompletionHistory.completed_at >= since)
            .first()
        )
        ranking.append({
            "member_id": m.id,
            "name": user.name if user else str(m.id),
            "count": result[0] or 0,
            "score": round(float(result[1] or 0), 2),
        })
    ranking.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(ranking):
        r["rank"] = i + 1
    return {"period": period, "since": since.isoformat(), "ranking": ranking}


@router.get("/families/{family_id}/stats/category")
def family_category_stats(
    family_id: int,
    days: int = 30,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """카테고리별 완료 통계"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(ChoreTask.category, func.count(CompletionHistory.id).label("count"), func.sum(CompletionHistory.score_earned).label("score"))
        .join(CompletionHistory, CompletionHistory.task_id == ChoreTask.id)
        .filter(ChoreTask.family_id == family_id, CompletionHistory.completed_at >= since)
        .group_by(ChoreTask.category)
        .order_by(func.count(CompletionHistory.id).desc())
        .all()
    )
    return [
        {"category": row.category or "기타", "count": row.count, "score": round(float(row.score or 0), 2)}
        for row in rows
    ]


# ─────────────────────────────────────────────
# Phase 7 신규 통계 엔드포인트
# ─────────────────────────────────────────────
from app.services.stats_service import (
    compute_heatmap, compute_weekly_chart, compute_category_breakdown,
    compute_family_ranking, get_user_balance,
)


@router.get("/stats/heatmap")
def heatmap(
    family_id: int,
    user_id: Optional[int] = None,
    year: Optional[int] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    if year is None:
        from datetime import datetime as _dt
        year = _dt.now().year
    uid = user_id if user_id is not None else member.user_id
    return {"year": year, "data": compute_heatmap(uid, family_id, year, db)}


@router.get("/stats/weekly-chart")
def weekly_chart(
    family_id: int,
    user_id: Optional[int] = None,
    weeks: int = 8,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    uid = user_id if user_id is not None else member.user_id
    return compute_weekly_chart(uid, family_id, weeks, db)


@router.get("/stats/category-breakdown")
def category_breakdown(
    family_id: int,
    user_id: Optional[int] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    uid = user_id if user_id is not None else member.user_id
    return compute_category_breakdown(uid, family_id, db)


@router.get("/stats/family-ranking")
def family_ranking(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    return compute_family_ranking(family_id, db)


@router.get("/stats/balance")
def user_balance(
    family_id: int,
    user_id: Optional[int] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    uid = user_id if user_id is not None else member.user_id
    return {"user_id": uid, "balance": get_user_balance(uid, family_id, db)}
