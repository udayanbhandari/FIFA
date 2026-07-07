"""Unit tests for sustainability carbon calculations."""

from __future__ import annotations

from app.models import SustainabilityQuery
from app.sustainability.tracker import calculate_match_footprint, compare_to_fifa_target


def test_footprint_calculation_yields_expected_numbers() -> None:
    """Verifies that the math matches standard emissions factors."""
    query = SustainabilityQuery(
        attendance=10000,
        transport_mix={"metro": 0.5, "bus": 0.5},
        energy_kwh=100000,
        waste_kg=5000,
        water_liters=100000,
    )
    result = calculate_match_footprint(query)
    assert result.total_kg_co2e > 0.0
    assert result.energy_kg_co2e > 0.0
    assert result.transport_kg_co2e > 0.0
    assert result.per_fan_kg_co2e > 0.0


def test_compare_to_fifa_target_limits() -> None:
    """Checks target evaluation limits (max 4 kg CO2 per fan)."""
    # Clean target
    query_green = SustainabilityQuery(
        attendance=50000,
        transport_mix={"metro": 1.0}, # metro has very low emission factor
        energy_kwh=1000,
        waste_kg=10,
        water_liters=100,
    )
    footprint_green = calculate_match_footprint(query_green)
    comp_green = compare_to_fifa_target(footprint_green, 50000)
    assert comp_green.on_target is True

    # Bad performance target exceedance
    query_heavy = SustainabilityQuery(
        attendance=100,
        transport_mix={"rideshare": 1.0}, # high ICE transit impact
        energy_kwh=500000,
        waste_kg=50000,
        water_liters=1000000,
    )
    footprint_heavy = calculate_match_footprint(query_heavy)
    comp_heavy = compare_to_fifa_target(footprint_heavy, 100)
    assert comp_heavy.on_target is False
    assert len(comp_heavy.recommendations) > 0
