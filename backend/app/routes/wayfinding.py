"""FastAPI Transport Router for accessible wayfinding operations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.models import (
    NearestFacilityRequest,
    WayfindingRequest,
    WayfindingRoute,
)
from app.wayfinding.navigator import find_accessible_route, find_nearest_facility

router = APIRouter(prefix="/wayfinding", tags=["wayfinding"])


@router.post("/route", response_model=WayfindingRoute)
def get_route(request: WayfindingRequest) -> WayfindingRoute:
    """Find an accessible A* path matching mobility requirements."""
    route = find_accessible_route(
        request.origin_zone,
        request.destination_zone,
        request.accessibility_need,
    )
    if not route.steps:
        raise HTTPException(
            status_code=404,
            detail=f"No path found connecting {request.origin_zone} and {request.destination_zone}",
        )
    return route


@router.post("/nearest")
def get_nearest(request: NearestFacilityRequest) -> dict[str, Any]:
    """Locate the closest matches for facilities with accessibility filters."""
    result = find_nearest_facility(
        request.current_zone,
        request.facility_type,
        request.accessibility_need,
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No facility of type {request.facility_type.value} accessible from {request.current_zone}",
        )

    facility_zone, route = result
    return {
        "facility_zone_id": facility_zone,
        "route": route,
    }
