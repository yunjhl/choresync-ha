"""IoT 기기 + 트리거 모델"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeviceType(str, enum.Enum):
    SENSOR = "Sensor"
    SWITCH = "Switch"
    CAMERA = "Camera"
    OTHER = "Other"


class IoTDevice(Base):
    """등록된 IoT 기기"""

    __tablename__ = "iot_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(
        Enum(DeviceType), nullable=False, default=DeviceType.SENSOR
    )
    mqtt_topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    family = relationship("Family")
    triggers = relationship("IoTTrigger", back_populates="device", cascade="all, delete-orphan")


class IoTTrigger(Base):
    """기기 이벤트 → 할일 자동 생성 트리거"""

    __tablename__ = "iot_triggers"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("iot_devices.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_match: Mapped[str | None] = mapped_column(String(200), nullable=True)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_category: Mapped[str] = mapped_column(String(50), nullable=False, default="IoT")
    task_estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    device = relationship("IoTDevice", back_populates="triggers")
