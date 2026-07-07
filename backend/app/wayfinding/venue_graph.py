"""Stadium venue graph for accessible wayfinding.

Pure data structure — no I/O. Represents a realistic FIFA World Cup venue
with ~30 nodes (zones) and weighted edges (corridors, elevators, ramps, stairs).
Accessibility metadata on each edge enables A* routing for mobility needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VenueEdge:
    """A connection between two zones in the stadium."""

    to_zone: str
    distance_meters: float
    wheelchair_accessible: bool = True
    has_elevator: bool = False
    has_ramp: bool = False
    has_stairs: bool = False
    has_tactile_markers: bool = False
    width_meters: float = 3.0
    description: str = ""


@dataclass
class VenueNode:
    """A zone in the stadium with its connections."""

    zone_id: str
    zone_type: str
    display_name: str
    edges: list[VenueEdge] = field(default_factory=list)
    is_accessible: bool = True
    has_accessible_restroom: bool = False
    has_medical: bool = False


def build_default_venue() -> dict[str, VenueNode]:
    """Build a realistic FIFA World Cup venue graph.

    Models a ~80,000 capacity stadium with:
    - 4 main gates (N, S, E, W)
    - 4 concourse sections
    - 8 seating sections
    - Concession, restroom, and medical areas
    - Accessible routes with elevators and ramps
    """
    nodes: dict[str, VenueNode] = {}

    # ── Gates ──
    for direction in ("north", "south", "east", "west"):
        gate_id = f"gate_{direction}"
        nodes[gate_id] = VenueNode(
            zone_id=gate_id,
            zone_type="gate",
            display_name=f"{direction.title()} Gate",
        )

    # ── Concourses ──
    for direction in ("north", "south", "east", "west"):
        conc_id = f"concourse_{direction}"
        nodes[conc_id] = VenueNode(
            zone_id=conc_id,
            zone_type="concourse",
            display_name=f"{direction.title()} Concourse",
        )

    # ── Seating sections ──
    for section_num in range(1, 9):
        seat_id = f"seating_{section_num}"
        nodes[seat_id] = VenueNode(
            zone_id=seat_id,
            zone_type="seating",
            display_name=f"Section {section_num}",
        )

    # ── Concession stands ──
    for direction in ("north", "south"):
        conc_id = f"concession_{direction}"
        nodes[conc_id] = VenueNode(
            zone_id=conc_id,
            zone_type="concession",
            display_name=f"{direction.title()} Food Court",
        )

    # ── Restrooms ──
    for direction in ("north", "south", "east", "west"):
        rest_id = f"restroom_{direction}"
        nodes[rest_id] = VenueNode(
            zone_id=rest_id,
            zone_type="restroom",
            display_name=f"{direction.title()} Restroom",
            has_accessible_restroom=(direction in ("north", "south")),
        )

    # ── Medical ──
    nodes["medical_main"] = VenueNode(
        zone_id="medical_main",
        zone_type="medical",
        display_name="Main Medical Center",
        has_medical=True,
    )
    nodes["medical_field"] = VenueNode(
        zone_id="medical_field",
        zone_type="medical",
        display_name="Field-Level Medical",
        has_medical=True,
    )

    # ── Transit hub ──
    nodes["transit_hub"] = VenueNode(
        zone_id="transit_hub",
        zone_type="transit_hub",
        display_name="Transit Hub (Metro/Bus)",
    )

    # ── Vomitories (seating entry points) ──
    for section_num in range(1, 5):
        vom_id = f"vomitory_{section_num}"
        nodes[vom_id] = VenueNode(
            zone_id=vom_id,
            zone_type="vomitory",
            display_name=f"Vomitory {section_num}",
        )

    # ── Connect edges ──
    _connect(nodes, "gate_north", "concourse_north", 80, ramp=True, tactile=True)
    _connect(nodes, "gate_south", "concourse_south", 80, ramp=True, tactile=True)
    _connect(nodes, "gate_east", "concourse_east", 80, ramp=True, tactile=True)
    _connect(nodes, "gate_west", "concourse_west", 80, ramp=True, tactile=True)

    # Concourse ring (connected for circumnavigation)
    _connect(nodes, "concourse_north", "concourse_east", 200, ramp=True)
    _connect(nodes, "concourse_east", "concourse_south", 200, ramp=True)
    _connect(nodes, "concourse_south", "concourse_west", 200, ramp=True)
    _connect(nodes, "concourse_west", "concourse_north", 200, ramp=True)

    # Concourse → seating via vomitories
    _connect(nodes, "concourse_north", "vomitory_1", 30)
    _connect(nodes, "concourse_east", "vomitory_2", 30)
    _connect(nodes, "concourse_south", "vomitory_3", 30)
    _connect(nodes, "concourse_west", "vomitory_4", 30)

    for i in range(1, 5):
        # Stairs-only path for ambulatory users
        _connect(nodes, f"vomitory_{i}", f"seating_{i}", 40, stairs=True, wheelchair=False)
        # Wheelchair-accessible ramp path (slightly longer distance)
        _connect(nodes, f"vomitory_{i}", f"seating_{i}", 55, ramp=True, wheelchair=True,
                 desc=f"Accessible ramp to Section {i}")
        _connect(nodes, f"vomitory_{i}", f"seating_{i + 4}", 50,
                 stairs=True, elevator=True, desc="Elevator to upper level")

    # Concourse → facilities
    _connect(nodes, "concourse_north", "concession_north", 25)
    _connect(nodes, "concourse_south", "concession_south", 25)
    _connect(nodes, "concourse_north", "restroom_north", 20, tactile=True)
    _connect(nodes, "concourse_south", "restroom_south", 20, tactile=True)
    _connect(nodes, "concourse_east", "restroom_east", 20, tactile=True)
    _connect(nodes, "concourse_west", "restroom_west", 20, tactile=True)

    # Medical access
    _connect(nodes, "concourse_north", "medical_main", 60, elevator=True, tactile=True)
    _connect(nodes, "concourse_south", "medical_field", 40, ramp=True)

    # Transit hub connection
    _connect(nodes, "gate_north", "transit_hub", 150, ramp=True, tactile=True,
             desc="Covered walkway to metro/bus station")
    _connect(nodes, "gate_east", "transit_hub", 200, ramp=True)

    return nodes


def _connect(
    nodes: dict[str, VenueNode],
    from_id: str,
    to_id: str,
    distance: float,
    *,
    wheelchair: bool = True,
    elevator: bool = False,
    ramp: bool = False,
    stairs: bool = False,
    tactile: bool = False,
    width: float = 3.0,
    desc: str = "",
) -> None:
    """Add a bidirectional edge between two nodes."""
    edge_forward = VenueEdge(
        to_zone=to_id,
        distance_meters=distance,
        wheelchair_accessible=wheelchair,
        has_elevator=elevator,
        has_ramp=ramp,
        has_stairs=stairs,
        has_tactile_markers=tactile,
        width_meters=width,
        description=desc or f"Corridor from {from_id} to {to_id}",
    )
    edge_back = VenueEdge(
        to_zone=from_id,
        distance_meters=distance,
        wheelchair_accessible=wheelchair,
        has_elevator=elevator,
        has_ramp=ramp,
        has_stairs=stairs,
        has_tactile_markers=tactile,
        width_meters=width,
        description=desc or f"Corridor from {to_id} to {from_id}",
    )
    if from_id in nodes:
        nodes[from_id].edges.append(edge_forward)
    if to_id in nodes:
        nodes[to_id].edges.append(edge_back)
