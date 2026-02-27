# app/Router/health.py

from fastapi import APIRouter, Request
from app.Core.rate_limiter import limiter

router = APIRouter(tags=["health"])

@router.get("/", tags=["health"])
@limiter.limit("5/minute")
async def health(request: Request):
    """
    Endpoint di controllo dello stato dell'applicazione.
    """
    return {"status": "ok"}
