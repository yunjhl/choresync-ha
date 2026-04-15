"""HA 알림 서비스 — notify / TTS / webhook (SUPERVISOR_TOKEN 우선 지원)"""
import os
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# 한글 지원 엔진 우선 — google_translate_en_com은 영어 전용이므로 최후 수단
TTS_ENGINE_PRIORITY = ["tts.google_translate_ko_com", "tts.google_ai_tts", "tts.google_cloud", "tts.cloud", "tts.google_translate_en_com"]


def _get_ha_config():
    """SUPERVISOR_TOKEN 우선, 없으면 ha_url/ha_token 폴백"""
    sup_token = os.environ.get("SUPERVISOR_TOKEN")
    if sup_token:
        return "http://supervisor/core/api", sup_token
    if settings.ha_url and settings.ha_token:
        return settings.ha_url.rstrip("/") + "/api", settings.ha_token
    return None, None


async def _find_tts_engine(base: str, token: str, preferred: str = "") -> str:
    """사용 가능한 TTS 엔진 엔티티 반환 (preferred 있으면 priority list 앞에 삽입)"""
    priority = ([preferred] if preferred and preferred.startswith("tts.") else []) + TTS_ENGINE_PRIORITY
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{base}/states",
                headers={"Authorization": f"Bearer {token}"},
            )
            if r.status_code == 200:
                entities = r.json()
                tts_entities = [e["entity_id"] for e in entities if e["entity_id"].startswith("tts.")]
                for candidate in priority:
                    if candidate in tts_entities:
                        return candidate
                if tts_entities:
                    return tts_entities[0]
    except Exception:
        pass
    return preferred if preferred and preferred.startswith("tts.") else "tts.google_translate_en_com"


async def _find_media_player(base, token):
    """사용 가능한 media_player 자동 탐색"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base}/states", headers={"Authorization": f"Bearer {token}"})
            if r.status_code == 200:
                for e in r.json():
                    eid2 = e.get("entity_id", "")
                    st2 = e.get("state", "")
                    if eid2.startswith("media_player.") and st2 not in ("unavailable", "unknown", "off"):
                        return eid2
    except Exception:
        pass
    return ""

async def ha_notify(message: str, title: str = "ChoreSync") -> bool:
    """HA persistent_notification.create 서비스 호출"""
    base, token = _get_ha_config()
    if not base:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{base}/services/persistent_notification/create",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"title": title, "message": message, "notification_id": "choresync"},
            )
            return r.status_code == 200
    except Exception as e:
        logger.warning("HA notify failed: %s", e)
        return False


async def ha_tts(text: str, media_player: str = "", tts_engine: str = "") -> bool:
    """HA TTS 서비스 호출 — tts/speak API 사용"""
    base, token = _get_ha_config()
    if not base:
        logger.info("HA TTS: 연결 설정 없음 (SUPERVISOR_TOKEN 또는 ha_url/ha_token 필요)")
        return False

    # 스피커 (media_player) — ha_tts_entity는 TTS 엔진용이므로 폴백으로 쓰지 않음
    target = media_player
    if not target:
        target = await _find_media_player(base, token)
    if not target:
        logger.warning("HA TTS: no media_player available")
        return False
    # TTS 엔진 자동 탐지 (preferred가 있어도 priority list 통해 검증)
    engine = await _find_tts_engine(base, token, preferred=tts_engine)

    # 엔진별 language 파라미터 — google_ai_tts는 ko-KR, 나머지는 ko
    # google_ai_tts: ko-KR / google_translate_ko_com & others: ko
    lang = "ko-KR" if "google_ai" in engine else "ko"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{base}/services/tts/speak",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "entity_id": engine,
                    "media_player_entity_id": target,
                    "message": text,
                    "cache": False,
                    "language": lang,
                },
            )
            if r.status_code == 200:
                logger.info("HA TTS 발화 성공: engine=%s target=%s text=%s", engine, target, text[:50])
                return True
            logger.warning("HA TTS 응답 오류: %s %s", r.status_code, r.text[:200])
            return False
    except Exception as e:
        logger.warning("HA TTS failed: %s", e)
        return False


async def ha_webhook(data: dict) -> bool:
    """HA 자동화 웹훅 트리거"""
    base, token = _get_ha_config()
    if not base or not settings.ha_webhook_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{base}/webhook/{settings.ha_webhook_id}",
                json=data,
            )
            return r.status_code in (200, 201, 204)
    except Exception as e:
        logger.warning("HA webhook failed: %s", e)
        return False
async def ha_mobile_push(notify_entity: str, message: str, title: str = "ChoreSync", url: str = "/") -> bool:
    """HA 모바일 앱 푸시 알림 (notify.mobile_app_xxx 서비스 호출)"""
    base, token = _get_ha_config()
    if not base or not notify_entity:
        return False
    if not notify_entity.startswith("notify."):
        notify_entity = f"notify.{notify_entity}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{base}/services/{notify_entity.replace('.', '/', 1)}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"message": message, "title": title, "data": {"url": url, "push": {"sound": "default"}}},
            )
            if r.status_code == 200:
                logger.info("HA mobile push 성공: entity=%s msg=%s", notify_entity, message[:50])
                return True
            logger.warning("HA mobile push 오류: %s %s", r.status_code, r.text[:200])
            return False
    except Exception as e:
        logger.warning("HA mobile push failed: %s", e)
        return False


async def ha_get_notify_entities() -> list[str]:
    """HA에서 notify.mobile_app_* 엔티티 목록 반환"""
    base, token = _get_ha_config()
    if not base:
        return []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{base}/services",
                headers={"Authorization": f"Bearer {token}"},
            )
            if r.status_code == 200:
                services = r.json()
                notify_entities = []
                for svc in services:
                    if svc.get("domain") == "notify":
                        for svc_name in svc.get("services", {}).keys():
                            if svc_name.startswith("mobile_app"):
                                notify_entities.append(f"notify.{svc_name}")
                return notify_entities
    except Exception as e:
        logger.warning("HA notify entities fetch failed: %s", e)
    return []
