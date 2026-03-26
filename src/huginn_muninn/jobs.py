"""Thread-safe in-memory job store for async job tracking."""
from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStore:
    """Thread-safe in-memory dict of jobs with FIFO eviction."""

    def __init__(self, max_jobs: int = 1000):
        self._lock = threading.RLock()
        self._jobs: OrderedDict[str, dict] = OrderedDict()
        self._max_jobs = max_jobs

    def create(
        self,
        claim: str,
        method: str,
        callback_url: str | None = None,
        session_id: int | None = None,
        deep_sources: bool = False,
    ) -> str:
        job_id = uuid.uuid4().hex[:16]
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "id": job_id,
            "claim": claim,
            "method": method,
            "status": JobStatus.PENDING,
            "callback_url": callback_url,
            "session_id": session_id,
            "deep_sources": deep_sources,
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._jobs[job_id] = job
            self._evict()
        return job_id

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def update(self, job_id: str, **kwargs) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            for key, value in kwargs.items():
                if key in job:
                    job[key] = value
            job["updated_at"] = datetime.now(timezone.utc).isoformat()
            return dict(job)

    def list_jobs(self, limit: int = 50) -> list[dict]:
        with self._lock:
            jobs = list(self._jobs.values())
        return [dict(j) for j in reversed(jobs[-limit:])]

    def _evict(self):
        """Remove oldest completed/failed jobs when over capacity."""
        while len(self._jobs) > self._max_jobs:
            for job_id, job in self._jobs.items():
                if job["status"] in (JobStatus.COMPLETED, JobStatus.FAILED):
                    del self._jobs[job_id]
                    break
            else:
                break
