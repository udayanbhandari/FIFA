"""FastAPI Transport Router for crowd density operations."""

from __future__ import annotations

from fastapi import APIRouter

from app.crowd.density import estimate_zone_density, predict_congestion, suggest_reroute
from app.models import (
    CongestionAlert,
    CongestionPredictionQuery,
    CrowdQuery,
    ZoneDensity,
)

router = APIRouter(prefix="/crowd", tags=["crowd"])


@router.post("/density", response_model=ZoneDensity)
def get_density(query: CrowdQuery) -> ZoneDensity:
    """Analyze current turnstile traffic inputs to compute current zone density."""
    return estimate_zone_density(query)


@router.post("/predict", response_model=list[CongestionAlert])
def get_prediction(query: CongestionPredictionQuery) -> list[CongestionAlert]:
    """Identify congestion hotspots and recommend exit deployment actions."""
    return predict_congestion(query)


@router.post("/reroute", response_model=list[str])
def get_reroute(query: dict[str, float], target_zone: str) -> list[str]:
    """Find the lowest density zones adjacent to the congested target."""
    return suggest_reroute(query, target_zone)
