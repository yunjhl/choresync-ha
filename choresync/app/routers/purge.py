"""임시 DB 초기화 엔드포인트 — 시뮬레이션 전 데이터 리셋용"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, inspect
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin", tags=["admin"])

PURGE_SECRET = "sim-reset-2024"

@router.get("/tables")
def list_tables(secret: str, db: Session = Depends(get_db)):
    if secret != PURGE_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    return {"tables": [r[0] for r in result.fetchall()]}

@router.post("/purge")
def purge_all_data(secret: str, db: Session = Depends(get_db)):
    """모든 유저/가족/할일 데이터 삭제 (alembic_version, badge_definitions 제외)."""
    if secret != PURGE_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Get actual table names from SQLite
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    all_tables = [r[0] for r in result.fetchall()]
    
    # Skip system/seed tables
    skip_tables = {"alembic_version", "badge_definitions", "badge_definition",
                   "marketplace_template", "marketplace_templates"}
    
    deleted = {}
    # Delete in dependency order (children first)
    order = ["completion_history", "push_subscription"]
    for t in all_tables:
        if t not in order and t not in skip_tables:
            order.append(t)
    
    db.execute(text("PRAGMA foreign_keys = OFF"))
    for t in order:
        if t in skip_tables or t not in all_tables:
            continue
        try:
            result = db.execute(text(f"DELETE FROM \"{t}\""))
            deleted[t] = result.rowcount
        except Exception as e:
            deleted[t] = f"err: {str(e)[:80]}"
    db.execute(text("PRAGMA foreign_keys = ON"))
    db.commit()
    return {"status": "purged", "tables_found": all_tables, "deleted": deleted}
