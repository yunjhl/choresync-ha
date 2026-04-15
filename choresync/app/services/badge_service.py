"""배지/업적 서비스 — 스트릭 갱신 + 배지 조건 평가"""
import json
import logging
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.badge import BadgeDefinition, EarnedBadge, UserStreak
from app.models.chore import CompletionHistory, ChoreTask
from app.models.quest import Quest, QuestStatus

logger = logging.getLogger(__name__)

DEFAULT_BADGES = [
    {"code":"streak_3",  "name":"3일 연속",   "badge_type":"streak",      "condition_json":'{"type":"streak","days":3}',  "tier":"bronze", "icon":"🔥", "points_bonus":5},
    {"code":"streak_7",  "name":"일주일 연속", "badge_type":"streak",      "condition_json":'{"type":"streak","days":7}',  "tier":"silver", "icon":"🔥", "points_bonus":15},
    {"code":"streak_30", "name":"한 달 연속",  "badge_type":"streak",      "condition_json":'{"type":"streak","days":30}', "tier":"gold",   "icon":"🔥", "points_bonus":50},
    {"code":"score_100",  "name":"첫 백 점",  "badge_type":"score_total", "condition_json":'{"type":"score_total","threshold":100}',  "tier":"bronze", "icon":"⭐", "points_bonus":10},
    {"code":"score_500",  "name":"500점 달성", "badge_type":"score_total", "condition_json":'{"type":"score_total","threshold":500}',  "tier":"silver", "icon":"⭐", "points_bonus":30},
    {"code":"score_1000", "name":"천 점 달성", "badge_type":"score_total", "condition_json":'{"type":"score_total","threshold":1000}', "tier":"gold",   "icon":"⭐", "points_bonus":100},
    {"code":"tasks_10",  "name":"초보 청소부", "badge_type":"task_count",  "condition_json":'{"type":"task_count","count":10}',  "tier":"bronze", "icon":"🧹", "points_bonus":5},
    {"code":"tasks_50",  "name":"베테랑",     "badge_type":"task_count",  "condition_json":'{"type":"task_count","count":50}',  "tier":"silver", "icon":"🧹", "points_bonus":20},
    {"code":"tasks_100", "name":"프로",       "badge_type":"task_count",  "condition_json":'{"type":"task_count","count":100}', "tier":"gold",   "icon":"🧹", "points_bonus":50},
    {"code":"first_quest",        "name":"첫 퀘스트",   "badge_type":"first_complete", "condition_json":'{"type":"first_quest"}',                        "tier":"bronze", "icon":"🗡️", "points_bonus":10},
    {"code":"category_kitchen_5", "name":"주방 마스터", "badge_type":"category",       "condition_json":'{"type":"category","category":"주방","count":5}',  "tier":"bronze", "icon":"🍳", "points_bonus":8},
    {"code":"category_clean_5",   "name":"청소 마스터", "badge_type":"category",       "condition_json":'{"type":"category","category":"청소","count":5}',  "tier":"bronze", "icon":"🧽", "points_bonus":8},
]


def seed_default_badges(db: Session) -> None:
    for b in DEFAULT_BADGES:
        exists = db.query(BadgeDefinition).filter(BadgeDefinition.code == b["code"]).first()
        if not exists:
            bd = BadgeDefinition(
                code=b["code"], name=b["name"], badge_type=b["badge_type"],
                condition_json=b["condition_json"], tier=b["tier"],
                icon=b["icon"], points_bonus=b["points_bonus"],
                description=None, family_id=None,
            )
            db.add(bd)
    db.commit()


def _update_streak(user_id: int, family_id: int, completion_date: date, db: Session) -> UserStreak:
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user_id, UserStreak.family_id == family_id,
    ).first()
    if not streak:
        streak = UserStreak(user_id=user_id, family_id=family_id)
        db.add(streak)
    today = completion_date
    last = streak.last_completion_date
    if last is None:
        streak.current_streak = 1
        streak.streak_start_date = today
    elif (today - last).days == 1:
        streak.current_streak += 1
    elif (today - last).days == 0:
        pass
    else:
        streak.current_streak = 1
        streak.streak_start_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.last_completion_date = today
    streak.updated_at = datetime.now(timezone.utc)
    db.flush()
    return streak


