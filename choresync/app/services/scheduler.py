"""APScheduler — 반복 할일 자동 생성 + 주간 리포트"""
import logging
from datetime import date, datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.models.chore import ChoreTask, ChoreTemplate, TaskStatus
from app.models.family import FamilyMember
from app.config import settings

logger = logging.getLogger(__name__)

# 인터벌별 최소 일수
INTERVAL_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "every4weeks": 28,
}


def _should_create(tmpl: ChoreTemplate, today: date, last_created: date | None) -> bool:
    """오늘 이 템플릿의 할일을 생성해야 하는지 판단"""
    interval = tmpl.recurrence_interval
    if not interval:
        return False
    if last_created is None:
        return True  # 최초 생성

    delta = (today - last_created).days
    weekday = today.weekday()  # 0=월, 6=일
    dom = today.day            # 1-31

    if interval == "daily":
        return delta >= 1
    elif interval == "weekly":
        return delta >= 7 and (tmpl.recurrence_day is None or tmpl.recurrence_day == weekday)
    elif interval == "biweekly":
        return delta >= 14 and (tmpl.recurrence_day is None or tmpl.recurrence_day == weekday)
    elif interval == "every4weeks":
        return delta >= 28 and (tmpl.recurrence_day is None or tmpl.recurrence_day == weekday)
    elif interval == "monthly":
        # 매달 recurrence_day일 (없으면 첫날)
        target_day = tmpl.recurrence_day or 1
        return dom == target_day and delta >= 28
    elif interval == "quarterly":
        # 3개월마다
        target_day = tmpl.recurrence_day or 1
        return dom == target_day and delta >= 85
    elif interval == "semiannual":
        # 6개월마다
        target_day = tmpl.recurrence_day or 1
        return dom == target_day and delta >= 175
    elif interval == "annual":
        # 1년마다
        target_day = tmpl.recurrence_day or 1
        return dom == target_day and delta >= 360
    return False


def _create_recurring_tasks_sync():
    """활성화된 recurring 템플릿에서 오늘 할일을 자동 생성 (이미 있으면 스킵)"""
    db = SessionLocal()
    try:
        today = date.today()

        templates = db.query(ChoreTemplate).filter(
            ChoreTemplate.is_active.is_(True),
            ChoreTemplate.recurrence_interval.isnot(None),
        ).all()

        created = 0
        for tmpl in templates:
            # 마지막으로 생성된 날짜 조회
            last_task = db.query(ChoreTask).filter(
                ChoreTask.family_id == tmpl.family_id,
                ChoreTask.template_id == tmpl.id,
            ).order_by(ChoreTask.due_date.desc()).first()
            last_created = last_task.due_date if last_task else None

            if not _should_create(tmpl, today, last_created):
                continue

            # 오늘 이미 있으면 스킵
            exists = db.query(ChoreTask).filter(
                ChoreTask.family_id == tmpl.family_id,
                ChoreTask.template_id == tmpl.id,
                ChoreTask.due_date == today,
            ).first()
            if exists:
                continue

            creator = db.query(FamilyMember).filter(
                FamilyMember.family_id == tmpl.family_id,
            ).first()
            if not creator:
                continue

            from app.services.chore import calc_score
            score = calc_score(tmpl.estimated_minutes, tmpl.intensity)
            task = ChoreTask(
                family_id=tmpl.family_id,
                template_id=tmpl.id,
                name=tmpl.name,
                category=tmpl.category,
                estimated_minutes=tmpl.estimated_minutes,
                intensity=tmpl.intensity,
                score=score,
                due_date=today,
                status=TaskStatus.PENDING,
                created_by=creator.id,
            )
            db.add(task)
            created += 1

        db.commit()
        if created:
            logger.info("Recurring tasks created: %d", created)
    except Exception as e:
        logger.error("Recurring task creation failed: %s", e)
        db.rollback()
    finally:
        db.close()


