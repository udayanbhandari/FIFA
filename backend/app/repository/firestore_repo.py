"""Firestore storage integration for StadiumIQ.

Uses lazy SDK loading. Wraps synchronous Google cloud library operations
in asyncio.to_thread calls to avoid blocking the FastAPI event loop.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from app.models import FanQueryRecord
from app.repository.base import FanQueryRepository

if TYPE_CHECKING:
    from google.cloud import firestore


class FirestoreFanQueryRepository(FanQueryRepository):
    """Google Cloud Firestore implementation of FanQueryRepository protocol."""

    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self._db: firestore.Client | None = None

    def _get_client(self) -> firestore.Client:
        """Lazily initialize client instance when first requested."""
        if self._db is None:
            from google.cloud import firestore
            self._db = firestore.Client(project=self.project_id)
        return self._db

    def add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Synchronously write a fan interaction snapshot into Firestore."""
        db = self._get_client()

        record_id = record.id or str(uuid.uuid4())
        created_at = record.created_at or datetime.now(timezone.utc)

        doc_ref = db.collection("fan_queries").document(record_id)
        data = {
            "id": record_id,
            "device_id": record.device_id,
            "question": record.question,
            "answer": record.answer,
            "source": record.source,
            "language": record.language.value,
            "created_at": created_at,
        }
        doc_ref.set(data)

        # Return a copy representing what was stored
        stored = record.model_copy()
        stored.id = record_id
        stored.created_at = created_at
        return stored

    def list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Synchronously search and filter records by device ID index."""
        db = self._get_client()
        query = (
            db.collection("fan_queries")
            .where("device_id", "==", device_id)
            .order_by("created_at", direction="DESCENDING")
        )

        records = []
        for doc in query.stream():
            data = doc.to_dict()
            records.append(
                FanQueryRecord(
                    id=data["id"],
                    device_id=data["device_id"],
                    question=data["question"],
                    answer=data["answer"],
                    source=data["source"],
                    language=data["language"],
                    created_at=data["created_at"],
                )
            )
        return records

    async def async_add(self, record: FanQueryRecord) -> FanQueryRecord:
        """Asynchronously write record by wrapping client execution in a thread pool."""
        return await asyncio.to_thread(self.add, record)

    async def async_list_by_device(self, device_id: str) -> list[FanQueryRecord]:
        """Asynchronously query records by wrapping client execution in a thread pool."""
        return await asyncio.to_thread(self.list_by_device, device_id)
