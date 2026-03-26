"""Tests for BatchStore."""
from __future__ import annotations

from huginn_muninn.batch import BatchStore
from huginn_muninn.jobs import JobStatus, JobStore


def _make_stores(max_jobs=100, max_batches=200):
    js = JobStore(max_jobs=max_jobs)
    bs = BatchStore(js, max_batches=max_batches)
    return js, bs


class TestBatchStore:
    def test_create_returns_batch_id(self):
        js, bs = _make_stores()
        jid = js.create("claim1", "check")
        batch_id = bs.create([jid])
        assert len(batch_id) == 16

    def test_get_returns_batch(self):
        js, bs = _make_stores()
        jid = js.create("claim1", "check")
        batch_id = bs.create([jid], session_id=42)
        batch = bs.get(batch_id)
        assert batch is not None
        assert batch["id"] == batch_id
        assert batch["job_ids"] == [jid]
        assert batch["session_id"] == 42
        assert "created_at" in batch

    def test_get_missing_returns_none(self):
        js, bs = _make_stores()
        assert bs.get("nonexistent") is None

    def test_status_all_pending(self):
        js, bs = _make_stores()
        jid1 = js.create("c1", "check")
        jid2 = js.create("c2", "check")
        batch_id = bs.create([jid1, jid2])
        batch = bs.get(batch_id)
        assert batch["status"] == "pending"

    def test_status_running(self):
        js, bs = _make_stores()
        jid1 = js.create("c1", "check")
        jid2 = js.create("c2", "check")
        js.update(jid1, status=JobStatus.RUNNING)
        batch_id = bs.create([jid1, jid2])
        assert bs.get(batch_id)["status"] == "running"

    def test_status_completed(self):
        js, bs = _make_stores()
        jid1 = js.create("c1", "check")
        jid2 = js.create("c2", "check")
        js.update(jid1, status=JobStatus.COMPLETED)
        js.update(jid2, status=JobStatus.COMPLETED)
        batch_id = bs.create([jid1, jid2])
        assert bs.get(batch_id)["status"] == "completed"

    def test_status_partial(self):
        js, bs = _make_stores()
        jid1 = js.create("c1", "check")
        jid2 = js.create("c2", "check")
        js.update(jid1, status=JobStatus.COMPLETED)
        js.update(jid2, status=JobStatus.FAILED)
        batch_id = bs.create([jid1, jid2])
        assert bs.get(batch_id)["status"] == "partial"

    def test_status_all_failed(self):
        js, bs = _make_stores()
        jid1 = js.create("c1", "check")
        jid2 = js.create("c2", "check")
        js.update(jid1, status=JobStatus.FAILED)
        js.update(jid2, status=JobStatus.FAILED)
        batch_id = bs.create([jid1, jid2])
        assert bs.get(batch_id)["status"] == "failed"

    def test_eviction(self):
        js, bs = _make_stores(max_batches=2)
        jid = js.create("c1", "check")
        b1 = bs.create([jid])
        b2 = bs.create([jid])
        b3 = bs.create([jid])
        # b1 should be evicted
        assert bs.get(b1) is None
        assert bs.get(b2) is not None
        assert bs.get(b3) is not None
