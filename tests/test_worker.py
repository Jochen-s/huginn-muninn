"""Tests for background job runner."""
import threading
from unittest.mock import MagicMock, patch

import pytest

from huginn_muninn.jobs import JobStatus, JobStore
from huginn_muninn.worker import JobRunner

_VALID_VERDICT = {
    "verdict": "true", "confidence": 0.9,
    "evidence_for": [], "evidence_against": [], "unknowns": [],
    "common_ground": {"shared_concern": "Truth", "framing_technique": "none_detected",
                      "technique_explanation": "None", "reflection": "Why?"},
    "escalation": {"score": 0.1, "should_escalate": False, "reason": "Simple"},
}


@pytest.fixture
def job_store():
    return JobStore(max_jobs=100)


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.store_verdict.return_value = 1
    db.store_analysis.return_value = 1
    return db


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def runner(mock_db, mock_client, job_store):
    return JobRunner(mock_db, mock_client, job_store)


def _wait_for_job(job_store, job_id, timeout=5.0):
    """Helper: block until job reaches terminal state."""
    done = threading.Event()
    original_update = job_store.update

    def update_and_signal(jid, **kwargs):
        result = original_update(jid, **kwargs)
        if kwargs.get("status") in (JobStatus.COMPLETED, JobStatus.FAILED):
            done.set()
        return result

    job_store.update = update_and_signal
    return done, update_and_signal


class TestJobDispatch:
    def test_submit_runs_job_to_completion(self, runner, job_store, mock_client):
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract:
            mock_extract.return_value = _VALID_VERDICT
            mock_client.generate.return_value = "{}"
            job_id = job_store.create("test claim", "check")
            done, patched_update = _wait_for_job(job_store, job_id)
            job_store.update = patched_update
            runner.submit(job_id)
            assert done.wait(timeout=5.0)
            job = job_store.get(job_id)
            assert job["status"] == JobStatus.COMPLETED
            assert job["result"] is not None

    def test_failed_job_sets_error(self, runner, job_store, mock_client):
        mock_client.generate.side_effect = RuntimeError("LLM down")
        job_id = job_store.create("test claim", "check")
        done, patched_update = _wait_for_job(job_store, job_id)
        job_store.update = patched_update
        runner.submit(job_id)
        assert done.wait(timeout=5.0)
        job = job_store.get(job_id)
        assert job["status"] == JobStatus.FAILED
        assert "LLM down" in job["error"]

    def test_unknown_method_fails(self, runner, job_store):
        job_id = job_store.create("claim", "unknown_method")
        done, patched_update = _wait_for_job(job_store, job_id)
        job_store.update = patched_update
        runner.submit(job_id)
        assert done.wait(timeout=5.0)
        job = job_store.get(job_id)
        assert job["status"] == JobStatus.FAILED
        assert "Unknown method" in job["error"]


class TestCallback:
    def test_fires_callback_on_success(self, runner, job_store, mock_client):
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract, \
             patch("huginn_muninn.worker.httpx.post") as mock_post:
            mock_extract.return_value = _VALID_VERDICT
            mock_client.generate.return_value = "{}"
            job_id = job_store.create("claim", "check", callback_url="http://example.com/cb")
            done, patched_update = _wait_for_job(job_store, job_id)
            job_store.update = patched_update
            runner.submit(job_id)
            assert done.wait(timeout=5.0)
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs.args[0] == "http://example.com/cb"

    def test_no_callback_when_url_missing(self, runner, job_store, mock_client):
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract, \
             patch("huginn_muninn.worker.httpx.post") as mock_post:
            mock_extract.return_value = _VALID_VERDICT
            mock_client.generate.return_value = "{}"
            job_id = job_store.create("claim", "check")
            done, patched_update = _wait_for_job(job_store, job_id)
            job_store.update = patched_update
            runner.submit(job_id)
            assert done.wait(timeout=5.0)
        mock_post.assert_not_called()


class TestWebhookDispatch:
    def test_dispatches_webhook_on_completion(self, mock_db, mock_client, job_store):
        mock_dispatcher = MagicMock()
        runner_with_wh = JobRunner(mock_db, mock_client, job_store, mock_dispatcher)
        with patch("huginn_muninn.llm.extract_json_from_response") as mock_extract:
            mock_extract.return_value = _VALID_VERDICT
            mock_client.generate.return_value = "{}"
            job_id = job_store.create("claim", "check")
            done, patched_update = _wait_for_job(job_store, job_id)
            job_store.update = patched_update
            runner_with_wh.submit(job_id)
            assert done.wait(timeout=5.0)
        calls = [c.args[0] for c in mock_dispatcher.dispatch.call_args_list]
        assert "job.completed" in calls
        assert "verdict.completed" in calls

    def test_dispatches_job_failed_on_error(self, mock_db, mock_client, job_store):
        mock_dispatcher = MagicMock()
        runner_with_wh = JobRunner(mock_db, mock_client, job_store, mock_dispatcher)
        mock_client.generate.side_effect = RuntimeError("boom")
        job_id = job_store.create("claim", "check")
        done, patched_update = _wait_for_job(job_store, job_id)
        job_store.update = patched_update
        runner_with_wh.submit(job_id)
        assert done.wait(timeout=5.0)
        calls = [c.args[0] for c in mock_dispatcher.dispatch.call_args_list]
        assert "job.failed" in calls
