"""배지/업적 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_family_member, get_admin_member
from app.models.badge import BadgeDefinition, EarnedBadge, UserStreak
from app.models.family import FamilyMember
from app.models.user import User
from app.services.badge_service import get_badge_progress

router = APIRouter(prefix="/api/badges", tags=["badges"])


@router.get("/definitions")
def list_badge_definitions(
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defs = db.query(BadgeDefinition).filter(
        BadgeDefinition.is_active.is_(True),
        (BadgeDefinition.family_id == family_id) | (BadgeDefinition.family_id.is_(None)),
    ).all()
    return [{"id": b.id, "code": b.code, "name": b.name, "icon": b.icon,
             "tier": b.tier, "badge_type": b.badge_type,
             "points_bonus": b.points_bonus, "description": b.description} for b in defs]


@router.get("/earned/{user_id}")
def get_earned_badges(
    user_id: int,
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earned = db.query(EarnedBadge).filter(
        EarnedBadge.user_id == user_id,
        EarnedBadge.family_id == family_id,
    ).all()
    result = []
    for eb in earned:
        bd = db.get(BadgeDefinition, eb.badge_definition_id)
        if bd:
            result.append({
                "id": eb.id, "badge_id": bd.id, "code": bd.code,
                "name": bd.name, "icon": bd.icon, "tier": bd.tier,
                "earned_at": eb.earned_at.isoformat(),
            })
    return result


@router.get("/progress/{user_id}")
def badge_progress(
    user_id: int,
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_badge_progress(user_id, family_id, db)


@router.get("/streak/{user_id}")
def get_streak(
    user_id: int,
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user_id,
        UserStreak.family_id == family_id,
    ).first()
    if not streak:
        return {"current_streak": 0, "longest_streak": 0, "last_date": None}
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "last_date": str(streak.last_completion_date) if streak.last_completion_date else None,
    }
