"""MQTT 브로커 연동 (aiomqtt) — IoT 트리거 평가 및 할일 자동 생성"""

import asyncio
import logging
from datetime import datetime, timezone

from app.config import settings
from app.services.sse import broadcast

logger = logging.getLogger(__name__)


async def start_mqtt_listener(app) -> None:
    """FastAPI lifespan에서 백그라운드로 실행하는 MQTT 수신 루프."""
    try:
        import aiomqtt
    except ImportError:
        logger.warning("aiomqtt not installed — MQTT disabled")
        return

    broker = settings.mqtt_broker
    if not broker:
        logger.info("MQTT_BROKER not configured — MQTT disabled")
        return

    asyncio.create_task(_run_loop(broker))


async def _run_loop(broker: str) -> None:
    import aiomqtt
    while True:
        try:
            kwargs = {
                "hostname": broker,
                "port": settings.mqtt_port,
            }
            if settings.mqtt_user:
                kwargs["username"] = settings.mqtt_user
                kwargs["password"] = settings.mqtt_pass
            async with aiomqtt.Client(**kwargs) as client:
                await client.subscribe("choresync/#")
                logger.info("MQTT connected: %s (user=%s)", broker, settings.mqtt_user or "anon")
                async for message in client.messages:
                    await _handle_message(str(message.topic), message.payload)
        except Exception as exc:
            logger.error("MQTT error: %s — reconnect in 10s", exc)
            await asyncio.sleep(10)


async def _handle_message(topic: str, payload: bytes) -> None:
    """MQTT 메시지 수신 → 트리거 매칭 → 할일 생성 + SSE 알림"""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.iot import IoTDevice, IoTTrigger
    from app.models.chore import ChoreTask, IntensityLevel
    from app.services.chore import calc_score

    payload_str = payload.decode("utf-8", errors="ignore")
    logger.info("MQTT message: topic=%s payload=%s", topic, payload_str[:100])

    db: Session = SessionLocal()
    try:
        device = db.query(IoTDevice).filter(
            IoTDevice.mqtt_topic == topic, IoTDevice.is_active.is_(True)
        ).first()
        if not device:
            logger.debug("No device for topic: %s", topic)
            return

        device.last_seen = datetime.now(timezone.utc)

        triggers = db.query(IoTTrigger).filter(
            IoTTrigger.device_id == device.id, IoTTrigger.is_active.is_(True)
        ).all()

        for trigger in triggers:
            if trigger.payload_match and trigger.payload_match not in payload_str:
                continue
            task = ChoreTask(
                family_id=device.family_id,
                name=trigger.task_name,
                category=trigger.task_category,
                estimated_minutes=trigger.task_estimated_minutes,
                intensity=IntensityLevel.NORMAL,
                score=calc_score(trigger.task_estimated_minutes, IntensityLevel.NORMAL),
                created_by=1,
            )
            db.add(task)
            db.flush()
            logger.info("Auto task created: %s (trigger=%s)", task.name, trigger.name)
            broadcast(
                device.family_id,
                "task_created",
                {"task_id": task.id, "name": task.name, "source": "iot"},
            )

        db.commit()
    except Exception as exc:
        logger.error("MQTT handle error: %s", exc)
        db.rollback()
    finally:
        db.close()
