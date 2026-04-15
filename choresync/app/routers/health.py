from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time

router = APIRouter(tags=["health"])

_start = time.time()

@router.get("/health")
def health():
    return JSONResponse({"status": "ok", "uptime_seconds": round(time.time() - _start, 1)})