def _weekly_report_sync():
    """주간 요약 리포트를 HA 알림으로 전송"""
    import asyncio
    from app.services.ha_notify import ha_notify, ha_tts
    db = SessionLocal()
    try:
        from datetime import timedelta
        from sqlalchemy import func
        from app.models.chore import CompletionHistory
        from app.models.family import Family

        since = datetime.now(timezone.utc) - timedelta(days=7)
        families = db.query(Family).all()
        for family in families:
            count = db.query(func.count(CompletionHistory.id)).join(
                ChoreTask, CompletionHistory.task_id == ChoreTask.id
            ).filter(
                ChoreTask.family_id == family.id,
                CompletionHistory.completed_at >= since,
            ).scalar() or 0

            total_score = db.query(func.sum(CompletionHistory.score_earned)).join(
                ChoreTask, CompletionHistory.task_id == ChoreTask.id
            ).filter(
                ChoreTask.family_id == family.id,
                CompletionHistory.completed_at >= since,
            ).scalar() or 0

            message = f"[{family.name}] 이번 주 완료: {count}개, 획득 점수: {round(float(total_score), 1)}점"
            asyncio.run(ha_notify(message, title="ChoreSync 주간 리포트"))

            # Phase 10-3: MVP 계산 + TTS + WeeklyReport DB 저장
            from sqlalchemy import func as sqlfunc
            from app.models.family import FamilyMember as FM2
            from app.models.user import User as User2
            rows = db.query(
                CompletionHistory.completed_by, sqlfunc.count(CompletionHistory.id).label("cnt")
            ).join(ChoreTask, CompletionHistory.task_id == ChoreTask.id).filter(
                ChoreTask.family_id == family.id, CompletionHistory.completed_at >= since
            ).group_by(CompletionHistory.completed_by).all()

            mvp_name = None
            if rows:
                mvp_mid = max(rows, key=lambda r: r.cnt).completed_by
                mvp_m = db.get(FM2, mvp_mid)
                if mvp_m:
                    mvp_u = db.get(User2, mvp_m.user_id)
                    if mvp_u:
                        mvp_name = mvp_u.name

            # WeeklyReport DB 저장
            from app.models.chore import WeeklyReport
            week_tasks_count = db.query(sqlfunc.count(ChoreTask.id)).filter(
                ChoreTask.family_id == family.id,
                ChoreTask.due_date >= since.date(),
            ).scalar() or 0
            pct = round(count / week_tasks_count * 100) if week_tasks_count > 0 else 0
            report = WeeklyReport(
                family_id=family.id,
                week_start=since.date(),
                total_count=count,
                total_score=round(float(total_score), 1),
                achievement_pct=pct,
                mvp_name=mvp_name,
            )
            db.add(report)
            db.flush()

            if family.tts_player and family.briefing_enabled:
                text = f"이번 주 {family.name}의 달성률은 {pct}%였어요. "
                if mvp_name:
                    text += f"MVP는 {mvp_name}님이에요! 수고하셨어요."
                asyncio.run(ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or ""))
    except Exception as e:
        logger.error("Weekly report failed: %s", e)
    finally:
        db.close()


def _deadline_alert_sync():
    """오늘 마감인 PENDING 할일을 담당자별로 TTS 알림"""
    import asyncio
    db = SessionLocal()
    try:
        from app.models.family import Family, FamilyMember
        from app.models.user import User
        from app.services.ha_notify import ha_tts
        today = date.today()
        families = db.query(Family).filter(Family.briefing_enabled.is_(True), Family.tts_player.isnot(None)).all()
        for family in families:
            tasks = db.query(ChoreTask).filter(
                ChoreTask.family_id == family.id,
                ChoreTask.due_date == today,
                ChoreTask.status == TaskStatus.PENDING,
            ).all()
            if not tasks:
                continue
            # 담당자별 그룹핑
            by_member: dict[int | None, list] = {}
            for t in tasks:
                by_member.setdefault(t.assigned_to, []).append(t)
            for member_id, mtasks in by_member.items():
                if member_id:
                    member = db.get(FamilyMember, member_id)
                    user = db.get(User, member.user_id) if member else None
                    name = user.name if user else "가족"
                else:
                    name = "가족"
                n = len(mtasks)
                names = ", ".join(t.name for t in mtasks[:3])
                extra = f" 외 {n-3}개" if n > 3 else ""
                text = f"{name}님, 오늘까지인 할일 {n}개가 있어요: {names}{extra}."
                asyncio.run(ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or ""))
    except Exception as e:
        logger.error("Deadline alert failed: %s", e)
    finally:
        db.close()


