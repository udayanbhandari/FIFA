"""Repository protocols for data persistence in StadiumIQ.

Uses Python structural typing (Protocol) to support multiple
interchangeable storage engines (Firestore / in-memory).
"""

from __future__ import annotations

from typing import Protocol

from app.models import FanQueryRecord


class FanQueryRepository(Protocol):
    """Protocol defining storage operations for fan assistant interactions."""

    def add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Synchronously persist a new fan interaction record."""
        ...

    def list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Synchronously list all assistant interactions for a specific device."""
        ...

    async def async_add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Asynchronously persist a new fan interaction record (non-blocking)."""
        ...

    async def async_list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Asynchronously list all assistant interactions for a specific device."""
        ...
