"""Domain models and validated API contracts for StadiumIQ.

Every field uses bounded constraints via Field(). Enums enforce
finite value sets at compile time. Models serve as both input
validation and OpenAPI documentation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# ── Named upper-bound constants (generous but finite) ──

MAX_STADIUM_CAPACITY = 110_000  # Largest FIFA venue ≈ 105K (Azteca)
MAX_ZONES = 200  # Stadium zones including sub-areas
MAX_GATE_COUNT = 50_000  # Max ingress through a single gate cluster
MAX_ELAPSED_MINUTES = 600  # 10-hour event window
MAX_QUERY_LENGTH = 1000  # Fan assistant question character limit
MAX_ZONE_NAME_LENGTH = 100
MAX_COORDINATE = 10_000.0  # Relative coordinate system
MAX_DENSITY = 10.0  # persons/m² — beyond this is physically impossible
MAX_ATTENDANCE = 110_000
MAX_ENERGY_KWH = 1_000_000  # Large venue energy per match
MAX_WASTE_KG = 100_000  # Waste per match
MAX_WATER_LITERS = 5_000_000  # Water usage per match


class ZoneType(str, Enum):
    """Stadium zone categories."""

    GATE = "gate"
    CONCOURSE = "concourse"
    SEATING = "seating"
    CONCESSION = "concession"
    MEDICAL = "medical"
    RESTROOM = "restroom"
    VOMITORY = "vomitory"
    PARKING = "parking"
    TRANSIT_HUB = "transit_hub"


class AccessibilityNeed(str, Enum):
    """Fan accessibility requirements for route planning."""

    NONE = "none"
    WHEELCHAIR = "wheelchair"
    VISUAL = "visual"
    HEARING = "hearing"
    COGNITIVE = "cognitive"


class TransportMode(str, Enum):
    """Transportation options for stadium access and departure."""

    METRO = "metro"
    BUS = "bus"
    RIDESHARE = "rideshare"
    WALK = "walk"
    ACCESSIBLE_SHUTTLE = "accessible_shuttle"
    BICYCLE = "bicycle"


class EventPhase(str, Enum):
    """Phases of a match event affecting crowd dynamics."""

    PRE_MATCH = "pre_match"
    KICKOFF = "kickoff"
    HALFTIME = "halftime"
    SECOND_HALF = "second_half"
    FULL_TIME = "full_time"
    POST_MATCH = "post_match"


class Language(str, Enum):
    """Supported languages for fan assistance."""

    EN = "en"
    ES = "es"
    FR = "fr"
    AR = "ar"
    PT = "pt"
    DE = "de"
    JA = "ja"
    KO = "ko"
    ZH = "zh"


# ── Input Models ──


class CrowdQuery(BaseModel):
    """Request for crowd density analysis at a specific zone."""

    zone_id: str = Field(min_length=1, max_length=MAX_ZONE_NAME_LENGTH)
    gate_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Gate ID → current cumulative count",
    )
    elapsed_minutes: int = Field(ge=0, le=MAX_ELAPSED_MINUTES)
    event_phase: EventPhase = EventPhase.PRE_MATCH
    stadium_capacity: int = Field(
        default=80_000, ge=1_000, le=MAX_STADIUM_CAPACITY
    )


class CongestionPredictionQuery(BaseModel):
    """Request for congestion prediction across the venue."""

    zone_densities: dict[str, float] = Field(
        default_factory=dict,
        description="Zone ID → current persons/m²",
    )
    event_phase: EventPhase = EventPhase.PRE_MATCH
    elapsed_minutes: int = Field(ge=0, le=MAX_ELAPSED_MINUTES)
    stadium_capacity: int = Field(
        default=80_000, ge=1_000, le=MAX_STADIUM_CAPACITY
    )


class WayfindingRequest(BaseModel):
    """Request for accessible route finding between two points."""

    origin_zone: str = Field(min_length=1, max_length=MAX_ZONE_NAME_LENGTH)
    destination_zone: str = Field(
        min_length=1, max_length=MAX_ZONE_NAME_LENGTH
    )
    accessibility_need: AccessibilityNeed = AccessibilityNeed.NONE


class NearestFacilityRequest(BaseModel):
    """Request for the nearest facility of a given type."""

    current_zone: str = Field(min_length=1, max_length=MAX_ZONE_NAME_LENGTH)
    facility_type: ZoneType = ZoneType.RESTROOM
    accessibility_need: AccessibilityNeed = AccessibilityNeed.NONE


class FanAssistantQuery(BaseModel):
    """Fan question for the AI assistant."""

    question: str = Field(min_length=1, max_length=MAX_QUERY_LENGTH)
    language: Language = Language.EN
    current_zone: str = Field(
        default="main_concourse",
        min_length=1,
        max_length=MAX_ZONE_NAME_LENGTH,
    )
    device_id: str = Field(
        default="anonymous",
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9_\-]+$",
    )


class SustainabilityQuery(BaseModel):
    """Input for match sustainability footprint calculation."""

    attendance: int = Field(ge=0, le=MAX_ATTENDANCE)
    transport_mix: dict[str, float] = Field(
        default_factory=lambda: {
            "metro": 0.40,
            "bus": 0.20,
            "rideshare": 0.25,
            "walk": 0.10,
            "accessible_shuttle": 0.05,
        },
        description="Transport mode → fraction of fans (must sum to ~1.0)",
    )
    energy_kwh: float = Field(default=250_000.0, ge=0, le=MAX_ENERGY_KWH)
    waste_kg: float = Field(default=15_000.0, ge=0, le=MAX_WASTE_KG)
    water_liters: float = Field(default=500_000.0, ge=0, le=MAX_WATER_LITERS)


# ── Output Models ──


class ZoneDensity(BaseModel):
    """Density analysis result for a stadium zone."""

    zone_id: str
    zone_type: ZoneType
    current_density: float = Field(description="persons/m²")
    occupancy_count: int
    capacity: int
    utilization_pct: float = Field(description="0-100 percentage")
    safety_status: str = Field(description="safe / caution / critical")


class CongestionAlert(BaseModel):
    """Predicted congestion hotspot."""

    zone_id: str
    predicted_density: float
    risk_level: str = Field(description="low / medium / high / critical")
    recommended_action: str
    time_horizon_minutes: int


class RouteStep(BaseModel):
    """Single step in a wayfinding route."""

    from_zone: str
    to_zone: str
    instruction: str
    distance_meters: float
    is_accessible: bool
    accessibility_features: list[str] = Field(default_factory=list)


class WayfindingRoute(BaseModel):
    """Complete accessible route between two points."""

    origin: str
    destination: str
    steps: list[RouteStep]
    total_distance_meters: float
    estimated_minutes: float
    accessibility_score: float = Field(
        ge=0.0, le=1.0, description="1.0 = fully accessible"
    )


class SuggestedAction(BaseModel):
    """Action suggested by the AI assistant."""

    action: str
    details: str


class AssistantResponse(BaseModel):
    """Response from the fan assistant (AI or rules-based)."""

    answer: str
    suggested_actions: list[SuggestedAction] = Field(default_factory=list)
    zone_reference: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(description="gemini / rules / cache")
    language: Language = Language.EN


class MatchFootprint(BaseModel):
    """Carbon footprint breakdown for a single match."""

    total_kg_co2e: float
    transport_kg_co2e: float
    energy_kg_co2e: float
    waste_kg_co2e: float
    water_kg_co2e: float
    per_fan_kg_co2e: float
    transport_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Mode → kg CO₂e",
    )


class SustainabilityComparison(BaseModel):
    """Comparison of match footprint against FIFA targets."""

    match_footprint: MatchFootprint
    fifa_target_kg_co2e: float
    difference_kg_co2e: float
    on_target: bool
    recommendations: list[str] = Field(default_factory=list)


class FanQueryRecord(BaseModel):
    """Stored fan assistant interaction for analytics."""

    id: str = ""
    device_id: str
    question: str
    answer: str
    source: str
    language: Language
    created_at: datetime | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
