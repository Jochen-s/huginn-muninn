"""In-memory batch store for grouping multiple jobs."""
from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

from huginn_muninn.jobs import JobStatus, JobStore


class BatchStore:
    """Thread-safe in-memory store for batch job groups."""

    def __init__(self, job_store: JobStore, max_batches: int = 200):
        self._lock = threading.RLock()
        self._batches: OrderedDict[str, dict] = OrderedDict()
        self._job_store = job_store
        self._max_batches = max_batches

    def create(
        self,
        job_ids: list[str],
        session_id: int | None = None,
    ) -> str:
        batch_id = uuid.uuid4().hex[:16]
        now = datetime.now(timezone.utc).isoformat()
        batch = {
            "id": batch_id,
            "job_ids": job_ids,
            "session_id": session_id,
            "created_at": now,
        }
        with self._lock:
            self._batches[batch_id] = batch
            self._evict()
        return batch_id

    def get(self, batch_id: str) -> dict | None:
        with self._lock:
            batch = self._batches.get(batch_id)
            if batch is None:
                return None
            batch = dict(batch)
        batch["status"] = self._compute_status(batch["job_ids"])
        return batch

    def _compute_status(self, job_ids: list[str]) -> str:
        """Derive batch status from constituent job statuses."""
        statuses = set()
        for jid in job_ids:
            job = self._job_store.get(jid)
            if job:
                s = job["status"]
                statuses.add(s.value if hasattr(s, "value") else s)
            else:
                statuses.add("unknown")

        if not statuses:
            return "unknown"
        if statuses == {"completed"}:
            return "completed"
        if statuses == {"failed"}:
            return "failed"
        if statuses == {"pending"}:
            return "pending"
        if "running" in statuses or "pending" in statuses:
            return "running"
        # Mix of completed and failed
        if statuses <= {"completed", "failed"}:
            return "partial"
        return "running"

    def _evict(self):
        while len(self._batches) > self._max_batches:
            self._batches.popitem(last=False)