def _get_user_stats(user_id: int, family_id: int, db: Session) -> dict:
    from app.models.family import FamilyMember
    member = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id, FamilyMember.family_id == family_id,
    ).first()
    if not member:
        return {}
    task_count = db.query(func.count(CompletionHistory.id)).filter(
        CompletionHistory.completed_by == member.id).scalar() or 0
    task_score = db.query(func.sum(CompletionHistory.score_earned)).filter(
        CompletionHistory.completed_by == member.id).scalar() or 0.0
    quest_count = db.query(func.count(Quest.id)).filter(
        Quest.accepted_by == member.id, Quest.status == QuestStatus.COMPLETED,
    ).scalar() or 0
    cat_rows = db.query(ChoreTask.category, func.count(CompletionHistory.id)).join(
        CompletionHistory, CompletionHistory.task_id == ChoreTask.id
    ).filter(CompletionHistory.completed_by == member.id).group_by(ChoreTask.category).all()
    category_counts = {r[0]: r[1] for r in cat_rows}
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user_id, UserStreak.family_id == family_id,
    ).first()
    return {
        "task_count": task_count, "task_score": float(task_score),
        "quest_count": quest_count, "category_counts": category_counts,
        "current_streak": streak.current_streak if streak else 0,
    }


def _check_condition(condition: dict, stats: dict) -> bool:
    t = condition.get("type")
    if t == "streak":        return stats.get("current_streak", 0) >= condition["days"]
    elif t == "score_total": return stats.get("task_score", 0) >= condition["threshold"]
    elif t == "task_count":  return stats.get("task_count", 0) >= condition["count"]
    elif t == "first_quest": return stats.get("quest_count", 0) >= 1
    elif t == "category":    return stats.get("category_counts", {}).get(condition.get("category", ""), 0) >= condition["count"]
    return False


def evaluate_on_completion(user_id: int, family_id: int, completion_date: date, db: Session) -> list[dict]:
    _update_streak(user_id, family_id, completion_date, db)
    stats = _get_user_stats(user_id, family_id, db)
    definitions = db.query(BadgeDefinition).filter(
        BadgeDefinition.is_active.is_(True),
        (BadgeDefinition.family_id == family_id) | (BadgeDefinition.family_id.is_(None)),
    ).all()
    already_earned = {eb.badge_definition_id for eb in
                      db.query(EarnedBadge).filter(
                          EarnedBadge.user_id == user_id, EarnedBadge.family_id == family_id,
                      ).all()}
    newly_earned = []
    for bd in definitions:
        if bd.id in already_earned:
            continue
        try:
            cond = json.loads(bd.condition_json)
        except Exception:
            continue
        if _check_condition(cond, stats):
            eb = EarnedBadge(
                user_id=user_id, family_id=family_id,
                badge_definition_id=bd.id, context_json=json.dumps(stats), notified=False,
            )
            db.add(eb)
            newly_earned.append({"code": bd.code, "name": bd.name, "icon": bd.icon, "tier": bd.tier})
    db.flush()
    return newly_earned


def get_badge_progress(user_id: int, family_id: int, db: Session) -> list[dict]:
    stats = _get_user_stats(user_id, family_id, db)
    definitions = db.query(BadgeDefinition).filter(
        BadgeDefinition.is_active.is_(True),
        (BadgeDefinition.family_id == family_id) | (BadgeDefinition.family_id.is_(None)),
    ).all()
    already_earned = {eb.badge_definition_id for eb in
                      db.query(EarnedBadge).filter(
                          EarnedBadge.user_id == user_id, EarnedBadge.family_id == family_id,
                      ).all()}
    result = []
    for bd in definitions:
        try:
            cond = json.loads(bd.condition_json)
        except Exception:
            continue
        earned = bd.id in already_earned
        current, required = _get_progress_values(cond, stats)
        pct = min(100, int(current / required * 100)) if required > 0 else (100 if earned else 0)
        result.append({
            "badge_id": bd.id, "code": bd.code, "name": bd.name,
            "icon": bd.icon, "tier": bd.tier, "earned": earned,
            "current": current, "required": required, "pct": pct,
        })
    return result


def _get_progress_values(cond: dict, stats: dict) -> tuple[int, int]:
    t = cond.get("type")
    if t == "streak":        return stats.get("current_streak", 0), cond["days"]
    elif t == "score_total": return int(stats.get("task_score", 0)), cond["threshold"]
    elif t == "task_count":  return stats.get("task_count", 0), cond["count"]
    elif t == "first_quest": return min(stats.get("quest_count", 0), 1), 1
    elif t == "category":    return stats.get("category_counts", {}).get(cond.get("category", ""), 0), cond["count"]
    return 0, 1


def check_daily_streaks_sync():
    db = SessionLocal()
    try:
        from datetime import timedelta
        yesterday = date.today() - timedelta(days=1)
        streaks = db.query(UserStreak).filter(
            UserStreak.current_streak > 0,
            UserStreak.last_completion_date < yesterday,
        ).all()
        for s in streaks:
            s.current_streak = 0
        db.commit()
        if streaks:
            logger.info("Streak reset for %d users", len(streaks))
    except Exception as e:
        logger.error("check_daily_streaks failed: %s", e)
        db.rollback()
    finally:
        db.close()
