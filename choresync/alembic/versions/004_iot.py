"""Phase 4: IoT tables

Revision ID: 004_iot
Revises: 003_quest
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "004_iot"
down_revision = "003_quest"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "iot_devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("family_id", sa.Integer, sa.ForeignKey("families.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "device_type",
            sa.Enum("Sensor", "Switch", "Camera", "Other", name="devicetype"),
            nullable=False,
            server_default="Sensor",
        ),
        sa.Column("mqtt_topic", sa.String(200), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("last_seen", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_iot_devices_family_id", "iot_devices", ["family_id"])

    op.create_table(
        "iot_triggers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("device_id", sa.Integer, sa.ForeignKey("iot_devices.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("payload_match", sa.String(200), nullable=True),
        sa.Column("task_name", sa.String(100), nullable=False),
        sa.Column("task_category", sa.String(50), nullable=False, server_default="IoT"),
        sa.Column("task_estimated_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_iot_triggers_device_id", "iot_triggers", ["device_id"])


def downgrade():
    op.drop_index("ix_iot_triggers_device_id", "iot_triggers")
    op.drop_table("iot_triggers")
    op.drop_index("ix_iot_devices_family_id", "iot_devices")
    op.drop_table("iot_devices")
