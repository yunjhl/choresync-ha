"""웹 페이지 라우터 — Jinja2 + HTMX"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import jinja2

from app.services.i18n import detect_lang, get_translator

router = APIRouter(tags=["pages"])

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/templates"),
    auto_reload=True,
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)
templates = Jinja2Templates(env=_jinja_env)

BASE_PATH = ""


def _ctx(request: Request, **extra):
    """공통 템플릿 컨텍스트 — t(), base_path 포함"""
    lang = detect_lang(
        request.cookies.get("lang", ""),
        request.headers.get("Accept-Language", ""),
    )
    return {"request": request, "t": get_translator(lang), "lang": lang, "base_path": BASE_PATH, **extra}


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", _ctx(request))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", _ctx(request))


@router.get("/members", response_class=HTMLResponse)
async def members_page(request: Request):
    return templates.TemplateResponse("members.html", _ctx(request))


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", _ctx(request))


@router.get("/quests", response_class=HTMLResponse)
async def quests_page(request: Request):
    return templates.TemplateResponse("quests.html", _ctx(request))


@router.get("/wishes", response_class=HTMLResponse)
async def wishes_page(request: Request):
    return templates.TemplateResponse("wishes.html", _ctx(request))


@router.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request):
    return templates.TemplateResponse("devices.html", _ctx(request))


@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    return templates.TemplateResponse("stats.html", _ctx(request))


@router.get("/marketplace", response_class=HTMLResponse)
async def marketplace_page(request: Request):
    return templates.TemplateResponse("marketplace.html", _ctx(request))


@router.get("/ha", response_class=HTMLResponse)
async def ha_page(request: Request):
    return templates.TemplateResponse("ha.html", _ctx(request))


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", _ctx(request))


@router.get("/badges", response_class=HTMLResponse)
async def badges_page(request: Request):
    return templates.TemplateResponse("badges.html", _ctx(request))


@router.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request):
    return templates.TemplateResponse("shop.html", _ctx(request))


@router.get("/invite/{code}", response_class=HTMLResponse)
async def invite_page(request: Request, code: str):
    return templates.TemplateResponse("invite.html", _ctx(request, code=code))

@router.get("/guide", response_class=HTMLResponse)
async def guide_page(request: Request):
    return templates.TemplateResponse("guide.html", _ctx(request))
