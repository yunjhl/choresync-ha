"""SSE — asyncio Queue 기반 서버 발송 이벤트 브로드캐스트"""

import asyncio
import json
from typing import AsyncGenerator

# 가족별 구독자 큐 관리
_queues: dict[int, list[asyncio.Queue]] = {}


def subscribe(family_id: int) -> asyncio.Queue:
    """새 SSE 클라이언트를 등록하고 Queue 반환"""
    q: asyncio.Queue = asyncio.Queue(maxsize=50)
    _queues.setdefault(family_id, []).append(q)
    return q


def unsubscribe(family_id: int, q: asyncio.Queue) -> None:
    queues = _queues.get(family_id, [])
    if q in queues:
        queues.remove(q)


def broadcast(family_id: int, event_type: str, data: dict) -> None:
    """모든 구독자에게 이벤트 발송 (동기 컨텍스트에서 호출 가능)"""
    payload = json.dumps({"type": event_type, **data})
    for q in list(_queues.get(family_id, [])):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass  # 느린 클라이언트 드랍


async def event_generator(family_id: int) -> AsyncGenerator[str, None]:
    """SSE 스트림 비동기 제너레이터"""
    q = subscribe(family_id)
    try:
        # 연결 확인 이벤트
        yield f"event: connected\ndata: {{\"family_id\": {family_id}}}\n\n"
        while True:
            try:
                payload = await asyncio.wait_for(q.get(), timeout=30.0)
                yield f"data: {payload}\n\n"
            except asyncio.TimeoutError:
                yield "event: heartbeat\ndata: {}\n\n"  # keepalive
    finally:
        unsubscribe(family_id, q)
