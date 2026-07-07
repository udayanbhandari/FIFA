"""Pytest configuration fixtures for StadiumIQ backend testing."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings


@pytest.fixture(autouse=True)
def test_settings_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force settings overrides for unit testing environment.

    Guarantees no real external Google APIs are hit.
    Sets environment variables before clearing the lru_cache so
    the next call to get_settings() picks up test values.
    """
    monkeypatch.setenv("USE_GEMINI", "false")
    monkeypatch.setenv("USE_FIRESTORE", "false")
    monkeypatch.setenv("GCP_PROJECT_ID", "stadium-test-project")
    # Clear the cached instance so settings re-read env vars
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client instance for integration testing."""
    # Import here to ensure middleware is fully initialised after settings patch
    from app.main import create_app
    return TestClient(create_app())