def _workload_balance_sync():
    """지난 주 부하 불균형 감지 → TTS 알림"""
    import asyncio
    from datetime import timedelta
    from sqlalchemy import func
    db = SessionLocal()
    try:
        from app.models.family import Family, FamilyMember
        from app.models.user import User
        from app.models.chore import CompletionHistory
        from app.services.ha_notify import ha_tts

        since = datetime.now(timezone.utc) - timedelta(days=7)
        families = db.query(Family).filter(
            Family.briefing_enabled.is_(True), Family.tts_player.isnot(None)
        ).all()
        for family in families:
            members = db.query(FamilyMember).filter(FamilyMember.family_id == family.id).all()
            if len(members) < 2:
                continue
            counts = {}
            for m in members:
                cnt = db.query(func.count(CompletionHistory.id)).filter(
                    CompletionHistory.completed_by == m.id,
                    CompletionHistory.completed_at >= since,
                ).scalar() or 0
                counts[m.id] = cnt
            total = sum(counts.values())
            if total == 0:
                continue
            max_id = max(counts, key=lambda k: counts[k])
            max_pct = counts[max_id] / total
            if max_pct >= 0.6:
                member = db.get(FamilyMember, max_id)
                user = db.get(User, member.user_id) if member else None
                name = user.name if user else "한 분"
                text = (f"{name}님이 지난 주 할일의 대부분을 혼자 하셨어요. "
                        "이번 주는 함께 나눠봐요!")
                asyncio.run(ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or ""))
    except Exception as e:
        logger.error("Workload balance failed: %s", e)
    finally:
        db.close()


def start_scheduler() -> AsyncIOScheduler:
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled")
        return None
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(_create_recurring_tasks_sync, CronTrigger(hour=0, minute=5))
    scheduler.add_job(_weekly_report_sync, CronTrigger(day_of_week="sun", hour=9, minute=0))

    # Phase 7: 배지 스트릭 체크 (매일 00:10)
    from app.services.badge_service import check_daily_streaks_sync
    scheduler.add_job(check_daily_streaks_sync, CronTrigger(hour=0, minute=10), id="daily_streak_check", replace_existing=True)

    # Phase 7: 통계 캐시 갱신 (매 시간)
    from app.services.stats_service import refresh_stats_cache_sync
    scheduler.add_job(refresh_stats_cache_sync, CronTrigger(minute=30), id="stats_cache_refresh", replace_existing=True, max_instances=1)

    # Phase 8-3: 마감 임박 알림 (매일 08:00)
    scheduler.add_job(_deadline_alert_sync, CronTrigger(hour=8, minute=0), id="deadline_alert", replace_existing=True)

    # Phase 9-3: 부하 균형 알림 (매주 월요일 09:00)
    scheduler.add_job(_workload_balance_sync, CronTrigger(day_of_week="mon", hour=9, minute=0), id="workload_balance", replace_existing=True)

    scheduler.start()
    logger.info("Scheduler started")

    # 앱 시작 시 즉시 오늘치 반복 할일 생성 (00:05 cron 이전에도 동작하도록)
    try:
        _create_recurring_tasks_sync()
        logger.info("Initial recurring tasks created on startup")
    except Exception as e:
        logger.warning("Startup recurring task creation failed: %s", e)


    # Phase 8: 브리핑 활성화된 가족 잡 등록
    global _scheduler
    _scheduler = scheduler
    try:
        from app.models.family import Family
        db_init = SessionLocal()
        try:
            briefing_families = db_init.query(Family).filter(Family.briefing_enabled.is_(True)).all()
            for fam in briefing_families:
                reschedule_briefing(fam)
        finally:
            db_init.close()
    except Exception as e:
        logger.warning("Briefing job init failed: %s", e)

    return scheduler


