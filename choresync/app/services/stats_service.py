"""통계 서비스 — 히트맵/주간차트/카테고리/랭킹/잔액"""
import json
import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import SessionLocal
from app.models.chore import CompletionHistory, ChoreTask
from app.models.family import FamilyMember
from app.models.quest import Quest, QuestStatus
from app.models.reward import RewardPurchase
from app.models.stats_cache import StatsCache
from app.models.user import User

logger = logging.getLogger(__name__)


def _get_or_compute(family_id: int, user_id: int | None, stat_type: str, period_key: str,
                    db: Session, compute_fn) -> dict:
    """캐시 우선 조회 → 없으면 compute_fn 실행 후 저장"""
    cached = db.query(StatsCache).filter(
        StatsCache.family_id == family_id,
        StatsCache.user_id == user_id,
        StatsCache.stat_type == stat_type,
        StatsCache.period_key == period_key,
    ).first()
    if cached:
        try:
            return json.loads(cached.data_json)
        except Exception:
            pass
    result = compute_fn()
    upsert = cached or StatsCache(family_id=family_id, user_id=user_id, stat_type=stat_type, period_key=period_key)
    upsert.data_json = json.dumps(result)
    upsert.computed_at = datetime.now(timezone.utc)
    if not cached:
        db.add(upsert)
    db.commit()
    return result


def get_user_balance(user_id: int, family_id: int, db: Session) -> float:
    """포인트 잔액 = 완료 점수 + 퀘스트 보상 + 배지 보너스 - 상점 사용"""
    from app.models.family import FamilyMember
    member = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id, FamilyMember.family_id == family_id,
    ).first()
    if not member:
        return 0.0
    task_score = db.query(func.sum(CompletionHistory.score_earned)).filter(
        CompletionHistory.completed_by == member.id).scalar() or 0.0
    quest_score = db.query(func.sum(Quest.reward_points)).filter(
        Quest.accepted_by == member.id, Quest.status == QuestStatus.COMPLETED,
    ).scalar() or 0.0
    # 배지 보너스
    from app.models.badge import EarnedBadge, BadgeDefinition
    badge_bonus = db.query(func.sum(BadgeDefinition.points_bonus)).join(
        EarnedBadge, EarnedBadge.badge_definition_id == BadgeDefinition.id
    ).filter(EarnedBadge.user_id == user_id, EarnedBadge.family_id == family_id).scalar() or 0
    # 상점 사용 포인트 (rejected 제외)
    spent = db.query(func.sum(RewardPurchase.points_spent)).filter(
        RewardPurchase.user_id == user_id,
        RewardPurchase.family_id == family_id,
        RewardPurchase.status != "rejected",
    ).scalar() or 0
    return round(float(task_score) + float(quest_score) + float(badge_bonus) - float(spent), 2)


def compute_heatmap(user_id: int, family_id: int, year: int, db: Session) -> dict:
    """연간 완료 히트맵: {"2026-04-14": 3, ...}"""
    from app.models.family import FamilyMember
    member = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id, FamilyMember.family_id == family_id,
    ).first()
    if not member:
        return {}
    rows = db.query(
        func.date(CompletionHistory.completed_at).label("d"),
        func.count(CompletionHistory.id).label("cnt"),
    ).filter(
        CompletionHistory.completed_by == member.id,
        func.strftime("%Y", CompletionHistory.completed_at) == str(year),
    ).group_by(func.date(CompletionHistory.completed_at)).all()
    return {str(r.d): r.cnt for r in rows}


def compute_weekly_chart(user_id: int, family_id: int, weeks: int, db: Session) -> list[dict]:
    """주간 점수/횟수: [{"week":"2026-W15","score":124,"count":12}]"""
    from app.models.family import FamilyMember
    member = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id, FamilyMember.family_id == family_id,
    ).first()
    if not member:
        return []
    since = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    rows = db.query(
        func.strftime("%Y-W%W", CompletionHistory.completed_at).label("wk"),
        func.count(CompletionHistory.id).label("cnt"),
        func.sum(CompletionHistory.score_earned).label("score"),
    ).filter(
        CompletionHistory.completed_by == member.id,
        CompletionHistory.completed_at >= since,
    ).group_by(func.strftime("%Y-W%W", CompletionHistory.completed_at)).order_by("wk").all()
    return [{"week": r.wk, "count": r.cnt, "score": round(float(r.score or 0), 2)} for r in rows]


def compute_category_breakdown(user_id: int, family_id: int, db: Session) -> list[dict]:
    """카테고리별 완료 수/점수"""
    from app.models.family import FamilyMember
    member = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id, FamilyMember.family_id == family_id,
    ).first()
    if not member:
        return []
    rows = db.query(
        ChoreTask.category,
        func.count(CompletionHistory.id).label("cnt"),
        func.sum(CompletionHistory.score_earned).label("score"),
    ).join(CompletionHistory, CompletionHistory.task_id == ChoreTask.id).filter(
        CompletionHistory.completed_by == member.id,
    ).group_by(ChoreTask.category).order_by(func.count(CompletionHistory.id).desc()).all()
    total_score = sum(float(r.score or 0) for r in rows) or 1
    return [{"category": r.category, "count": r.cnt,
             "score": round(float(r.score or 0), 2),
             "pct": round(float(r.score or 0) / total_score * 100, 1)} for r in rows]


def compute_family_ranking(family_id: int, db: Session) -> list[dict]:
    """가족 구성원 랭킹 (전체 점수 기준)"""
    from app.services.wish import get_member_score
    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    result = []
    for m in members:
        user = db.get(User, m.user_id)
        score = get_member_score(m, db)
        result.append({"member_id": m.id, "user_id": m.user_id,
                       "name": user.name if user else str(m.id), "score": score})
    result.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(result):
        r["rank"] = i + 1
    return result


# ─────────────────────────────────────────────
# APScheduler 잡 — 매 시간 통계 캐시 갱신
# ─────────────────────────────────────────────
def refresh_stats_cache_sync():
    db = SessionLocal()
    try:
        from app.models.family import Family
        families = db.query(Family).all()
        now = datetime.now(timezone.utc)
        year = now.year
        for family in families:
            members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
            for m in members:
                # 잔액 캐시
                bal = get_user_balance(m.user_id, family.id, db)
                _upsert_cache(db, family.id, m.user_id, "balance", "all_time", {"balance": bal})
                # 히트맵
                hm = compute_heatmap(m.user_id, family.id, year, db)
                _upsert_cache(db, family.id, m.user_id, "heatmap", str(year), hm)
            # 가족 랭킹
            ranking = compute_family_ranking(family.id, db)
            _upsert_cache(db, family.id, None, "family_ranking", "all_time", ranking)
        db.commit()
        logger.info("Stats cache refreshed for %d families", len(families))
    except Exception as e:
        logger.error("refresh_stats_cache failed: %s", e)
        db.rollback()
    finally:
        db.close()


def _upsert_cache(db, family_id, user_id, stat_type, period_key, data):
    existing = db.query(StatsCache).filter(
        StatsCache.family_id == family_id,
        StatsCache.user_id == user_id,
        StatsCache.stat_type == stat_type,
        StatsCache.period_key == period_key,
    ).first()
    if existing:
        existing.data_json = json.dumps(data)
        existing.computed_at = datetime.now(timezone.utc)
    else:
        db.add(StatsCache(
            family_id=family_id, user_id=user_id,
            stat_type=stat_type, period_key=period_key,
            data_json=json.dumps(data),
        ))
