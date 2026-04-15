"""템플릿 마켓플레이스 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_family_member
from app.models.chore import ChoreTemplate, INTENSITY_MULTIPLIER
from app.models.family import FamilyMember
from app.models.marketplace import MarketplaceTemplate
from app.schemas.marketplace import MarketplaceTemplateCreate, MarketplaceTemplateOut

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

# 나이대별 허용 assignee_type
_ALLOWED_ASSIGNEE = {
    "영유아": {None, "adult_only"},
    "초등": {None, "adult_only", "child_assist"},
}


@router.get("", response_model=list[MarketplaceTemplateOut])
def list_marketplace(
    category: str | None = None,
    family_size: str | None = None,
    family_id: int | None = None,
    child_age: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(MarketplaceTemplate).filter(MarketplaceTemplate.approved.is_(True))
    if category:
        q = q.filter(MarketplaceTemplate.category == category)
    if family_size and family_size != "전체":
        q = q.filter(
            (MarketplaceTemplate.family_size == family_size) |
            (MarketplaceTemplate.family_size == "전체")
        )
    items = q.order_by(MarketplaceTemplate.import_count.desc()).all()

    # child_age 필터
    if child_age is not None:
        filtered = []
        for item in items:
            if item.age_min is not None and child_age < item.age_min:
                continue
            if item.age_max is not None and child_age > item.age_max:
                continue
            filtered.append(item)
        items = filtered

    # 나이대별 assignee_type 필터 (영유아/초등은 부적합 task 제거)
    if family_size:
        for keyword, allowed in _ALLOWED_ASSIGNEE.items():
            if keyword in family_size:
                items = [i for i in items if i.assignee_type in allowed]
                break

    # 이미 임포트된 템플릿 이름 집합
    imported_names: set[str] = set()
    if family_id:
        rows = db.query(ChoreTemplate.name).filter(
            ChoreTemplate.family_id == family_id,
            ChoreTemplate.is_active.is_(True),
        ).all()
        imported_names = {r[0] for r in rows}

    result = []
    for item in items:
        out = MarketplaceTemplateOut.model_validate(item)
        mult = INTENSITY_MULTIPLIER.get(item.intensity, 1.5)
        out.points = round(item.estimated_minutes / 5 * mult, 1)
        out.is_imported = item.name in imported_names
        result.append(out)
    return result


@router.post("", response_model=MarketplaceTemplateOut, status_code=201)
def submit_to_marketplace(
    body: MarketplaceTemplateCreate,
    family_id: int,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    tmpl = MarketplaceTemplate(submitted_by_family_id=family_id, **body.model_dump())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.post("/{template_id}/import", response_model=dict, status_code=201)
def import_from_marketplace(
    template_id: int,
    family_id: int,
    recurrence_interval: str | None = None,
    recurrence_day: int | None = None,
    assigned_to: int | None = None,
    trigger_context: str | None = None,
    member: FamilyMember = Depends(get_family_member),
    db: Session = Depends(get_db),
):
    mkt = db.get(MarketplaceTemplate, template_id)
    if not mkt or not mkt.approved:
        raise HTTPException(404, "마켓플레이스 템플릿을 찾을 수 없음")

    existing = db.query(ChoreTemplate).filter(
        ChoreTemplate.family_id == family_id,
        ChoreTemplate.name == mkt.name,
        ChoreTemplate.is_active.is_(True),
    ).first()
    if existing:
        raise HTTPException(409, "이미 같은 이름의 템플릿이 있습니다")

    rec_interval = recurrence_interval if recurrence_interval is not None else mkt.recurrence_interval
    rec_day = recurrence_day if recurrence_day is not None else mkt.recurrence_day
    ctx = trigger_context if trigger_context is not None else mkt.trigger_context

    new_tmpl = ChoreTemplate(
        family_id=family_id,
        created_by=member.id,
        name=mkt.name,
        category=mkt.category,
        estimated_minutes=mkt.estimated_minutes,
        intensity=mkt.intensity,
        description=mkt.description,
        is_marketplace=True,
        recurrence_interval=rec_interval,
        recurrence_day=rec_day,
        trigger_context=ctx,
        assigned_to=assigned_to,
        age_min=mkt.age_min,
        age_max=mkt.age_max,
        assignee_type=mkt.assignee_type,
    )
    db.add(new_tmpl)
    mkt.import_count += 1
    db.commit()
    db.refresh(new_tmpl)
    return {"template_id": new_tmpl.id, "message": "임포트 완료", "recurrence": rec_interval}