# 전역 스케줄러 참조 (reschedule_briefing에서 사용)
_scheduler: AsyncIOScheduler | None = None


def reschedule_briefing(family) -> None:
    """가족 브리핑 잡을 스케줄러에 등록/해제한다. 설정 변경 시 호출."""
    global _scheduler
    if _scheduler is None:
        return
    job_id = f"briefing_{family.id}"
    # 기존 잡 제거
    try:
        _scheduler.remove_job(job_id)
    except Exception:
        pass
    if not family.briefing_enabled or not family.tts_player:
        return
    # 새 잡 등록
    _scheduler.add_job(
        _run_briefing_for_family,
        CronTrigger(hour=family.briefing_hour, minute=0),
        id=job_id,
        args=[family.id],
        replace_existing=True,
    )
    logger.info("Briefing job scheduled: family=%d hour=%d", family.id, family.briefing_hour)


def _run_briefing_for_family(family_id: int) -> None:
    """특정 가족의 아침 브리핑 TTS를 발화한다."""
    import asyncio
    asyncio.run(_async_briefing(family_id))


async def _async_briefing(family_id: int) -> None:
    from app.services.ha_notify import ha_tts
    from app.services.ha_api import get_weather
    db = SessionLocal()
    try:
        from app.models.family import Family
        from app.models.chore import ChoreTask, TaskStatus
        from app.models.user import User
        family = db.get(Family, family_id)
        if not family or not family.briefing_enabled or not family.tts_player:
            return

        today = date.today()

        # 오늘 PENDING 할일 집계
        tasks = db.query(ChoreTask).filter(
            ChoreTask.family_id == family_id,
            ChoreTask.due_date == today,
            ChoreTask.status == TaskStatus.PENDING,
        ).all()

        # 날씨 정보
        weather_text = ""
        try:
            weather = await get_weather()
            if weather:
                state = weather.get("state", "")
                temp = weather.get("attributes", {}).get("temperature", "")
                cond_map = {
                    "sunny": "맑음", "clear-night": "맑은 밤", "cloudy": "흐림",
                    "partlycloudy": "구름 조금", "rainy": "비", "snowy": "눈",
                    "lightning": "천둥번개", "foggy": "안개",
                }
                cond = cond_map.get(state, state)
                if cond:
                    weather_text = f"오늘 날씨는 {cond}"
                    if temp:
                        weather_text += f"이고 기온은 {temp}도"
                    weather_text += "예요. "
                # 날씨별 추가 멘트
                tips = {
                    "rainy": "빨래는 실내에 건조하세요. ",
                    "snowy": "현관 정리 잊지 마세요. ",
                }
                if today.weekday() in (5, 6) and state == "sunny":
                    weather_text += "이불 빨래 하기 좋은 날이에요. "
                elif state in tips:
                    weather_text += tips[state]
        except Exception:
            pass

        # 브리핑 텍스트 조합
        n = len(tasks)
        if n == 0:
            task_text = "오늘 할일이 없어요. 푹 쉬세요!"
        elif n <= 3:
            names = ", ".join(t.name for t in tasks[:3])
            task_text = f"오늘 할일은 {n}개예요. {names}."
        else:
            names = ", ".join(t.name for t in tasks[:3])
            task_text = f"오늘 할일은 {n}개예요. {names} 외 {n-3}개."

        text = f"좋은 아침이에요! {weather_text}{family.name}의 {task_text}"
        await ha_tts(text, media_player=family.tts_player, tts_engine=family.tts_engine or "")
        logger.info("Morning briefing sent: family=%d", family_id)
    except Exception as e:
        logger.error("Briefing failed: %s", e)
    finally:
        db.close()
