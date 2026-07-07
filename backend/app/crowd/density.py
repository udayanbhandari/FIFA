"""Pure, deterministic crowd density estimation and congestion prediction.

No I/O, no side effects. The same inputs always produce the same outputs.
Uses FIFA Green Guide and Fruin LOS standards for safety classification.
"""

from __future__ import annotations

import math

from app.crowd import (
    BASE_FLOW_RATE,
    CAUTION_DENSITY,
    CRUSH_DENSITY,
    DENSITY_SPEED_FACTOR,
    FLOW_DECAY_HALF_LIFE_MIN,
    PHASE_CONCOURSE_LOAD,
    PREDICTION_HORIZON_MINUTES,
    TYPICAL_ZONE_AREA_M2,
)
from app.models import (
    CongestionAlert,
    CongestionPredictionQuery,
    CrowdQuery,
    ZoneDensity,
    ZoneType,
)


def _zone_area(zone_id: str) -> float:
    """Estimate zone area from the zone ID prefix or return a default.

    Zone IDs follow the pattern: {type}_{identifier}, e.g., 'concourse_north'.
    """
    for zone_type, area in TYPICAL_ZONE_AREA_M2.items():
        if zone_id.startswith(zone_type):
            return area
    return TYPICAL_ZONE_AREA_M2.get("concourse", 800.0)


def _decay_factor(elapsed_minutes: int) -> float:
    """Exponential decay factor modelling how crowd pressure dissipates.

    Based on Helbing & Johansson (2009) pedestrian flow dynamics.
    After FLOW_DECAY_HALF_LIFE_MIN minutes, ~50% of initial pressure remains.
    """
    if elapsed_minutes <= 0:
        return 1.0
    return math.exp(-0.693 * elapsed_minutes / FLOW_DECAY_HALF_LIFE_MIN)


def _classify_safety(density: float) -> str:
    """Classify density level into a safety status.

    Uses UK Green Guide thresholds:
    - safe:     < 2.0 persons/m² (comfortable standing)
    - caution:  2.0–5.0 persons/m² (steward intervention)
    - critical: ≥ 5.0 persons/m² (crush risk)
    """
    if density >= CRUSH_DENSITY:
        return "critical"
    if density >= CAUTION_DENSITY:
        return "caution"
    return "safe"


def _estimated_occupancy(
    gate_counts: dict[str, int],
    zone_id: str,
    event_phase: str,
) -> int:
    """Estimate how many people are currently in a zone.

    Distributes total gate ingress across zones based on event phase
    and zone type. This is a simplified model — production systems
    would use real-time sensor fusion.
    """
    total_ingress = sum(gate_counts.values()) if gate_counts else 0
    if total_ingress == 0:
        return 0

    phase_load = PHASE_CONCOURSE_LOAD.get(event_phase, 0.30)

    # Seating zones hold most fans during play phases
    if zone_id.startswith("seating"):
        return int(total_ingress * (1.0 - phase_load))

    # Non-seating zones share the concourse load proportionally
    zone_area = _zone_area(zone_id)
    total_non_seating_area = sum(
        area for zt, area in TYPICAL_ZONE_AREA_M2.items() if zt != "seating"
    )
    zone_share = zone_area / total_non_seating_area if total_non_seating_area > 0 else 0.1

    return max(1, int(total_ingress * phase_load * zone_share))


def estimate_zone_density(query: CrowdQuery) -> ZoneDensity:
    """Estimate current crowd density for a single zone.

    Pure function: takes a validated CrowdQuery, returns ZoneDensity.
    """
    zone_area = _zone_area(query.zone_id)
    occupancy = _estimated_occupancy(
        query.gate_counts, query.zone_id, query.event_phase.value
    )

    # Apply time-based decay for post-match thinning
    if query.event_phase.value in ("full_time", "post_match"):
        decay = _decay_factor(query.elapsed_minutes)
        occupancy = int(occupancy * decay)

    density = occupancy / zone_area if zone_area > 0 else 0.0
    capacity = int(zone_area * CAUTION_DENSITY)
    utilization = min(100.0, (occupancy / capacity * 100.0) if capacity > 0 else 0.0)

    # Determine zone type from ID
    zone_type = ZoneType.CONCOURSE
    for zt in ZoneType:
        if query.zone_id.startswith(zt.value):
            zone_type = zt
            break

    return ZoneDensity(
        zone_id=query.zone_id,
        zone_type=zone_type,
        current_density=round(density, 2),
        occupancy_count=occupancy,
        capacity=capacity,
        utilization_pct=round(utilization, 1),
        safety_status=_classify_safety(density),
    )


def _predict_future_density(
    current_density: float,
    event_phase: str,
    zone_id: str,
) -> float:
    """Predict density after PREDICTION_HORIZON_MINUTES.

    Uses phase transition heuristics: halftime and full_time see
    the largest surges in concourse density.
    """
    surge_phases = {"halftime": 1.4, "full_time": 1.6, "post_match": 1.3}
    decay_phases = {"kickoff": 0.5, "second_half": 0.4}

    multiplier = surge_phases.get(event_phase, 1.0)
    if event_phase in decay_phases and not zone_id.startswith("seating"):
        multiplier = decay_phases[event_phase]

    return round(current_density * multiplier, 2)


def _risk_level(density: float) -> str:
    """Map predicted density to a risk level string."""
    if density >= CRUSH_DENSITY:
        return "critical"
    if density >= CAUTION_DENSITY:
        return "high"
    if density >= CAUTION_DENSITY * 0.6:
        return "medium"
    return "low"


def _recommend_action(risk: str, zone_id: str) -> str:
    """Generate a recommended action based on risk level and zone."""
    actions = {
        "critical": f"Immediately open additional exits near {zone_id}. Deploy crowd control stewards.",
        "high": f"Direct incoming fans away from {zone_id}. Open overflow concourse areas.",
        "medium": f"Monitor {zone_id} closely. Prepare alternative routing.",
        "low": f"No action needed for {zone_id}. Normal crowd flow.",
    }
    return actions.get(risk, f"Continue monitoring {zone_id}.")


def predict_congestion(query: CongestionPredictionQuery) -> list[CongestionAlert]:
    """Predict congestion hotspots across all monitored zones.

    Returns alerts sorted by risk level (critical first).
    """
    alerts: list[CongestionAlert] = []
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    for zone_id, current_density in query.zone_densities.items():
        predicted = _predict_future_density(
            current_density, query.event_phase.value, zone_id
        )
        risk = _risk_level(predicted)

        alerts.append(
            CongestionAlert(
                zone_id=zone_id,
                predicted_density=predicted,
                risk_level=risk,
                recommended_action=_recommend_action(risk, zone_id),
                time_horizon_minutes=PREDICTION_HORIZON_MINUTES,
            )
        )

    alerts.sort(key=lambda a: risk_order.get(a.risk_level, 99))
    return alerts


def suggest_reroute(
    zone_densities: dict[str, float],
    target_zone: str,
) -> list[str]:
    """Suggest alternative zones when the target zone is congested.

    Returns zone IDs sorted by lowest density, excluding the target.
    Pure function with no I/O.
    """
    alternatives = {
        zid: d
        for zid, d in zone_densities.items()
        if zid != target_zone and d < CAUTION_DENSITY
    }
    return sorted(alternatives, key=lambda z: alternatives[z])[:5]


def walking_speed_at_density(density: float) -> float:
    """Estimate walking speed (m/s) at a given crowd density.

    Based on Helbing & Johansson (2009) speed-density relationship.
    """
    speed = BASE_FLOW_RATE - DENSITY_SPEED_FACTOR * density
    return max(speed, 0.3)
