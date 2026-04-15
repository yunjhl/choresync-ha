"""웹 푸시 알림 라우터 — VAPID + subscription 관리"""
import json
import os
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_current_user

router = APIRouter(prefix="/api/notify", tags=["notify"])
logger = logging.getLogger(__name__)

# VAPID 키 및 subscription 저장 경로
_DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
_VAPID_FILE = _DATA_DIR / "vapid_keys.json"
_SUBS_FILE = _DATA_DIR / "push_subscriptions.json"


def _load_vapid_keys():
    if _VAPID_FILE.exists():
        return json.loads(_VAPID_FILE.read_text())
    return None


def _get_vapid_public_key() -> str | None:
    keys = _load_vapid_keys()
    return keys.get("public_key") if keys else None


def _load_subscriptions() -> list:
    if _SUBS_FILE.exists():
        try:
            return json.loads(_SUBS_FILE.read_text())
        except Exception:
            return []
    return []


def _save_subscriptions(subs: list):
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _SUBS_FILE.write_text(json.dumps(subs))


class PushSubscription(BaseModel):
    endpoint: str
    keys: dict


@router.get("/vapid-key")
async def get_vapid_public_key():
    """VAPID 공개 키 반환 (서비스 워커 구독용)"""
    try:
        from py_vapid import Vapid
        keys = _load_vapid_keys()
        if not keys:
            # 키 생성
            vapid = Vapid()
            vapid.generate_keys()
            _DATA_DIR.mkdir(parents=True, exist_ok=True)
            public_key = vapid.public_key.public_bytes(
                __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding", "PublicFormat"]).Encoding.X962,
                __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding", "PublicFormat"]).PublicFormat.UncompressedPoint,
            )
            import base64
            pub_b64 = base64.urlsafe_b64encode(public_key).rstrip(b"=").decode()
            private_pem = vapid.private_key.private_bytes(
                __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding", "PrivateFormat", "NoEncryption"]).Encoding.PEM,
                __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding", "PrivateFormat", "NoEncryption"]).PrivateFormat.TraditionalOpenSSL,
                __import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding", "PrivateFormat", "NoEncryption"]).NoEncryption(),
            ).decode()
            keys = {"public_key": pub_b64, "private_pem": private_pem}
            _VAPID_FILE.write_text(json.dumps(keys))
        return {"public_key": keys["public_key"]}
    except ImportError:
        raise HTTPException(501, "pywebpush 라이브러리가 설치되어 있지 않습니다")
    except Exception as e:
        logger.warning("VAPID key generation failed: %s", e)
        raise HTTPException(500, str(e))


@router.post("/subscribe")
async def subscribe(sub: PushSubscription, current_user=Depends(get_current_user)):
    """푸시 구독 저장"""
    subs = _load_subscriptions()
    # 중복 제거
    subs = [s for s in subs if s.get("endpoint") != sub.endpoint]
    subs.append({"endpoint": sub.endpoint, "keys": sub.keys, "user_id": current_user.id})
    _save_subscriptions(subs)
    return {"status": "subscribed"}


@router.delete("/subscribe")
async def unsubscribe(sub: PushSubscription, current_user=Depends(get_current_user)):
    """푸시 구독 삭제"""
    subs = _load_subscriptions()
    subs = [s for s in subs if s.get("endpoint") != sub.endpoint]
    _save_subscriptions(subs)
    return {"status": "unsubscribed"}


async def send_push_to_all(message: str, title: str = "ChoreSync", url: str = "/"):
    """모든 구독자에게 웹 푸시 발송"""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.debug("pywebpush not installed, skipping web push")
        return
    keys = _load_vapid_keys()
    if not keys:
        return
    subs = _load_subscriptions()
    if not subs:
        return
    payload = json.dumps({"title": title, "body": message, "url": url})
    dead_endpoints = []
    for sub in subs:
        try:
            webpush(
                subscription_info={"endpoint": sub["endpoint"], "keys": sub["keys"]},
                data=payload,
                vapid_private_key=keys["private_pem"],
                vapid_claims={"sub": "mailto:choresync@home.local"},
            )
        except Exception as e:
            logger.debug("Push send failed for %s: %s", sub["endpoint"][:50], e)
            if "410" in str(e) or "404" in str(e):
                dead_endpoints.append(sub["endpoint"])
    if dead_endpoints:
        subs = [s for s in subs if s["endpoint"] not in dead_endpoints]
        _save_subscriptions(subs)
