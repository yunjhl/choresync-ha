"""배지/업적 서비스 — 조건 체크, 수여, 스트릭 업데이트"""
import json
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.badge import BadgeDefinition, EarnedBadge, UserStreak
from app.models.chore import CompletionHistory, ChoreTask
from app.models.family import FamilyMember
from app.models.quest import Quest, QuestStatus
from app.models.user import User


def _get_or_create_streak(user_id: int, family_id: int, db: Session) -> UserStreak:
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user_id, UserStreak.family_id == family_id
    ).first()
    if not streak:
        streak = UserStreak(user_id=user_id, family_id=family_id)
        db.add(streak)
        db.flush()
    return streak


def update_streak(member: FamilyMember, db: Session) -> UserStreak:
    """할일 완료 후 연속 달성 스트릭 업데이트"""
    streak = _get_or_create_streak(member.user_id, member.family_id, db)
    today = date.today()

    if streak.last_completion_date is None:
        streak.current_streak = 1
        streak.streak_start_date = today
    elif streak.last_completion_date == today:
        pass  # 오늘 이미 카운트
    elif streak.last_completion_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1
        streak.streak_start_date = today

    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.last_completion_date = today
    streak.updated_at = datetime.now(timezone.utc)
    db.flush()
    return streak


def _count_task_completions(user_id: int, family_id: int, db: Session) -> int:
    return (
        db.query(func.count(CompletionHistory.id))
        .join(FamilyMember, CompletionHistory.completed_by == FamilyMember.id)
        .filter(FamilyMember.user_id == user_id, FamilyMember.family_id == family_id)
        .scalar() or 0
    )


def _count_quests(user_id: int, family_id: int, db: Session) -> int:
    return (
        db.query(func.count(Quest.id))
        .join(FamilyMember, Quest.accepted_by == FamilyMember.id)
        .filter(FamilyMember.user_id == user_id, FamilyMember.family_id == family_id, Quest.status == QuestStatus.COMPLETED)
        .scalar() or 0
    )


def _get_total_score(member: FamilyMember, db: Session) -> float:
    from app.services.wish import get_member_score
    return get_member_score(member, db)


def check_and_award(member: FamilyMember, db: Session, streak: UserStreak | None = None) -> list[dict]:
    """배지 조건 확인 후 미획득 배지 수여. 새로 획득한 배지 목록 반환."""
    if streak is None:
        streak = _get_or_create_streak(member.user_id, member.family_id, db)

    already_earned = set(
        row[0] for row in
        db.query(EarnedBadge.badge_definition_id)
        .filter(EarnedBadge.user_id == member.user_id, EarnedBadge.family_id == member.family_id)
        .all()
    )

    definitions = db.query(BadgeDefinition).filter(BadgeDefinition.is_active.is_(True)).all()
    task_count = None
    quest_count = None
    total_score = None
    newly_earned = []

    for defn in definitions:
        if defn.id in already_earned:
            continue
        try:
            cond = json.loads(defn.condition_json)
        except Exception:
            continue

        earned = False
        ctype = cond.get("type")

        if ctype == "first_complete":
            if task_count is None: task_count = _count_task_completions(member.user_id, member.family_id, db)
            earned = task_count >= 1
        elif ctype == "streak":
            earned = streak.current_streak >= cond.get("days", 1)
        elif ctype == "task_count":
            if task_count is None: task_count = _count_task_completions(member.user_id, member.family_id, db)
            earned = task_count >= cond.get("threshold", 1)
        elif ctype == "score_total":
            if total_score is None: total_score = _get_total_score(member, db)
            earned = total_score >= cond.get("threshold", 0)
        elif ctype == "quest_count":
            if quest_count is None: quest_count = _count_quests(member.user_id, member.family_id, db)
            earned = quest_count >= cond.get("threshold", 1)

        if earned:
            badge = EarnedBadge(
                user_id=member.user_id,
                family_id=member.family_id,
                badge_definition_id=defn.id,
                context_json=json.dumps({"streak": streak.current_streak}),
            )
            db.add(badge)
            db.flush()
            newly_earned.append({
                "code": defn.code, "name": defn.name,
                "icon": defn.icon, "tier": defn.tier, "points_bonus": defn.points_bonus
            })

    return newly_earned
