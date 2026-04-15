"""대시보드 위젯 레이아웃 모델"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

# 사용 가능한 위젯 ID 목록
AVAILABLE_WIDGETS = [
    {"id": "today_tasks", "name": "오늘 할일", "size": "full"},
    {"id": "score_summary", "name": "점수 요약", "size": "half"},
    {"id": "streak_card", "name": "스트릭", "size": "half"},
    {"id": "badge_progress", "name": "배지 진행도", "size": "half"},
    {"id": "family_ranking", "name": "가족 랭킹", "size": "half"},
    {"id": "shop_balance", "name": "포인트 잔액", "size": "half"},
    {"id": "weekly_chart", "name": "주간 통계", "size": "full"},
    {"id": "pending_quests", "name": "진행 중 퀘스트", "size": "half"},
]

DEFAULT_LAYOUT = [
    {"widget_id": "today_tasks", "position": 0, "visible": True, "size": "full"},
    {"widget_id": "score_summary", "position": 1, "visible": True, "size": "half"},
    {"widget_id": "streak_card", "position": 2, "visible": True, "size": "half"},
    {"widget_id": "badge_progress", "position": 3, "visible": True, "size": "half"},
    {"widget_id": "family_ranking", "position": 4, "visible": True, "size": "half"},
    {"widget_id": "shop_balance", "position": 5, "visible": True, "size": "half"},
    {"widget_id": "weekly_chart", "position": 6, "visible": True, "size": "full"},
    {"widget_id": "pending_quests", "position": 7, "visible": True, "size": "half"},
]


class DashboardLayout(Base):
    """사용자별 대시보드 위젯 레이아웃"""
    __tablename__ = "dashboard_layouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    layout_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
