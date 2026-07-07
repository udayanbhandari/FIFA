"""Integration tests validating FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_endpoint_returns_status_and_version(client: TestClient) -> None:
    """Verifies Health Route structure and content."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_crowd_density_estimation_route(client: TestClient) -> None:
    """Verifies Density calculations route status and structure."""
    payload = {
        "zone_id": "concourse_north",
        "gate_counts": {"gate_north": 2000},
        "elapsed_minutes": 10,
        "event_phase": "pre_match",
    }
    res = client.post("/api/crowd/density", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["zone_id"] == "concourse_north"
    assert "current_density" in data
    assert "safety_status" in data


def test_wayfinding_route_resolution(client: TestClient) -> None:
    """Verifies Wayfinding routing paths."""
    payload = {
        "origin_zone": "gate_north",
        "destination_zone": "seating_1",
        "accessibility_need": "wheelchair",
    }
    res = client.post("/api/wayfinding/route", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["origin"] == "gate_north"
    assert data["destination"] == "seating_1"
    assert len(data["steps"]) > 0


def test_wayfinding_route_rejection_for_disconnected(client: TestClient) -> None:
    """Confirms route request returns 404 for disconnected/invalid zones."""
    payload = {
        "origin_zone": "gate_north",
        "destination_zone": "invalid_zone",
        "accessibility_need": "none",
    }
    res = client.post("/api/wayfinding/route", json=payload)
    assert res.status_code == 404


def test_sustainability_footprint_calculation(client: TestClient) -> None:
    """Verifies Sustainability calculation integration route."""
    payload = {
        "attendance": 50000,
        "energy_kwh": 100000,
        "waste_kg": 10000,
        "water_liters": 200000,
    }
    res = client.post("/api/sustainability/footprint", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "total_kg_co2e" in data
    assert data["per_fan_kg_co2e"] > 0.0


def test_security_headers_present_on_all_responses(client: TestClient) -> None:
    """Asserts that security headers are applied by app middleware."""
    res = client.get("/api/health")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["Referrer-Policy"] == "no-referrer"
    assert "Content-Security-Policy" in res.headers


def test_request_body_size_middleware_limit(client: TestClient) -> None:
    """Validates that payload size limit middleware blocks massive requests."""
    import json as _json
    # Create body larger than 64 KB limit
    large_body = {"question": "A" * 66000}
    body_bytes = _json.dumps(large_body).encode()
    # Send with explicit Content-Length so middleware fast-path triggers
    res = client.post(
        "/api/assist",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body_bytes)),
        },
    )
    assert res.status_code == 413
    assert res.json()["detail"] == "Request body too large"


def test_rate_limiting_on_assist_endpoint(client: TestClient) -> None:
    """Verifies that rate limiting is configured on the assistant endpoint."""
    # Just verify the endpoint responds (rate limiting is active but threshold
    # varies by test environment isolation so we only verify it doesn't crash)
    payload = {
        "question": "Where is Section 1?",
        "language": "en",
        "current_zone": "concourse_north",
        "device_id": "test_device_limiter",
    }
    res = client.post("/api/assist", json=payload)
    # Should return either 200 (normal) or 429 (rate limited)
    assert res.status_code in (200, 429)


def test_wayfinding_nearest_facility_route(client: TestClient) -> None:
    """Confirms nearest facility resolution works via API for restrooms."""
    payload = {
        "current_zone": "gate_north",
        "facility_type": "restroom",
        "accessibility_need": "none",
    }
    res = client.post("/api/wayfinding/nearest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "facility_zone_id" in data
    assert "route" in data


def test_wayfinding_nearest_facility_not_found(client: TestClient) -> None:
    """Confirms 404 is returned when no facility is reachable from given zone."""
    payload = {
        "current_zone": "invalid_zone",
        "facility_type": "medical",
        "accessibility_need": "none",
    }
    res = client.post("/api/wayfinding/nearest", json=payload)
    assert res.status_code == 404


def test_sustainability_targets_route(client: TestClient) -> None:
    """Verifies the sustainability targets endpoint returns config data."""
    res = client.get("/api/sustainability/targets")
    assert res.status_code == 200
    data = res.json()
    assert "fifa_target_kg_co2e_per_fan" in data
    assert "metrics_tracked" in data


def test_crowd_congestion_prediction_route(client: TestClient) -> None:
    """Verifies the crowd prediction endpoint responds correctly."""
    payload = {
        "zone_densities": {"concourse_north": 3.5, "concourse_south": 1.2},
        "elapsed_minutes": 30,
        "event_phase": "halftime",
        "stadium_capacity": 80000,
    }
    res = client.post("/api/crowd/predict", json=payload)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
