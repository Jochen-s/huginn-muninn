"""Tests for FastAPI REST API."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI test client with mocked lifespan dependencies."""
    from huginn_muninn.config import _reset_settings
    _reset_settings()
    from huginn_muninn.api import app

    # Pre-populate app.state so lifespan dependencies are available
    app.state.db = MagicMock()
    app.state.client = MagicMock()
    app.state.index_html = "<html><body>test</body></html>"
    app.state.job_store = MagicMock()
    app.state.job_runner = MagicMock()
    app.state.webhook_dispatcher = MagicMock()

    return TestClient(app, raise_server_exceptions=False)


class TestHealth:
    def test_health_endpoint_exists(self, client):
        with patch("huginn_muninn.api._check_llm") as mock:
            mock.return_value = {"status": "ok", "available": True}
            resp = client.get("/api/health")
        assert resp.status_code in (200, 503)

    def test_health_returns_status(self, client):
        with patch("huginn_muninn.api._check_llm") as mock:
            mock.return_value = {"status": "ok", "available": True}
            resp = client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"

    def test_health_503_when_ollama_down(self, client):
        with patch("huginn_muninn.api._check_llm") as mock:
            mock.return_value = {"status": "unavailable", "available": False}
            resp = client.get("/api/health")
            assert resp.status_code == 503


