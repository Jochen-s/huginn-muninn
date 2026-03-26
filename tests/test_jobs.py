"""Tests for in-memory job store."""
import threading

import pytest

from huginn_muninn.jobs import JobStatus, JobStore


@pytest.fixture
def store():
    return JobStore(max_jobs=5)


class TestJobCreate:
    def test_create_returns_id(self, store):
        job_id = store.create("test claim", "check")
        assert isinstance(job_id, str)
        assert len(job_id) == 16

    def test_create_sets_pending(self, store):
        job_id = store.create("claim", "check")
        job = store.get(job_id)
        assert job["status"] == JobStatus.PENDING

    def test_create_stores_fields(self, store):
        job_id = store.create("claim", "analyze", callback_url="http://example.com/cb", session_id=42)
        job = store.get(job_id)
        assert job["claim"] == "claim"
        assert job["method"] == "analyze"
        assert job["callback_url"] == "http://example.com/cb"
        assert job["session_id"] == 42


class TestJobGet:
    def test_get_nonexistent_returns_none(self, store):
        assert store.get("doesnotexist") is None

    def test_get_returns_copy(self, store):
        job_id = store.create("claim", "check")
        j1 = store.get(job_id)
        j2 = store.get(job_id)
        assert j1 is not j2
        assert j1 == j2


class TestJobUpdate:
    def test_update_status(self, store):
        job_id = store.create("claim", "check")
        updated = store.update(job_id, status=JobStatus.RUNNING)
        assert updated["status"] == JobStatus.RUNNING

    def test_update_result(self, store):
        job_id = store.create("claim", "check")
        store.update(job_id, status=JobStatus.COMPLETED, result={"verdict": "true"})
        job = store.get(job_id)
        assert job["result"] == {"verdict": "true"}

    def test_update_nonexistent_returns_none(self, store):
        assert store.update("nope", status=JobStatus.RUNNING) is None

    def test_update_ignores_unknown_keys(self, store):
        job_id = store.create("claim", "check")
        updated = store.update(job_id, unknown_field="value")
        assert "unknown_field" not in updated


class TestJobList:
    def test_list_empty(self, store):
        assert store.list_jobs() == []

    def test_list_returns_recent_first(self, store):
        store.create("first", "check")
        store.create("second", "check")
        jobs = store.list_jobs()
        assert jobs[0]["claim"] == "second"
        assert jobs[1]["claim"] == "first"

    def test_list_respects_limit(self, store):
        for i in range(5):
            store.create(f"claim {i}", "check")
        jobs = store.list_jobs(limit=2)
        assert len(jobs) == 2


class TestEviction:
    def test_evicts_completed_when_over_max(self):
        store = JobStore(max_jobs=3)
        ids = []
        for i in range(3):
            ids.append(store.create(f"claim {i}", "check"))
        store.update(ids[0], status=JobStatus.COMPLETED)
        # Adding a 4th should evict the completed one
        store.create("claim 3", "check")
        assert store.get(ids[0]) is None
        assert len(store.list_jobs()) == 3

    def test_does_not_evict_running_jobs(self):
        store = JobStore(max_jobs=2)
        id1 = store.create("claim 1", "check")
        store.update(id1, status=JobStatus.RUNNING)
        store.create("claim 2", "check")
        # Adding a 3rd -- neither is completed, so no eviction possible
        store.create("claim 3", "check")
        assert len(store.list_jobs()) == 3


class TestThreadSafety:
    def test_concurrent_creates(self):
        store = JobStore(max_jobs=1000)
        ids = []
        lock = threading.Lock()

        def create_jobs():
            for i in range(50):
                job_id = store.create(f"claim-{threading.current_thread().name}-{i}", "check")
                with lock:
                    ids.append(job_id)

        threads = [threading.Thread(target=create_jobs) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == 200
        assert len(set(ids)) == 200
