"""포인트 상점 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user, get_family_member, get_admin_member
from app.models.reward import RewardItem, RewardPurchase
from app.models.family import FamilyMember
from app.models.user import User
from app.services.shop_service import purchase_item, fulfill_purchase, reject_purchase
from app.services.stats_service import get_user_balance

router = APIRouter(prefix="/api/shop", tags=["shop"])


class CreateItemBody(BaseModel):
    name: str
    description: Optional[str] = None
    icon: str = "🎁"
    point_cost: int
    stock: int = -1
    max_per_user: int = -1
    category: str = "general"
    available_for: str = "all"


class PurchaseBody(BaseModel):
    reward_item_id: int
    note: Optional[str] = None


class FulfillBody(BaseModel):
    note: Optional[str] = None


@router.get("/items")
def list_items(
    family_id: int,
    category: Optional[str] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    query = db.query(RewardItem).filter(
        RewardItem.family_id == family_id,
        RewardItem.is_active.is_(True),
    )
    if category:
        query = query.filter(RewardItem.category == category)
    items = query.order_by(RewardItem.point_cost).all()
    balance = get_user_balance(member.user_id, family_id, db)
    return {
        "balance": balance,
        "items": [{"id": i.id, "name": i.name, "description": i.description,
                   "icon": i.icon, "point_cost": i.point_cost, "stock": i.stock,
                   "category": i.category, "available_for": i.available_for,
                   "can_afford": balance >= i.point_cost} for i in items],
    }


@router.post("/items")
def create_item(
    family_id: int,
    body: CreateItemBody,
    admin: FamilyMember = Depends(get_admin_member),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = RewardItem(
        family_id=family_id, name=body.name, description=body.description,
        icon=body.icon, point_cost=body.point_cost, stock=body.stock,
        max_per_user=body.max_per_user, category=body.category,
        available_for=body.available_for, created_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "point_cost": item.point_cost}


@router.delete("/items/{item_id}")
def delete_item(
    family_id: int,
    item_id: int,
    admin: FamilyMember = Depends(get_admin_member),
    db: Session = Depends(get_db),
):
    item = db.query(RewardItem).filter(
        RewardItem.id == item_id, RewardItem.family_id == family_id,
    ).first()
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")
    item.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/purchase")
def buy_item(
    family_id: int,
    body: PurchaseBody,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    purchase = purchase_item(member.user_id, family_id, body.reward_item_id, body.note, db)
    db.commit()
    return {"purchase_id": purchase.id, "status": purchase.status, "points_spent": purchase.points_spent}


@router.get("/purchases")
def list_purchases(
    family_id: int,
    status: Optional[str] = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    from app.models.family import MemberRole
    query = db.query(RewardPurchase).filter(RewardPurchase.family_id == family_id)
    if member.role != MemberRole.ADMIN:
        query = query.filter(RewardPurchase.user_id == member.user_id)
    if status:
        query = query.filter(RewardPurchase.status == status)
    purchases = query.order_by(RewardPurchase.purchased_at.desc()).all()
    result = []
    for p in purchases:
        user = db.get(User, p.user_id)
        item = db.get(RewardItem, p.reward_item_id)
        result.append({
            "id": p.id, "user_name": user.name if user else "", "item_name": item.name if item else "",
            "item_icon": item.icon if item else "🎁", "points_spent": p.points_spent,
            "status": p.status, "note": p.note,
            "purchased_at": p.purchased_at.isoformat(),
        })
    return result


@router.put("/purchases/{purchase_id}/fulfill")
def fulfill(
    family_id: int,
    purchase_id: int,
    body: FulfillBody,
    admin: FamilyMember = Depends(get_admin_member),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = fulfill_purchase(purchase_id, current_user.id, body.note, db)
    db.commit()
    return {"id": p.id, "status": p.status}


@router.put("/purchases/{purchase_id}/reject")
def reject(
    family_id: int,
    purchase_id: int,
    body: FulfillBody,
    admin: FamilyMember = Depends(get_admin_member),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = reject_purchase(purchase_id, current_user.id, body.note, db)
    db.commit()
    return {"id": p.id, "status": p.status}
