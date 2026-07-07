"""In-memory dictionary repository implementation.

Provides database fallback capabilities for local dev and fast tests.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models import FanQueryRecord
from app.repository.base import FanQueryRepository


class MemoryFanQueryRepository(FanQueryRepository):
    """In-memory implementation of the FanQueryRepository protocol."""

    def __init__(self) -> None:
        # dict: record_id -> FanQueryRecord
        self._records: dict[str, FanQueryRecord] = {}

    def add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Synchronously persist a new record to memory."""
        record_copy = record.model_copy()
        if not record_copy.id:
            record_copy.id = str(uuid.uuid4())
        if not record_copy.created_at:
            record_copy.created_at = datetime.now(timezone.utc)

        self._records[record_copy.id] = record_copy
        return record_copy

    def list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Synchronously retrieve records matched to device_id."""
        matching = [r.model_copy() for r in self._records.values() if r.device_id == device_id]
        # Sort by creation timestamp descending
        matching.sort(key=lambda r: r.created_at or datetime.min, reverse=True)
        return matching

    async def async_add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Asynchronously persist record (calls sync implementation directly)."""
        return self.add(record)

    async def async_list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Asynchronously retrieve records (calls sync implementation directly)."""
        return self.list_by_device(device_id)
