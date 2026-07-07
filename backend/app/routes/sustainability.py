"""FastAPI Transport Router for sustainability metrics calculations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.models import MatchFootprint, SustainabilityComparison, SustainabilityQuery
from app.sustainability.tracker import (
    FIFA_2026_TARGET_CO2_PER_FAN,
    calculate_match_footprint,
    compare_to_fifa_target,
)

router = APIRouter(prefix="/sustainability", tags=["sustainability"])


@router.post("/footprint", response_model=MatchFootprint)
def calculate_footprint(query: SustainabilityQuery) -> MatchFootprint:
    """Calculate the operational and spectator transport carbon footprint."""
    return calculate_match_footprint(query)


@router.post("/compare", response_model=SustainabilityComparison)
def compare_footprint(query: SustainabilityQuery) -> SustainabilityComparison:
    """Compare computed match carbon metrics against FIFA targets."""
    footprint = calculate_match_footprint(query)
    return compare_to_fifa_target(footprint, query.attendance)


@router.get("/targets")
def get_targets() -> dict[str, Any]:
    """Retrieve official sustainability performance targets."""
    return {
        "fifa_target_kg_co2e_per_fan": FIFA_2026_TARGET_CO2_PER_FAN,
        "metrics_tracked": ["transport", "energy", "waste", "water"],
    }
