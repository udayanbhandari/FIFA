"""Pure logic for calculating and evaluating matchday carbon footprints.

Uses FIFA 2026 sustainability standards and EPA equivalents.
No external I/O or API dependencies.
"""

from __future__ import annotations

from typing import Final

from app.models import MatchFootprint, SustainabilityComparison, SustainabilityQuery

# ── Emission factors (kg CO2e per unit) ──
# Sources: EPA Greenhouse Gas Equivalents (2024), FIFA 2022 Sustainability Reports, DEFRA (2023)
EMISSION_METRO_PASSENGER_KM: Final[float] = 0.035   # EPA standard transit emission factor
EMISSION_BUS_PASSENGER_KM: Final[float] = 0.058     # DEFRA average local bus
EMISSION_RIDESHARE_KM: Final[float] = 0.180        # Assumes average single occupant/pool ICE vehicle
EMISSION_SHUTTLE_KM: Final[float] = 0.045          # Dedicated transit shuttle
EMISSION_BICYCLE_KM: Final[float] = 0.0            # Direct zero emission

# Grid Electricity - US Average (EPA eGRID 2023)
EMISSION_ELECTRICITY_KWH: Final[float] = 0.385      # kg CO2e / kWh

# Municipal Solid Waste (EPA WARM model 2023)
EMISSION_WASTE_KG: Final[float] = 0.450             # kg CO2e / kg landfilled waste

# Water supply and wastewater treatment (DEFRA 2023)
EMISSION_WATER_LITER: Final[float] = 0.0003         # kg CO2e / Liter of treated water

# ── Constants for travel assumptions ──
AVERAGE_FAN_TRAVEL_DISTANCE_KM: Final[float] = 25.0  # Assumes stadium-bound fan commutes from hotel/home
FIFA_2026_TARGET_CO2_PER_FAN: Final[float] = 4.0      # FIFA target: max 4 kg CO2e per fan for operations


def calculate_match_footprint(query: SustainabilityQuery) -> MatchFootprint:
    """Calculate the carbon footprint of a single matchday.

    Pure function that transforms a query input into a MatchFootprint.
    """
    attendance = query.attendance
    transport_mix = query.transport_mix

    # 1. Transport footprint calculation
    transport_kg = 0.0
    transport_breakdown: dict[str, float] = {}

    for mode, fraction in transport_mix.items():
        fans_using_mode = attendance * fraction
        travel_distance_km = AVERAGE_FAN_TRAVEL_DISTANCE_KM

        # Match mode to emission factor
        if mode == "metro":
            factor = EMISSION_METRO_PASSENGER_KM
        elif mode == "bus":
            factor = EMISSION_BUS_PASSENGER_KM
        elif mode == "rideshare":
            # Assume rideshare has higher average distance and emissions
            factor = EMISSION_RIDESHARE_KM
        elif mode == "accessible_shuttle":
            factor = EMISSION_SHUTTLE_KM
        else:
            factor = 0.0

        mode_co2 = fans_using_mode * travel_distance_km * factor
        transport_kg += mode_co2
        transport_breakdown[mode] = round(mode_co2, 2)

    # 2. Energy footprint
    energy_kg = query.energy_kwh * EMISSION_ELECTRICITY_KWH

    # 3. Waste footprint
    waste_kg_co2e = query.waste_kg * EMISSION_WASTE_KG

    # 4. Water footprint
    water_kg_co2e = query.water_liters * EMISSION_WATER_LITER

    total_co2 = transport_kg + energy_kg + waste_kg_co2e + water_kg_co2e
    per_fan = (total_co2 / attendance) if attendance > 0 else 0.0

    return MatchFootprint(
        total_kg_co2e=round(total_co2, 2),
        transport_kg_co2e=round(transport_kg, 2),
        energy_kg_co2e=round(energy_kg, 2),
        waste_kg_co2e=round(waste_kg_co2e, 2),
        water_kg_co2e=round(water_kg_co2e, 2),
        per_fan_kg_co2e=round(per_fan, 2),
        transport_breakdown=transport_breakdown,
    )


def compare_to_fifa_target(footprint: MatchFootprint, attendance: int) -> SustainabilityComparison:
    """Compare a match footprint outcome against official target parameters."""
    target_total = attendance * FIFA_2026_TARGET_CO2_PER_FAN
    diff = footprint.total_kg_co2e - target_total
    on_target = diff <= 0

    recommendations: list[str] = []
    # Generate recommendations based on performance categories
    if footprint.per_fan_kg_co2e > FIFA_2026_TARGET_CO2_PER_FAN:
        recommendations.append(
            f"Per-fan emissions ({footprint.per_fan_kg_co2e} kg CO2e) exceed the target limit of "
            f"{FIFA_2026_TARGET_CO2_PER_FAN} kg. Review transit infrastructure partnerships."
        )

    # Specific threshold warnings
    transport_ratio = (footprint.transport_kg_co2e / footprint.total_kg_co2e) if footprint.total_kg_co2e > 0 else 0.0
    if transport_ratio > 0.60:
        recommendations.append(
            "Transport accounts for over 60% of total emissions. Increase metro schedules and offer "
            "incentives for public transit ticket bookings."
        )

    if footprint.waste_kg_co2e > 5000:
        recommendations.append(
            "Waste emissions are elevated. Deploy zero-waste sorting bins and compost options throughout the venue concourses."
        )

    if not recommendations:
        recommendations.append("All metrics are on track. Maintain existing operations.")

    return SustainabilityComparison(
        match_footprint=footprint,
        fifa_target_kg_co2e=round(target_total, 2),
        difference_kg_co2e=round(diff, 2),
        on_target=on_target,
        recommendations=recommendations,
    )