class TestCheckEndpoint:
    def test_check_validates_empty_claim(self, client):
        resp = client.post("/api/check", json={"claim": ""})
        assert resp.status_code == 422

    def test_check_returns_verdict(self, client):
        verdict = {
            "claim": "test",
            "verdict": "true",
            "confidence": 0.9,
            "evidence_for": [{"text": "e", "source_url": "http://x.com", "source_tier": 1, "supports_claim": True}],
            "evidence_against": [],
            "unknowns": [],
            "abstain_reason": None,
            "common_ground": {
                "shared_concern": "Truth",
                "framing_technique": "none_detected",
                "technique_explanation": "None",
                "reflection": "What makes this interesting?",
            },
            "escalation": {"score": 0.1, "should_escalate": False, "reason": "Simple"},
        }
        with patch("huginn_muninn.api._run_method1") as mock:
            mock.return_value = (verdict, 1)
            resp = client.post("/api/check", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "true"

    def test_check_with_no_cache(self, client):
        with patch("huginn_muninn.api._run_method1") as mock:
            mock.return_value = ({"verdict": "true", "confidence": 0.9}, 1)
            resp = client.post("/api/check", json={"claim": "Test claim here", "no_cache": True})
        assert resp.status_code == 200
        mock.assert_called_once()


class TestAnalyzeEndpoint:
    def test_analyze_validates_empty_claim(self, client):
        resp = client.post("/api/analyze", json={"claim": ""})
        assert resp.status_code == 422

    def test_analyze_returns_report(self, client):
        report = {
            "claim": "test",
            "method": "method_2",
            "overall_confidence": 0.7,
            "degraded": False,
            "degraded_reason": None,
            "decomposition": {"sub_claims": [{"text": "t", "type": "factual", "verifiable": True}], "original_claim": "test", "complexity": "simple"},
            "origins": {"origins": [], "mutations": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {"universal_needs": ["fairness"], "issue_overlap": "", "narrative_deconstruction": "", "perception_gap": "", "moral_foundations": {}, "reframe": "", "socratic_dialogue": ["R1"]},
            "audit": {"verdict": "pass", "findings": [], "confidence_adjustment": 0.0, "veto": False, "summary": "OK"},
        }
        with patch("huginn_muninn.api._run_method2") as mock:
            mock.return_value = (report, 1)
            resp = client.post("/api/analyze", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        data = resp.json()
        # Sprint 3 PR 1: response is now an AnalysisResponse envelope
        assert "data" in data
        assert data["data"]["method"] == "method_2"
        assert "suppressed_fields" in data
        assert "api_version" in data


class TestCheckAndEscalate:
    def test_escalate_returns_combined_when_triggered(self, client):
        verdict = {
            "verdict": "mixed", "confidence": 0.5,
            "escalation": {"score": 0.7, "should_escalate": True, "reason": "Complex"},
        }
        report = {"method": "method_2", "overall_confidence": 0.7}
        with patch("huginn_muninn.api._run_method1") as m1, \
             patch("huginn_muninn.api._run_method2") as m2:
            m1.return_value = (verdict, 1)
            m2.return_value = (report, 2)
            resp = client.post("/api/check-and-escalate", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["escalated"] is True
        assert "method_1" in data
        assert "method_2" in data

    def test_escalate_returns_method1_only_when_not_triggered(self, client):
        verdict = {
            "verdict": "true", "confidence": 0.95,
            "escalation": {"score": 0.1, "should_escalate": False, "reason": "Simple"},
        }
        with patch("huginn_muninn.api._run_method1") as m1:
            m1.return_value = (verdict, 1)
            resp = client.post("/api/check-and-escalate", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["escalated"] is False
        assert "method_1" in data
        assert "method_2" not in data


class TestFeedback:
    def test_feedback_accepts_valid(self, client):
        client.app.state.db.get_cached_verdict.return_value = None
        resp = client.post("/api/feedback", json={
            "claim": "Test claim", "type": "agree", "comment": "Looks right"
        })
        assert resp.status_code == 200

    def test_feedback_rejects_invalid_type(self, client):
        resp = client.post("/api/feedback", json={
            "claim": "Test claim", "type": "love_it"
        })
        assert resp.status_code == 422


class TestHistory:
    def test_history_returns_list(self, client):
        client.app.state.db.get_recent_verdicts.return_value = []
        client.app.state.db.get_recent_analyses.return_value = []
        resp = client.get("/api/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "verdicts" in data
        assert "analyses" in data

    def test_history_rejects_limit_too_large(self, client):
        resp = client.get("/api/history?limit=999")
        assert resp.status_code == 422

    def test_history_rejects_limit_zero(self, client):
        resp = client.get("/api/history?limit=0")
        assert resp.status_code == 422


class TestJobEndpoints:
    def test_submit_job_returns_202(self, client):
        client.app.state.job_store.create.return_value = "abc123"
        resp = client.post("/api/jobs", json={"claim": "Test claim", "method": "check"})
        assert resp.status_code == 202
        data = resp.json()
        assert data["job_id"] == "abc123"
        assert data["status"] == "pending"

    def test_submit_job_validates_claim(self, client):
        resp = client.post("/api/jobs", json={"claim": "", "method": "check"})
        assert resp.status_code == 422

    def test_get_job_found(self, client):
        from huginn_muninn.jobs import JobStatus
        client.app.state.job_store.get.return_value = {
            "id": "abc", "claim": "test", "method": "check",
            "status": JobStatus.COMPLETED, "result": {"verdict": "true"},
            "error": None, "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:01",
        }
        resp = client.get("/api/jobs/abc")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_get_job_not_found(self, client):
        client.app.state.job_store.get.return_value = None
        resp = client.get("/api/jobs/nonexistent")
        assert resp.status_code == 404

    def test_list_jobs(self, client):
        from huginn_muninn.jobs import JobStatus
        client.app.state.job_store.list_jobs.return_value = [
            {"id": "a", "claim": "c1", "method": "check", "status": JobStatus.PENDING, "created_at": "2026-01-01T00:00:00"},
        ]
        resp = client.get("/api/jobs")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_submit_job_invalid_method(self, client):
        resp = client.post("/api/jobs", json={"claim": "Test claim", "method": "invalid"})
        assert resp.status_code == 422


class TestWebhookEndpoints:
    def test_create_webhook(self, client):
        client.app.state.db.create_webhook.return_value = 1
        resp = client.post("/api/webhooks", json={
            "url": "http://example.com/hook", "events": ["job.completed"]
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert "secret" in data  # secret returned only on creation
        assert len(data["secret"]) == 64  # 32-byte hex

    def test_create_webhook_invalid_event(self, client):
        resp = client.post("/api/webhooks", json={
            "url": "http://example.com/hook", "events": ["invalid.event"]
        })
        assert resp.status_code == 422

    def test_list_webhooks_masks_secrets(self, client):
        client.app.state.db.list_webhooks.return_value = [
            {"id": 1, "url": "http://x.com", "secret": "abcdefghijklmnop", "events": ["job.completed"], "active": True, "created_at": "2026-01-01"}
        ]
        resp = client.get("/api/webhooks")
        assert resp.status_code == 200
        data = resp.json()
        # Sprint 3 PR 1: secret is fully hidden, replaced with boolean
        assert "secret" not in data[0]
        assert data[0]["secret_configured"] is True

    def test_get_webhook(self, client):
        client.app.state.db.get_webhook.return_value = {
            "id": 1, "url": "http://x.com", "secret": "abcdefghijklmnop",
            "events": ["job.completed"], "active": True, "created_at": "2026-01-01"
        }
        resp = client.get("/api/webhooks/1")
        assert resp.status_code == 200
        assert "secret" not in resp.json()
        assert resp.json()["secret_configured"] is True

    def test_get_webhook_not_found(self, client):
        client.app.state.db.get_webhook.return_value = None
        resp = client.get("/api/webhooks/999")
        assert resp.status_code == 404

    def test_update_webhook(self, client):
        client.app.state.db.update_webhook.return_value = {
            "id": 1, "url": "http://x.com", "secret": "abcdefghijklmnop",
            "events": ["job.completed", "job.failed"], "active": True, "created_at": "2026-01-01"
        }
        resp = client.patch("/api/webhooks/1", json={"events": ["job.completed", "job.failed"]})
        assert resp.status_code == 200

    def test_delete_webhook(self, client):
        client.app.state.db.delete_webhook.return_value = True
        resp = client.delete("/api/webhooks/1")
        assert resp.status_code == 204

    def test_delete_webhook_not_found(self, client):
        client.app.state.db.delete_webhook.return_value = False
        resp = client.delete("/api/webhooks/999")
        assert resp.status_code == 404


class TestSessionEndpoints:
    def test_create_session(self, client):
        client.app.state.db.create_session.return_value = 1
        resp = client.post("/api/sessions", json={"name": "Test Session"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert data["name"] == "Test Session"

    def test_create_session_empty_name(self, client):
        resp = client.post("/api/sessions", json={"name": ""})
        assert resp.status_code == 422

    def test_list_sessions(self, client):
        client.app.state.db.list_sessions.return_value = [
            {"id": 1, "name": "S1", "created_at": "2026-01-01"}
        ]
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_session(self, client):
        client.app.state.db.get_session.return_value = {
            "id": 1, "name": "S1", "created_at": "2026-01-01", "items": []
        }
        resp = client.get("/api/sessions/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "S1"

    def test_get_session_not_found(self, client):
        client.app.state.db.get_session.return_value = None
        resp = client.get("/api/sessions/999")
        assert resp.status_code == 404

    def test_add_session_item(self, client):
        client.app.state.db.get_session.return_value = {
            "id": 1, "name": "S1", "created_at": "2026-01-01", "items": []
        }
        client.app.state.db.add_session_item.return_value = 1
        resp = client.post("/api/sessions/1/items", json={
            "item_type": "verdict", "item_id": 42
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["item_type"] == "verdict"
        assert data["item_id"] == 42

    def test_add_session_item_invalid_type(self, client):
        client.app.state.db.get_session.return_value = {
            "id": 1, "name": "S1", "created_at": "2026-01-01", "items": []
        }
        resp = client.post("/api/sessions/1/items", json={
            "item_type": "invalid", "item_id": 1
        })
        assert resp.status_code == 422

    def test_add_item_to_nonexistent_session(self, client):
        client.app.state.db.get_session.return_value = None
        resp = client.post("/api/sessions/999/items", json={
            "item_type": "verdict", "item_id": 1
        })
        assert resp.status_code == 404


class TestReturnIds:
    def test_check_returns_verdict_id(self, client):
        with patch("huginn_muninn.api._run_method1") as mock:
            mock.return_value = ({"verdict": "true", "confidence": 0.9}, 42)
            resp = client.post("/api/check", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        assert resp.json()["verdict_id"] == 42

    def test_analyze_returns_analysis_id(self, client):
        with patch("huginn_muninn.api._run_method2") as mock:
            mock.return_value = ({"method": "method_2"}, 7)
            resp = client.post("/api/analyze", json={"claim": "Test claim here"})
        assert resp.status_code == 200
        assert resp.json()["analysis_id"] == 7

    def test_escalate_returns_both_ids(self, client):
        verdict = {
            "verdict": "mixed", "confidence": 0.5,
            "escalation": {"score": 0.7, "should_escalate": True, "reason": "Complex"},
        }
        report = {"method": "method_2"}
        with patch("huginn_muninn.api._run_method1") as m1, \
             patch("huginn_muninn.api._run_method2") as m2:
            m1.return_value = (verdict, 10)
            m2.return_value = (report, 20)
            resp = client.post("/api/check-and-escalate", json={"claim": "Test claim here"})
        data = resp.json()
        assert data["verdict_id"] == 10
        assert data["analysis_id"] == 20


class TestStaticFiles:
    def test_root_serves_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "html" in resp.text.lower()
