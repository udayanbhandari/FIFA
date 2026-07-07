"""Dependency Injection providers for StadiumIQ route handlers.

Configuration driven class selection. Wires repositories and settings.
"""

from __future__ import annotations

from fastapi import Depends

from app.config import Settings, get_settings
from app.repository.base import FanQueryRepository
from app.repository.firestore_repo import FirestoreFanQueryRepository
from app.repository.memory_repo import MemoryFanQueryRepository

# Singleton in-memory store for development/test configurations
_in_memory_repo_instance = MemoryFanQueryRepository()


def get_repository(settings: Settings = Depends(get_settings)) -> FanQueryRepository:
    """Resolve and return configured FanQueryRepository provider.

    Uses setting config parameter feature flags to switch implementations.
    FastAPI's dependency system caches the result per request.
    """
    if settings.use_firestore:
        return FirestoreFanQueryRepository(project_id=settings.gcp_project_id)
    return _in_memory_repo_instance
