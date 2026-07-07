"""Pure pathfinding and navigator logic for accessible stadium wayfinding.

Implements Dijkstra/A* routing on the venue graph.
Filters edges and adjusts weights based on accessibility needs.
Pure function with no side effects.
"""

from __future__ import annotations

import heapq
from typing import Final

from app.models import AccessibilityNeed, RouteStep, WayfindingRoute, ZoneType
from app.wayfinding.venue_graph import VenueNode, build_default_venue

# Speed mapping based on crowd guidelines
ACCESSIBLE_SPEED_M_S: Final[float] = 1.0  # 1 m/s average for wheelchair/assisted walking
STANDARD_SPEED_M_S: Final[float] = 1.3    # 1.3 m/s average normal walking speed


def find_accessible_route(
    origin: str,
    destination: str,
    accessibility_need: AccessibilityNeed,
    venue: dict[str, VenueNode] | None = None,
) -> WayfindingRoute:
    """Find the shortest accessible path between origin and destination.

    Uses Dijkstra's algorithm to search the venue graph.
    If wheelchair access is required, non-accessible edges (e.g. stairs only)
    are filtered out or penalized heavily.
    """
    if venue is None:
        venue = build_default_venue()

    if origin not in venue or destination not in venue:
        # Graceful return of empty route if invalid zones
        return WayfindingRoute(
            origin=origin,
            destination=destination,
            steps=[],
            total_distance_meters=0.0,
            estimated_minutes=0.0,
            accessibility_score=0.0,
        )

    counter = 0
    # Priority queue: (cost_so_far, counter, current_zone, path_taken)
    queue: list[tuple[float, int, str, list[RouteStep]]] = [(0.0, counter, origin, [])]
    visited: set[str] = set()

    while queue:
        cost, _, current, path = heapq.heappop(queue)

        if current == destination:
            # We reached the destination
            total_dist = sum(s.distance_meters for s in path)
            speed = ACCESSIBLE_SPEED_M_S if accessibility_need != AccessibilityNeed.NONE else STANDARD_SPEED_M_S
            est_minutes = (total_dist / speed) / 60.0

            # Calculate accessibility score based on steps compatibility
            total_steps = len(path)
            compatible_steps = sum(
                1 for s in path if _is_step_compatible(s, accessibility_need)
            )
            score = (compatible_steps / total_steps) if total_steps > 0 else 1.0

            return WayfindingRoute(
                origin=origin,
                destination=destination,
                steps=path,
                total_distance_meters=round(total_dist, 1),
                estimated_minutes=round(est_minutes, 1),
                accessibility_score=round(score, 2),
            )

        if current in visited:
            continue
        visited.add(current)

        node = venue[current]
        for edge in node.edges:
            # Filter based on wheelchair requirement
            if accessibility_need == AccessibilityNeed.WHEELCHAIR and not edge.wheelchair_accessible:
                continue

            # Skip stairs if wheelchair required
            if accessibility_need == AccessibilityNeed.WHEELCHAIR and edge.has_stairs and not edge.has_elevator and not edge.has_ramp:
                continue

            # Build step
            features = []
            if edge.has_elevator:
                features.append("elevator")
            if edge.has_ramp:
                features.append("ramp")
            if edge.has_tactile_markers:
                features.append("tactile_markers")
            if edge.width_meters >= 4.0:
                features.append("wide_corridor")

            instruction = edge.description or f"Proceed from {current} to {edge.to_zone}"
            if edge.has_elevator:
                instruction = f"Take the elevator from {current} to {edge.to_zone}"
            elif edge.has_ramp:
                instruction = f"Follow the ramp from {current} to {edge.to_zone}"

            step = RouteStep(
                from_zone=current,
                to_zone=edge.to_zone,
                instruction=instruction,
                distance_meters=edge.distance_meters,
                is_accessible=edge.wheelchair_accessible,
                accessibility_features=features,
            )

            # Weight heuristic adjustment based on accessibility need
            weight = edge.distance_meters
            if accessibility_need == AccessibilityNeed.VISUAL and not edge.has_tactile_markers:
                # Add penalty to non-tactile paths to favor safer paths for visually impaired
                weight *= 1.5

            counter += 1
            heapq.heappush(queue, (cost + weight, counter, edge.to_zone, path + [step]))

    # If no path found (disconnected graph segment)
    return WayfindingRoute(
        origin=origin,
        destination=destination,
        steps=[],
        total_distance_meters=0.0,
        estimated_minutes=0.0,
        accessibility_score=0.0,
    )


def find_nearest_facility(
    current_zone: str,
    facility_type: ZoneType,
    accessibility_need: AccessibilityNeed,
    venue: dict[str, VenueNode] | None = None,
) -> tuple[str, WayfindingRoute] | None:
    """Find the nearest facility of the specified type (e.g. RESTROOM, MEDICAL).

    Returns a tuple of (facility_zone_id, route_to_it) or None if not found.
    """
    if venue is None:
        venue = build_default_venue()

    best_route: WayfindingRoute | None = None
    best_zone: str | None = None

    for zone_id, node in venue.items():
        # Check node capability match
        if node.zone_type == facility_type.value:
            # If restroom, respect accessibility request if needed
            if facility_type == ZoneType.RESTROOM and accessibility_need == AccessibilityNeed.WHEELCHAIR:
                if not node.has_accessible_restroom:
                    continue

            # Calculate route
            route = find_accessible_route(current_zone, zone_id, accessibility_need, venue)
            if not route.steps:
                continue

            if best_route is None or route.total_distance_meters < best_route.total_distance_meters:
                best_route = route
                best_zone = zone_id

    if best_zone and best_route:
        return best_zone, best_route
    return None


def _is_step_compatible(step: RouteStep, need: AccessibilityNeed) -> bool:
    """Check if a route step fully matches accessibility requirements."""
    if need == AccessibilityNeed.NONE:
        return True
    if need == AccessibilityNeed.WHEELCHAIR:
        return step.is_accessible and ("stairs" not in step.instruction.lower())
    if need == AccessibilityNeed.VISUAL:
        return "tactile_markers" in step.accessibility_features
    return True
