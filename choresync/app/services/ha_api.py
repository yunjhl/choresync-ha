"""HA Supervisor REST API 클라이언트"""
import os
import httpx

SUPERVISOR_URL = "http://supervisor/core/api"
_FALLBACK_URL = os.environ.get("HA_URL", "")
_FALLBACK_TOKEN = os.environ.get("HA_TOKEN", "")


def _get_config():
    token = os.environ.get("SUPERVISOR_TOKEN") or _FALLBACK_TOKEN
    base = SUPERVISOR_URL if os.environ.get("SUPERVISOR_TOKEN") else _FALLBACK_URL
    if not token or not base:
        return None, None
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, base


async def get_states():
    headers, base = _get_config()
    if not headers:
        return None, "SUPERVISOR_TOKEN 없음 (HA 애드온으로 실행 중이 아님)"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(f"{base}/states", headers=headers)
            r.raise_for_status()
            return r.json(), None
        except Exception as e:
            return None, str(e)


async def trigger_automation(automation_id: str):
    """automation.trigger 서비스 호출"""
    headers, base = _get_config()
    if not headers:
        return None, "SUPERVISOR_TOKEN 없음"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(
                f"{base}/services/automation/trigger",
                headers=headers,
                json={"entity_id": automation_id},
            )
            r.raise_for_status()
            return {"ok": True}, None
        except Exception as e:
            return None, str(e)


async def call_service(domain: str, service: str, data: dict):
    headers, base = _get_config()
    if not headers:
        return None, "SUPERVISOR_TOKEN 없음"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(
                f"{base}/services/{domain}/{service}",
                headers=headers,
                json=data,
            )
            r.raise_for_status()
            return r.json(), None
        except Exception as e:
            return None, str(e)

async def get_weather() -> dict | None:
    """HA에서 weather.* 엔티티 상태를 조회한다. 없으면 None."""
    try:
        states = await get_states()
        for s in states:
            if s.get("entity_id", "").startswith("weather."):
                return s
    except Exception:
        pass
    return None
