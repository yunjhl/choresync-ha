"""Quest / Wish CRUD + 상태 전이 라우터"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_member, get_family_member
from app.models.family import Family, FamilyMember
from app.models.quest import Quest, Wish, WishStatus
from app.models.wish_vote import WishVote
from app.schemas.quest import QuestCreate, QuestOut, WishCreate, WishOut, WishVoteCreate, WishVoteOut
from app.services.quest import accept_quest, cancel_quest, confirm_quest, submit_quest
from app.services.wish import cancel_wish, fulfill_wish, get_family_total_score

router = APIRouter(prefix="/api", tags=["quests"])


# ── Quests ────────────────────────────────────────────────────────────────────

@router.get("/families/{family_id}/quests", response_model=list[QuestOut])
def list_quests(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    return db.query(Quest).filter(Quest.family_id == family_id).order_by(Quest.created_at.desc()).all()


@router.post("/families/{family_id}/quests", response_model=QuestOut, status_code=201)
def create_quest(
    family_id: int,
    body: QuestCreate,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    quest = Quest(family_id=family_id, created_by=member.id, **body.model_dump())
    db.add(quest)
    db.commit()
    db.refresh(quest)
    return quest


@router.post("/quests/{quest_id}/accept", response_model=QuestOut)
def quest_accept(
    quest_id: int,
    member: FamilyMember = Depends(get_family_member.__wrapped__ if hasattr(get_family_member, "__wrapped__") else get_family_member),
    db: Session = Depends(get_db),
):
    quest = db.get(Quest, quest_id)
    if not quest:
        raise HTTPException(404, "퀘스트를 찾을 수 없음")
    return quest


@router.post("/families/{family_id}/quests/{quest_id}/accept", response_model=QuestOut)
def quest_accept_v2(
    family_id: int,
    quest_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    quest = _get_quest(quest_id, family_id, db)
    result = accept_quest(quest, member, db)
    db.commit()
    db.refresh(result)
    return result


@router.post("/families/{family_id}/quests/{quest_id}/complete", response_model=QuestOut)
def quest_complete(
    family_id: int,
    quest_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    quest = _get_quest(quest_id, family_id, db)
    result = submit_quest(quest, member, db)
    db.commit()
    db.refresh(result)
    return result


@router.post("/families/{family_id}/quests/{quest_id}/confirm", response_model=QuestOut)
def quest_confirm(
    family_id: int,
    quest_id: int,
    member: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    quest = _get_quest(quest_id, family_id, db)
    result = confirm_quest(quest, member, db)
    db.commit()
    db.refresh(result)
    return result


@router.post("/families/{family_id}/quests/{quest_id}/cancel", response_model=QuestOut)
def quest_cancel(
    family_id: int,
    quest_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    quest = _get_quest(quest_id, family_id, db)
    result = cancel_quest(quest, member, db)
    db.commit()
    db.refresh(result)
    return result


# ── Wishes ────────────────────────────────────────────────────────────────────

def _enrich_wish(wish: Wish, current_member_id: int, db: Session) -> dict:
    """Wish 객체에 투표 통계를 추가해서 반환"""
    votes = db.query(WishVote).filter(WishVote.wish_id == wish.id).all()
    approve_count = sum(1 for v in votes if v.approved)
    reject_count = sum(1 for v in votes if not v.approved)
    my_vote_obj = next((v for v in votes if v.member_id == current_member_id), None)
    return {
        **{c.name: getattr(wish, c.name) for c in wish.__table__.columns},
        "vote_count": len(votes),
        "approve_count": approve_count,
        "reject_count": reject_count,
        "my_vote": my_vote_obj.approved if my_vote_obj else None,
    }


@router.get("/families/{family_id}/wishes", response_model=list[WishOut])
def list_wishes(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    wishes = db.query(Wish).filter(Wish.family_id == family_id).order_by(Wish.created_at.desc()).all()
    return [_enrich_wish(w, member.id, db) for w in wishes]


@router.post("/families/{family_id}/wishes", response_model=WishOut, status_code=201)
def create_wish(
    family_id: int,
    body: WishCreate,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    wish = Wish(family_id=family_id, requested_by=member.id, **body.model_dump())
    db.add(wish)
    db.commit()
    db.refresh(wish)
    return _enrich_wish(wish, member.id, db)


@router.post("/families/{family_id}/wishes/{wish_id}/vote", response_model=WishOut)
def wish_vote(
    family_id: int,
    wish_id: int,
    body: WishVoteCreate,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    """가족 투표 — 과반수 승인 시 Approved, 과반수 거절 시 Rejected"""
    wish = _get_wish(wish_id, family_id, db)
    if wish.status not in (WishStatus.PENDING,):
        raise HTTPException(400, f"투표 불가 상태: {wish.status}")

    # 기존 투표 업데이트 또는 신규 생성
    existing = db.query(WishVote).filter(
        WishVote.wish_id == wish_id,
        WishVote.member_id == member.id,
    ).first()
    if existing:
        existing.approved = body.approved
        existing.comment = body.comment
        existing.voted_at = datetime.now(timezone.utc)
    else:
        vote = WishVote(
            wish_id=wish_id,
            member_id=member.id,
            approved=body.approved,
            comment=body.comment,
        )
        db.add(vote)
    db.flush()

    # 과반수 집계
    family = db.get(Family, family_id)
    total_members = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
    ).count()
    votes = db.query(WishVote).filter(WishVote.wish_id == wish_id).all()
    approve_count = sum(1 for v in votes if v.approved)
    reject_count = sum(1 for v in votes if not v.approved)
    majority = (total_members // 2) + 1

    if approve_count >= majority:
        wish.status = WishStatus.APPROVED
        wish.approved_by = member.id
    elif reject_count >= majority:
        wish.status = WishStatus.REJECTED

    db.commit()
    db.refresh(wish)
    return _enrich_wish(wish, member.id, db)


@router.get("/families/{family_id}/wishes/{wish_id}/votes", response_model=list[WishVoteOut])
def wish_votes(
    family_id: int,
    wish_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    wish = _get_wish(wish_id, family_id, db)
    return db.query(WishVote).filter(WishVote.wish_id == wish_id).all()


@router.post("/families/{family_id}/wishes/{wish_id}/fulfill", response_model=WishOut)
def wish_fulfill(
    family_id: int,
    wish_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    wish = _get_wish(wish_id, family_id, db)
    result = fulfill_wish(wish, member, db)
    db.commit()
    db.refresh(result)
    return _enrich_wish(result, member.id, db)


@router.post("/families/{family_id}/wishes/{wish_id}/cancel", response_model=WishOut)
def wish_cancel(
    family_id: int,
    wish_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    wish = _get_wish(wish_id, family_id, db)
    result = cancel_wish(wish, member, db)
    db.commit()
    db.refresh(result)
    return _enrich_wish(result, member.id, db)


@router.get("/families/{family_id}/score", response_model=dict)
def family_score(
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    total = get_family_total_score(family_id, db)
    return {"family_id": family_id, "total_score": total}


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_quest(quest_id: int, family_id: int, db: Session) -> Quest:
    quest = db.get(Quest, quest_id)
    if not quest or quest.family_id != family_id:
        raise HTTPException(404, "퀘스트를 찾을 수 없음")
    return quest


def _get_wish(wish_id: int, family_id: int, db: Session) -> Wish:
    wish = db.get(Wish, wish_id)
    if not wish or wish.family_id != family_id:
        raise HTTPException(404, "위시를 찾을 수 없음")
    return wish
