"""FastAPI Transport Router for system health liveness checks."""

from __future__ import annotations

from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(prefix="/health", tags=["system"])


@router.get("", response_model=HealthResponse)
def check_health() -> HealthResponse:
    """Return standard system configuration details and version markers."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )
