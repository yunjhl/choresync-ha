"""ChoreSync HA 애드온 — FastAPI 진입점 (Phase 7)"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, families, pages, tasks, quests, iot, stats, health
from app.routers import marketplace, ha
from app.routers import chat, webhook, notify
from app.routers import calendar, badges, shop
from app.routers import purge


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.mqtt import start_mqtt_listener
    await start_mqtt_listener(app)
    from app.services.scheduler import start_scheduler
    _scheduler = start_scheduler()
    app.state.scheduler = _scheduler
    # Phase 7: 기본 배지 시드
    from app.database import SessionLocal
    from app.services.badge_service import seed_default_badges
    db = SessionLocal()
    try:
        seed_default_badges(db)
    finally:
        db.close()
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)


app = FastAPI(
    title="ChoreSync",
    version="0.7.0",
    docs_url="/api/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(families.router)
app.include_router(tasks.router)
app.include_router(quests.router)
app.include_router(iot.router)
app.include_router(stats.router)
app.include_router(marketplace.router)
app.include_router(ha.router)
app.include_router(chat.router)
app.include_router(webhook.router)
app.include_router(notify.router)
app.include_router(calendar.router)
app.include_router(badges.router)
app.include_router(shop.router)
app.include_router(purge.router)
app.include_router(pages.router)
app.include_router(health.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
