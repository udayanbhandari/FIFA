"""Unit tests for accessible wayfinding A* routing calculations."""

from __future__ import annotations

from app.models import AccessibilityNeed, ZoneType
from app.wayfinding.navigator import find_accessible_route, find_nearest_facility


def test_standard_route_calculation() -> None:
    """Verifies that navigation returns a valid route for standard profiles."""
    route = find_accessible_route("gate_north", "seating_1", AccessibilityNeed.NONE)
    assert len(route.steps) > 0
    assert route.total_distance_meters > 0.0
    assert route.estimated_minutes > 0.0
    assert route.accessibility_score == 1.0


def test_wheelchair_route_avoids_stair_heavy_paths() -> None:
    """Confirms wheelchair routes favour ramp/elevator edges over stairs."""
    # Use the default venue which has elevator paths for upper sections
    route = find_accessible_route("gate_north", "seating_5", AccessibilityNeed.WHEELCHAIR)

    # If a path exists, no step should rely on stairs-only (is_accessible must be True)
    if route.steps:
        for step in route.steps:
            assert step.is_accessible, (
                f"Step from {step.from_zone} to {step.to_zone} is not accessible but wheelchair was requested"
            )


def test_nearest_facility_restroom_resolution() -> None:
    """Validates closest restroom search returns nearest wheelchair-accessible match."""
    result = find_nearest_facility("gate_north", ZoneType.RESTROOM, AccessibilityNeed.WHEELCHAIR)
    assert result is not None
    facility_zone, route = result
    assert facility_zone.startswith("restroom")
    assert len(route.steps) > 0
    assert route.accessibility_score == 1.0


def test_invalid_origin_destination_returns_empty_gracefully() -> None:
    """Guarantees route search does not crash on unrecognized zone inputs."""
    route = find_accessible_route("invalid_zone_a", "seating_1", AccessibilityNeed.NONE)
    assert len(route.steps) == 0
    assert route.total_distance_meters == 0.0
