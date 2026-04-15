"""할일 비즈니스 로직 — 점수 계산 + 완료 처리 + 레벨업 감지"""

from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chore import (
    ChoreTask,
    CompletionHistory,
    IntensityLevel,
    INTENSITY_MULTIPLIER,
    TaskStatus,
)
from app.models.family import FamilyMember

# 가족 레벨 테이블 (families.py와 동일하게 유지)
FAMILY_LEVELS = [
    (1, "새내기 가족", 0),
    (2, "알콩달콩", 500),
    (3, "호흡 맞추는 중", 1500),
    (4, "척척 가족", 3000),
    (5, "드림팀 가족", 5000),
    (6, "집안일 고수", 8000),
    (7, "깔끔 마스터", 12000),
    (8, "슈퍼 가족", 17000),
    (9, "레전드 예비", 22000),
    (10, "레전드 가족", 28000),
]


def _get_level(total_score: float) -> int:
    lvl = 1
    for lv, _, threshold in FAMILY_LEVELS:
        if total_score >= threshold:
            lvl = lv
    return lvl


def calc_score(estimated_minutes: int, intensity: IntensityLevel) -> float:
    """점수 = (estimated_minutes / 5) × intensity_multiplier"""
    return round((estimated_minutes / 5) * INTENSITY_MULTIPLIER[intensity], 2)


def complete_task(
    task: ChoreTask,
    member: FamilyMember,
    db: Session,
    note: str | None = None,
    sim_date: str | None = None,
) -> CompletionHistory:
    """할일을 완료 처리하고 CompletionHistory를 반환한다."""
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 완료된 할일입니다"
        )
    if task.family_id != member.family_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="다른 가족의 할일입니다"
        )

    score = calc_score(task.estimated_minutes, task.intensity)
    task.status = TaskStatus.COMPLETED
    task.score = score

    if sim_date:
        import random as _random
        from datetime import date as _date
        _d = _date.fromisoformat(sim_date)
        _completed_at = datetime(_d.year, _d.month, _d.day,
                                 _random.randint(8, 22), _random.randint(0, 59),
                                 tzinfo=timezone.utc)
    else:
        _completed_at = datetime.now(timezone.utc)

    history = CompletionHistory(
        task_id=task.id,
        completed_by=member.id,
        score_earned=score,
        completed_at=_completed_at,
        note=note,
    )
    db.add(history)
    db.flush()

    # HA webhook trigger (fire-and-forget)
    import asyncio
    from app.services.ha_notify import ha_webhook
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(ha_webhook({
                "event": "task_completed",
                "task_name": task.name,
                "family_id": task.family_id,
                "score": score,
            }))
    except Exception:
        pass

    # Phase 7: 배지 평가 + SSE 알림
    try:
        from app.services.badge_service import evaluate_on_completion
        newly_earned = evaluate_on_completion(
            user_id=member.user_id,
            family_id=member.family_id,
            completion_date=_date.fromisoformat(sim_date) if sim_date else date.today(),
            db=db,
        )
        if newly_earned:
            from app.services.sse import broadcast
            for badge in newly_earned:
                broadcast(member.family_id, "badge_earned", {
                    "badge": badge,
                    "member_id": member.id,
                })
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Badge evaluation failed: %s", e)

    # Phase 9-2: 레벨업 감지 → SSE + TTS
    try:
        from sqlalchemy import func
        from app.models.chore import CompletionHistory as CH
        from app.models.family import Family

        # 완료 직전 총점 (현재 history는 아직 commit 전이므로 score 빼고 계산)
        prev_total = db.query(func.sum(CH.score_earned)).join(
            ChoreTask, CH.task_id == ChoreTask.id
        ).filter(ChoreTask.family_id == member.family_id).scalar() or 0
        prev_total = float(prev_total) - score  # history flush됐으므로 빼서 이전 값 계산
        new_total = float(prev_total) + score

        old_level = _get_level(prev_total)
        new_level = _get_level(new_total)

        if new_level > old_level:
            level_name = next((n for lv, n, _ in FAMILY_LEVELS if lv == new_level), "")
            from app.services.sse import broadcast
            broadcast(member.family_id, "family_levelup", {
                "level": new_level,
                "level_name": level_name,
                "total_score": new_total,
            })
            # TTS 축하 메시지
            family = db.get(Family, member.family_id)
            if family and family.tts_player:
                text = f"축하해요! {family.name}이 레벨 {new_level} {level_name}이 됐어요!"
                try:
                    from app.services.ha_notify import ha_tts
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(
                            ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or "")
                        )
                except Exception:
                    pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Level-up check failed: %s", e)

    return history
