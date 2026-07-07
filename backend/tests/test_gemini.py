"""Unit tests for the Gemini AI assistant integration.

Mocks external calls to google.genai.Client to run completely offline.
Tests structured schema generation, whitelists, caching, and fallbacks.
"""

from __future__ import annotations

import json
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from app.assistant.gemini import get_fan_assistance
from app.config import get_settings
from app.models import FanAssistantQuery, Language


@pytest.fixture
def mock_genai_client() -> Generator[MagicMock, None, None]:
    """Mock out the genai.Client instance return value."""
    with patch("app.assistant.gemini._get_gemini_client") as mock_factory:
        mock_client = MagicMock()
        mock_factory.return_value = mock_client
        yield mock_client


async def test_gemini_returns_valid_structured_response(mock_genai_client: MagicMock) -> None:
    """Confirms Gemini responses are parsed and structured correctly."""
    # Set settings configuration
    settings = get_settings()
    settings.use_gemini = True

    # Setup mock response body text representation
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "answer": "Go to restroom_north near Section 2.",
        "confidence": 0.95,
        "zone_reference": "restroom_north",
        "suggested_actions": [
            {"action": "find_nearest", "details": "View route map"}
        ]
    })
    mock_genai_client.models.generate_content.return_value = mock_response

    query = FanAssistantQuery(
        question="Where is the restroom?",
        language=Language.EN,
        current_zone="concourse_north"
    )

    # In conftest, settings has use_gemini = False. Let's patch it inline
    with patch("app.assistant.gemini.get_settings") as mock_settings_fn:
        mock_settings = MagicMock()
        mock_settings.use_gemini = True
        mock_settings.gemini_prompt_version = "v1"
        mock_settings_fn.return_value = mock_settings

        # Resolve async call
        res = await get_fan_assistance(query)

        assert res.source == "gemini"
        assert res.confidence == 0.95
        assert res.zone_reference == "restroom_north"
        assert len(res.suggested_actions) == 1
        assert res.suggested_actions[0].action == "find_nearest"


async def test_gemini_validation_catches_bad_responses(mock_genai_client: MagicMock) -> None:
    """Verifies that invalid/oversized AI outputs trigger fallback engine."""
    # Mock return of huge/corrupt JSON response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "answer": "A" * 2000, # Too long, max 1000 characters
        "confidence": -2.0,
        "zone_reference": "non_existent_zone",
        "suggested_actions": []
    })
    mock_genai_client.models.generate_content.return_value = mock_response

    query = FanAssistantQuery(
        question="Where is the restroom?",
        language=Language.EN,
    )

    with patch("app.assistant.gemini.get_settings") as mock_settings_fn:
        mock_settings = MagicMock()
        mock_settings.use_gemini = True
        mock_settings.gemini_prompt_version = "v1"
        mock_settings_fn.return_value = mock_settings

        res = await get_fan_assistance(query)
        # Validation failure should cause fallback to rules
        assert res.source == "rules"
        assert res.confidence == 0.5


async def test_fallback_on_genai_sdk_exception(mock_genai_client: MagicMock) -> None:
    """Asserts that GenAI connection exceptions degrade gracefully to rules."""
    # Trigger client SDK exception
    mock_genai_client.models.generate_content.side_effect = Exception("Vertex AI Service Unavailable")

    query = FanAssistantQuery(
        question="Where is the restroom?",
        language=Language.EN,
    )

    with patch("app.assistant.gemini.get_settings") as mock_settings_fn:
        mock_settings = MagicMock()
        mock_settings.use_gemini = True
        mock_settings.gemini_prompt_version = "v1"
        mock_settings_fn.return_value = mock_settings

        res = await get_fan_assistance(query)
        assert res.source == "rules"
        # Should populate basic placeholder answers
        assert "restroom" in res.answer.lower()
