"""LLM 챗봇 서비스 — Ollama API 연동"""
import re
import random
import logging
import httpx
from datetime import date

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """너는 가족 집안일 관리 어시스턴트 ChoreSync야.
반드시 한국어로만 대답하고, TTS용이므로 50자 이내로 짧고 친근하게 답해.

처리할 수 있는 명령:
- "X 완료"/"X 끝났어" → 할일 X를 완료 처리하겠다고 답해
- "X 추가해줘" → 할일 X를 추가하겠다고 답해
- "오늘 할일"/"할일 목록" → 오늘 할일 목록을 읽어줘
- "점수"/"포인트" → 가족 점수 현황 알려줘
- 칭찬 요청 → 격려 메시지 답해

컨텍스트: {context}"""

INTENT_PATTERNS = [
    ("complete", re.compile(r"(.+?)\s*(완료|끝났|했어|했다|마쳤|다했)", re.I)),
    ("add", re.compile(r"(.+?)\s*(추가|만들어|넣어|등록)", re.I)),
    ("list", re.compile(r"(오늘|할일|뭐가|무엇|목록)", re.I)),
    ("score", re.compile(r"(점수|포인트|얼마|순위)", re.I)),
]


def detect_intent(message: str) -> tuple[str, str]:
    """메시지에서 인텐트와 대상 추출"""
    for intent, pattern in INTENT_PATTERNS:
        m = pattern.search(message)
        if m:
            target = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else ""
            return intent, target
    return "chat", ""


def _rule_based_response(intent: str, target: str, context: dict) -> str:
    """LLM 없이 인텐트 기반 규칙 응답"""
    tasks = context.get("tasks", [])
    family_name = context.get("family_name", "우리 가족")

    if intent == "list":
        if tasks:
            names = [t["name"] for t in tasks[:4]]
            return f"오늘 할일은 {', '.join(names)} 입니다!"
        return "오늘은 등록된 할일이 없어요! 좋은 하루 되세요 😊"
    elif intent == "complete" and target:
        return f"'{target}' 완료 처리할게요! 수고하셨어요 👍"
    elif intent == "add" and target:
        return f"'{target}' 할일에 추가할게요!"
    elif intent == "score":
        return f"{family_name} 점수는 통계 페이지에서 확인해보세요!"
    else:
        return random.choice([
            "안녕하세요! 무엇을 도와드릴까요?",
            "오늘도 화이팅! 할일 있으면 말씀해주세요 😊",
            "네, 말씀하세요!",
        ])


async def chat(
    message: str,
    context: dict,
    tts_target: str = "",
    tts_engine: str = "",
) -> dict:
    """LLM 호출 → 응답 반환. LLM 실패 시 rule-based fallback"""
    intent, target = detect_intent(message)

    text = None

    if settings.llm_url:
        tasks_str = ", ".join([t["name"] for t in context.get("tasks", [])[:10]]) or "없음"
        ctx_str = (
            f"가족: {context.get('family_name', '우리 가족')}, "
            f"오늘({date.today().strftime('%m/%d')}) 할일: {tasks_str}, "
            f"구성원: {', '.join(context.get('members', []))}"
        )
        system = SYSTEM_PROMPT.format(context=ctx_str)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ]
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                r = await client.post(
                    settings.llm_url.rstrip("/") + "/api/chat",
                    json={"model": settings.llm_model, "messages": messages, "stream": False},
                )
                if r.status_code == 200:
                    text = r.json().get("message", {}).get("content", "").strip() or None
                else:
                    logger.warning("LLM error %s: %s", r.status_code, r.text[:200])
        except Exception as e:
            logger.warning("LLM call failed: %s", e)

    # fallback
    if not text:
        text = _rule_based_response(intent, target, context)

    if tts_target and text:
        try:
            from app.services.ha_notify import ha_tts
            await ha_tts(text, media_player=tts_target, tts_engine=tts_engine)
        except Exception as e:
            logger.warning("TTS failed: %s", e)

    return {"text": text, "intent": intent, "target": target}


async def health() -> dict:
    """LLM 서버 연결 상태 확인"""
    if not settings.llm_url:
        return {"status": "disabled", "model": None}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(settings.llm_url.rstrip("/") + "/api/tags")
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                active = settings.llm_model in models
                return {"status": "ok" if active else "model_missing", "model": settings.llm_model, "available": models[:5]}
    except Exception:
        pass
    return {"status": "unreachable", "model": settings.llm_model}


# ── Phase 10-1: 자연어 날짜/담당자 파싱 ──────────────────────────────────────

import re
from datetime import date, timedelta


def parse_date_from_text(text: str, today: date) -> date | None:
    """텍스트에서 날짜 표현을 파싱한다."""
    text = text.replace(" ", "")

    # N일 후
    m = re.search(r"(\d+)일후", text)
    if m:
        return today + timedelta(days=int(m.group(1)))

    # 내일
    if "내일" in text:
        return today + timedelta(days=1)

    # 모레
    if "모레" in text:
        return today + timedelta(days=2)

    # 다음 주 요일
    KO_DAYS = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
    m = re.search(r"다음\s*주\s*([월화수목금토일])", text)
    if m:
        target_wd = KO_DAYS[m.group(1)]
        days_ahead = (target_wd - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead + 7)

    # 이번 주 요일 / 요일만
    m = re.search(r"([월화수목금토일])요일", text) or re.search(r"([월화수목금토일])\b", text)
    if m:
        target_wd = KO_DAYS.get(m.group(1))
        if target_wd is not None:
            days_ahead = (target_wd - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)

    # N월 N일
    m = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)
    if m:
        try:
            return date(today.year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass

    return None


def parse_assignee_from_text(text: str, members: list, db) -> int | None:
    """텍스트에서 담당자를 찾아 FamilyMember.id를 반환한다."""
    from app.models.user import User
    for member in members:
        user = db.get(User, member.user_id)
        if user and user.name and user.name in text:
            return member.id
        # 역할 이름 (아빠, 엄마, 남편, 아내 등)
        role_aliases = {
            "남편": ["아빠", "남편"],
            "아내": ["엄마", "아내", "와이프"],
        }
        if member.role:
            for aliases in role_aliases.values():
                if member.role in aliases:
                    for alias in aliases:
                        if alias in text:
                            return member.id
    return None
