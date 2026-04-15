"""Quest 상태머신 서비스"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.family import FamilyMember, MemberRole
from app.models.quest import Quest, QuestStatus


def _check_family(quest: Quest, member: FamilyMember):
    if quest.family_id != member.family_id:
        raise HTTPException(403, "다른 가족의 퀘스트입니다")


def accept_quest(quest: Quest, member: FamilyMember, db: Session) -> Quest:
    _check_family(quest, member)
    if quest.status != QuestStatus.OPEN:
        raise HTTPException(409, f"퀘스트 상태가 {quest.status.value}이라 수락할 수 없습니다")
    quest.status = QuestStatus.ACCEPTED
    quest.accepted_by = member.id
    db.flush()
    return quest


def submit_quest(quest: Quest, member: FamilyMember, db: Session) -> Quest:
    """수행자가 완료 요청 (PendingConfirm)"""
    _check_family(quest, member)
    if quest.status != QuestStatus.ACCEPTED:
        raise HTTPException(409, f"퀘스트 상태가 {quest.status.value}이라 완료 요청을 할 수 없습니다")
    if quest.accepted_by != member.id:
        raise HTTPException(403, "퀘스트를 수락한 구성원만 완료 요청할 수 있습니다")
    quest.status = QuestStatus.PENDING_CONFIRM
    db.flush()
    return quest


def confirm_quest(quest: Quest, member: FamilyMember, db: Session) -> Quest:
    """Admin이 완료 확인"""
    _check_family(quest, member)
    if quest.status != QuestStatus.PENDING_CONFIRM:
        raise HTTPException(409, f"퀘스트 상태가 {quest.status.value}이라 확인할 수 없습니다")
    if member.role != MemberRole.ADMIN:
        raise HTTPException(403, "Admin만 퀘스트 완료를 확인할 수 있습니다")
    quest.status = QuestStatus.COMPLETED
    quest.confirmed_by = member.id
    quest.completed_at = datetime.now(timezone.utc)
    db.flush()
    return quest


def cancel_quest(quest: Quest, member: FamilyMember, db: Session) -> Quest:
    _check_family(quest, member)
    if quest.status in (QuestStatus.COMPLETED, QuestStatus.CANCELLED):
        raise HTTPException(409, "이미 완료되었거나 취소된 퀘스트입니다")
    if member.role != MemberRole.ADMIN and quest.created_by != member.id:
        raise HTTPException(403, "Admin 또는 퀘스트 생성자만 취소할 수 있습니다")
    quest.status = QuestStatus.CANCELLED
    db.flush()
    return quest
