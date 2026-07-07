"""Unit tests for models Pydantic boundary validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import CrowdQuery, FanAssistantQuery, SustainabilityQuery


def test_crowd_query_bounds_validation() -> None:
    """Confirms CrowdQuery enforces elapsed_minutes constraints."""
    # Under boundary
    with pytest.raises(ValidationError):
        CrowdQuery(
            zone_id="concourse_north",
            elapsed_minutes=-10,
        )

    # Over boundary
    with pytest.raises(ValidationError):
        CrowdQuery(
            zone_id="concourse_north",
            elapsed_minutes=700, # Max is 600
        )


def test_sustainability_query_attendance_boundaries() -> None:
    """Verifies SustainabilityQuery blocks impossible attendance numbers."""
    with pytest.raises(ValidationError):
        SustainabilityQuery(
            attendance=-5,
        )

    with pytest.raises(ValidationError):
        SustainabilityQuery(
            attendance=120000, # Max is 110000
        )


def test_fan_query_character_limit() -> None:
    """Ensures query length bounds block malicious/unusually long prompt payloads."""
    with pytest.raises(ValidationError):
        FanAssistantQuery(
            question="A" * 1500, # Max is 1000
        )
