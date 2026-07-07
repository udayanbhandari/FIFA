"""Unit tests for crowd density and safety calculations."""

from __future__ import annotations

from app.crowd.density import estimate_zone_density, predict_congestion, suggest_reroute
from app.models import CongestionPredictionQuery, CrowdQuery, EventPhase


def test_gate_ingress_calculates_correct_occupancy() -> None:
    """Verifies that turnstile counts yield the expected zone density."""
    query = CrowdQuery(
        zone_id="concourse_north",
        gate_counts={"gate_north": 1000, "gate_south": 1000},
        elapsed_minutes=0,
        event_phase=EventPhase.PRE_MATCH,
    )
    result = estimate_zone_density(query)
    assert result.zone_id == "concourse_north"
    assert result.occupancy_count > 0
    assert result.current_density > 0.0


def test_decay_reduces_occupancy_post_match() -> None:
    """Validates that crowd volumes drop over time in post-match phase."""
    query_start = CrowdQuery(
        zone_id="concourse_north",
        gate_counts={"gate_north": 5000},
        elapsed_minutes=0,
        event_phase=EventPhase.POST_MATCH,
    )
    query_later = CrowdQuery(
        zone_id="concourse_north",
        gate_counts={"gate_north": 5000},
        elapsed_minutes=60,
        event_phase=EventPhase.POST_MATCH,
    )
    density_start = estimate_zone_density(query_start)
    density_later = estimate_zone_density(query_later)

    assert density_later.occupancy_count < density_start.occupancy_count


def test_safety_status_classifies_correctly() -> None:
    """Validates boundary classifications of Safe / Caution / Critical densities."""
    # Under limit
    query_safe = CrowdQuery(
        zone_id="concourse_north",
        gate_counts={"gate_north": 50},
        elapsed_minutes=0,
        event_phase=EventPhase.PRE_MATCH,
    )
    assert estimate_zone_density(query_safe).safety_status == "safe"

    # Extreme numbers
    query_crush = CrowdQuery(
        zone_id="vomitory_1",
        gate_counts={"gate_north": 80000},
        elapsed_minutes=0,
        event_phase=EventPhase.POST_MATCH,
    )
    assert estimate_zone_density(query_crush).safety_status == "critical"


def test_congestion_prediction_returns_correct_ordering() -> None:
    """Confirms predicted hotspots are ranked by highest risk level."""
    query = CongestionPredictionQuery(
        zone_densities={
            "concourse_north": 0.5,
            "vomitory_1": 4.5,
            "transit_hub": 1.0,
        },
        event_phase=EventPhase.HALFTIME,
        elapsed_minutes=0,
    )
    alerts = predict_congestion(query)
    assert len(alerts) == 3
    # First alert should be the highest risk (vomitory_1 due to halftime surge multiplier)
    assert alerts[0].zone_id == "vomitory_1"
    assert alerts[0].risk_level in ("critical", "high")


def test_suggest_reroute_selects_lowest_congested_options() -> None:
    """Checks that rerouting options favor zones with low density occupancy."""
    densities = {
        "concourse_north": 4.2,
        "concourse_south": 0.8,
        "concourse_east": 1.5,
        "concourse_west": 2.9,
    }
    options = suggest_reroute(densities, "concourse_north")
    assert "concourse_north" not in options
    # Lowest density option should be first
    assert options[0] == "concourse_south"
