"""Wish 서비스 — 포인트 연동 자동 unlock 체크"""

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chore import CompletionHistory
from app.models.family import FamilyMember, MemberRole
from app.models.quest import Quest, QuestStatus, Wish, WishStatus


def get_member_score(member: FamilyMember, db: Session) -> float:
    """구성원의 총 획득 점수 (완료한 할일 + 퀘스트 보상)"""
    task_score = (
        db.query(func.sum(CompletionHistory.score_earned))
        .filter(CompletionHistory.completed_by == member.id)
        .scalar()
    ) or 0.0

    quest_score = (
        db.query(func.sum(Quest.reward_points))
        .filter(
            Quest.accepted_by == member.id,
            Quest.status == QuestStatus.COMPLETED,
        )
        .scalar()
    ) or 0.0

    return round(task_score + quest_score, 2)


def get_family_total_score(family_id: int, db: Session) -> float:
    """가족 전체 점수 합산"""
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    return round(sum(get_member_score(m, db) for m in members), 2)


def approve_wish(wish: Wish, member: FamilyMember, db: Session) -> Wish:
    if wish.family_id != member.family_id:
        raise HTTPException(403, "다른 가족의 위시입니다")
    if member.role != MemberRole.ADMIN:
        raise HTTPException(403, "Admin만 위시를 승인할 수 있습니다")
    if wish.status != WishStatus.PENDING:
        raise HTTPException(409, f"위시 상태가 {wish.status.value}입니다")
    wish.status = WishStatus.APPROVED
    wish.approved_by = member.id
    db.flush()
    return wish


def fulfill_wish(wish: Wish, member: FamilyMember, db: Session) -> Wish:
    """가족 전체 점수가 충분하면 이행"""
    if wish.family_id != member.family_id:
        raise HTTPException(403, "다른 가족의 위시입니다")
    if wish.status != WishStatus.APPROVED:
        raise HTTPException(409, f"승인되지 않은 위시입니다 (현재: {wish.status.value})")
    total = get_family_total_score(wish.family_id, db)
    if total < wish.point_cost:
        raise HTTPException(402, f"포인트 부족: 필요 {wish.point_cost}, 현재 {total}")
    wish.status = WishStatus.FULFILLED
    wish.fulfilled_by = member.id
    wish.fulfilled_at = datetime.now(timezone.utc)
    db.flush()
    return wish


def cancel_wish(wish: Wish, member: FamilyMember, db: Session) -> Wish:
    if wish.family_id != member.family_id:
        raise HTTPException(403, "다른 가족의 위시입니다")
    if wish.status == WishStatus.FULFILLED:
        raise HTTPException(409, "이미 이행된 위시입니다")
    if member.role != MemberRole.ADMIN and wish.requested_by != member.id:
        raise HTTPException(403, "Admin 또는 위시 요청자만 취소할 수 있습니다")
    wish.status = WishStatus.CANCELLED
    db.flush()
    return wish
