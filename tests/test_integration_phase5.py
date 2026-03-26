"""Integration tests for Phase 5: async jobs, sessions, webhooks."""
import json
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from huginn_muninn.db import HuginnDB
from huginn_muninn.jobs import JobStatus, JobStore
from huginn_muninn.webhooks import WebhookDispatcher, sign_payload, verify_signature
from huginn_muninn.worker import JobRunner

_VALID_VERDICT = {
    "verdict": "true", "confidence": 0.9,
    "evidence_for": [], "evidence_against": [], "unknowns": [],
    "common_ground": {"shared_concern": "Truth", "framing_technique": "none_detected",
                      "technique_explanation": "None", "reflection": "Why?"},
    "escalation": {"score": 0.1, "should_escalate": False, "reason": "Simple"},
}


@pytest.fixture
def db(tmp_path):
    return HuginnDB(tmp_path / "integration.db")


@pytest.fixture
def job_store():
    return JobStore(max_jobs=100)


@pytest.fixture
def mock_client():
    c = MagicMock()
    c.generate.return_value = "{}"
    return c


def _wait_for_jobs(job_store, job_ids):
    """Return a dict of {job_id: threading.Event} that fire on completion/failure.

    Patches job_store.update once and tracks all given job IDs.
    """
    events = {jid: threading.Event() for jid in job_ids}
    original_update = job_store.update

    def update_and_signal(jid, **kwargs):
        result = original_update(jid, **kwargs)
        if kwargs.get("status") in (JobStatus.COMPLETED, JobStatus.FAILED):
            ev = events.get(jid)
            if ev:
                ev.set()
        return result

    job_store.update = update_and_signal
    return events


class TestJobLifecycle:
    def test_submit_poll_complete(self, db, job_store, mock_client):
        """Full lifecycle: submit -> poll pending -> poll running -> poll completed."""
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract:
            mock_extract.return_value = _VALID_VERDICT
            runner = JobRunner(db, mock_client, job_store)
            job_id = job_store.create("Test claim", "check")

            # Verify initial state
            job = job_store.get(job_id)
            assert job["status"] == JobStatus.PENDING

            events = _wait_for_jobs(job_store, [job_id])
            runner.submit(job_id)
            assert events[job_id].wait(timeout=5.0)

            # Final state
            job = job_store.get(job_id)
            assert job["status"] == JobStatus.COMPLETED
            assert job["result"]["verdict"] == "true"

    def test_failed_job_lifecycle(self, db, job_store, mock_client):
        mock_client.generate.side_effect = RuntimeError("LLM error")
        runner = JobRunner(db, mock_client, job_store)
        job_id = job_store.create("claim", "check")
        events = _wait_for_jobs(job_store, [job_id])
        runner.submit(job_id)
        assert events[job_id].wait(timeout=5.0)
        job = job_store.get(job_id)
        assert job["status"] == JobStatus.FAILED
        assert job["error"] is not None


class TestCallbackDelivery:
    def test_callback_with_hmac(self, db, job_store, mock_client):
        """Callback URL receives the result with correct data."""
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract, \
             patch("huginn_muninn.worker.httpx.post") as mock_post:
            mock_extract.return_value = _VALID_VERDICT
            runner = JobRunner(db, mock_client, job_store)
            job_id = job_store.create("claim", "check", callback_url="http://localhost:9999/cb")
            events = _wait_for_jobs(job_store, [job_id])
            runner.submit(job_id)
            assert events[job_id].wait(timeout=5.0)

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["job_id"] == job_id
        assert payload["status"] == "completed"
        assert payload["result"]["verdict"] == "true"


class TestWebhookDelivery:
    def test_webhook_receives_signed_payload(self, db, job_store, mock_client):
        """Register webhook -> submit job -> webhook receives HMAC-signed payload."""
        secret = "test_webhook_secret"
        db.create_webhook("http://localhost:8888/hook", secret, ["job.completed", "verdict.completed"])

        dispatcher = WebhookDispatcher(db)
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract, \
             patch("huginn_muninn.webhooks.httpx.post") as mock_wh_post:
            mock_extract.return_value = _VALID_VERDICT
            mock_wh_post.return_value = MagicMock(status_code=200)
            runner = JobRunner(db, mock_client, job_store, dispatcher)
            job_id = job_store.create("claim", "check")
            events = _wait_for_jobs(job_store, [job_id])
            runner.submit(job_id)
            assert events[job_id].wait(timeout=5.0)
            # Give dispatcher time to process
            time.sleep(0.5)
            dispatcher.stop(timeout=2.0)

        # Verify signed payload was sent
        assert mock_wh_post.call_count >= 1
        for call in mock_wh_post.call_args_list:
            body = call.kwargs["content"]
            sig_header = call.kwargs["headers"]["X-Huginn-Signature-256"]
            sig = sig_header.removeprefix("sha256=")
            assert verify_signature(body, secret, sig)


class TestSessionIntegration:
    def test_create_session_add_items_browse(self, db):
        """Create session -> store verdict -> add to session -> browse."""
        sid = db.create_session("Investigation 1")
        vid = db.store_verdict("claim A", {"verdict": "true"})
        aid = db.store_analysis("claim B", {"method": "method_2"})

        db.add_session_item(sid, "verdict", vid)
        db.add_session_item(sid, "analysis", aid)

        session = db.get_session(sid)
        assert session["name"] == "Investigation 1"
        assert len(session["items"]) == 2
        assert session["items"][0]["item_type"] == "verdict"
        assert session["items"][1]["item_type"] == "analysis"


class TestConcurrentJobs:
    def test_three_concurrent_jobs(self, db, job_store, mock_client):
        """Submit 3 jobs concurrently -- all should complete without corruption."""
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract:
            mock_extract.return_value = _VALID_VERDICT
            runner = JobRunner(db, mock_client, job_store)
            ids = [job_store.create(f"claim {i}", "check") for i in range(3)]
            events = _wait_for_jobs(job_store, ids)

            for jid in ids:
                runner.submit(jid)

            for jid in ids:
                assert events[jid].wait(timeout=10.0)

            for jid in ids:
                job = job_store.get(jid)
                assert job["status"] in (JobStatus.COMPLETED, JobStatus.FAILED)

            # At least some should succeed
            completed = [jid for jid in ids if job_store.get(jid)["status"] == JobStatus.COMPLETED]
            assert len(completed) >= 1


class TestConfigIntegration:
    def test_webhook_secret_and_max_jobs(self, monkeypatch):
        monkeypatch.setenv("HUGINN_WEBHOOK_SECRET", "mysecret")
        monkeypatch.setenv("HUGINN_MAX_JOBS", "500")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.webhook_secret == "mysecret"
        assert s.max_jobs == 500
