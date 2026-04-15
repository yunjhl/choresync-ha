"""포인트 상점 서비스 — 재고 원자 차감 + 포인트 잔액 검증"""
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from app.models.reward import RewardItem, RewardPurchase
from app.models.family import FamilyMember

logger = logging.getLogger(__name__)


def purchase_item(
    user_id: int,
    family_id: int,
    reward_item_id: int,
    note: str | None,
    db: Session,
) -> RewardPurchase:
    """재고 원자 차감 + 잔액 확인 + 구매 기록"""
    item = db.get(RewardItem, reward_item_id)
    if not item or not item.is_active:
        raise HTTPException(404, "상품을 찾을 수 없습니다")
    if item.family_id != family_id:
        raise HTTPException(403, "다른 가족의 상품입니다")

    # 재고 원자 차감 (stock > 0 조건)
    if item.stock != -1:
        result = db.execute(
            update(RewardItem)
            .where(RewardItem.id == reward_item_id, RewardItem.stock > 0)
            .values(stock=RewardItem.stock - 1)
        )
        if result.rowcount == 0:
            raise HTTPException(400, "재고가 소진되었습니다")

    # 1인당 최대 구매 수 확인
    if item.max_per_user != -1:
        bought = db.query(RewardPurchase).filter(
            RewardPurchase.user_id == user_id,
            RewardPurchase.reward_item_id == reward_item_id,
            RewardPurchase.status != "rejected",
        ).count()
        if bought >= item.max_per_user:
            raise HTTPException(400, f"1인당 최대 {item.max_per_user}개까지 구매 가능합니다")

    # 잔액 확인
    from app.services.stats_service import get_user_balance
    balance = get_user_balance(user_id, family_id, db)
    if balance < item.point_cost:
        raise HTTPException(402, f"포인트 부족: 필요 {item.point_cost}, 현재 {round(balance, 1)}")

    purchase = RewardPurchase(
        family_id=family_id,
        user_id=user_id,
        reward_item_id=reward_item_id,
        points_spent=item.point_cost,
        status="pending",
        note=note,
    )
    db.add(purchase)
    db.flush()
    return purchase


def fulfill_purchase(purchase_id: int, admin_user_id: int, note: str | None, db: Session) -> RewardPurchase:
    purchase = db.get(RewardPurchase, purchase_id)
    if not purchase:
        raise HTTPException(404, "구매 내역을 찾을 수 없습니다")
    if purchase.status not in ("pending", "approved"):
        raise HTTPException(409, f"처리할 수 없는 상태입니다: {purchase.status}")
    purchase.status = "fulfilled"
    purchase.fulfilled_at = datetime.now(timezone.utc)
    purchase.fulfilled_by = admin_user_id
    if note:
        purchase.note = note
    db.flush()
    return purchase


def reject_purchase(purchase_id: int, admin_user_id: int, note: str | None, db: Session) -> RewardPurchase:
    purchase = db.get(RewardPurchase, purchase_id)
    if not purchase:
        raise HTTPException(404, "구매 내역을 찾을 수 없습니다")
    if purchase.status not in ("pending", "approved"):
        raise HTTPException(409, f"처리할 수 없는 상태입니다: {purchase.status}")
    # 재고 환원
    item = db.get(RewardItem, purchase.reward_item_id)
    if item and item.stock != -1:
        item.stock += 1
    purchase.status = "rejected"
    if note:
        purchase.note = note
    db.flush()
    return purchase
