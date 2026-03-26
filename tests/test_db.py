"""Tests for SQLite cache and feedback store."""
import pytest

from huginn_muninn.db import HuginnDB


@pytest.fixture
def db(tmp_path):
    return HuginnDB(tmp_path / "test.db")


class TestCache:
    def test_cache_miss_returns_none(self, db):
        assert db.get_cached_verdict("nonexistent claim") is None

    def test_cache_hit_after_store(self, db):
        db.store_verdict("test claim", {"verdict": "true", "confidence": 0.9})
        result = db.get_cached_verdict("test claim")
        assert result["verdict"] == "true"

    def test_similar_claims_are_different_cache_keys(self, db):
        db.store_verdict("claim A", {"verdict": "true"})
        assert db.get_cached_verdict("claim B") is None


class TestFeedback:
    def test_store_feedback(self, db):
        db.store_feedback(
            claim="test claim",
            verdict="true",
            feedback_type="agree",
            comment="Looks right",
        )
        feedback = db.get_feedback_for_claim("test claim")
        assert len(feedback) == 1
        assert feedback[0]["feedback_type"] == "agree"

    def test_multiple_feedback_entries(self, db):
        db.store_feedback("claim", "true", "agree", None)
        db.store_feedback("claim", "true", "disagree", "Wrong!")
        feedback = db.get_feedback_for_claim("claim")
        assert len(feedback) == 2


class TestAnalysisStorage:
    def test_store_and_retrieve_analysis(self, tmp_path):
        db = HuginnDB(tmp_path / "test.db")
        analysis = {
            "claim": "Test claim",
            "method": "method_2",
            "overall_confidence": 0.75,
            "decomposition": {"sub_claims": []},
            "degraded": False,
        }
        db.store_analysis("Test claim", analysis)
        cached = db.get_cached_analysis("Test claim")
        assert cached is not None
        assert cached["method"] == "method_2"
        assert cached["overall_confidence"] == 0.75
        db.close()

    def test_analysis_cache_miss(self, tmp_path):
        db = HuginnDB(tmp_path / "test.db")
        assert db.get_cached_analysis("nonexistent") is None
        db.close()


class TestSessions:
    def test_create_session(self, db):
        sid = db.create_session("Test Session")
        assert isinstance(sid, int)

    def test_get_session(self, db):
        sid = db.create_session("My Session")
        session = db.get_session(sid)
        assert session["name"] == "My Session"
        assert session["items"] == []

    def test_get_nonexistent_session(self, db):
        assert db.get_session(999) is None

    def test_list_sessions(self, db):
        db.create_session("S1")
        db.create_session("S2")
        sessions = db.list_sessions()
        assert len(sessions) == 2

    def test_add_session_item(self, db):
        sid = db.create_session("Session")
        db.store_verdict("claim", {"verdict": "true"})
        item_id = db.add_session_item(sid, "verdict", 1)
        assert isinstance(item_id, int)
        session = db.get_session(sid)
        assert len(session["items"]) == 1
        assert session["items"][0]["item_type"] == "verdict"

    def test_session_item_fk_constraint(self, db):
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            db.add_session_item(999, "verdict", 1)


class TestWebhooks:
    def test_create_webhook(self, db):
        wid = db.create_webhook("http://example.com/hook", "secret123", ["job.completed"])
        assert isinstance(wid, int)

    def test_get_webhook(self, db):
        wid = db.create_webhook("http://example.com/hook", "secret123", ["job.completed", "job.failed"])
        wh = db.get_webhook(wid)
        assert wh["url"] == "http://example.com/hook"
        assert wh["secret"] == "secret123"
        assert wh["events"] == ["job.completed", "job.failed"]
        assert wh["active"] is True

    def test_get_nonexistent_webhook(self, db):
        assert db.get_webhook(999) is None

    def test_list_webhooks(self, db):
        db.create_webhook("http://a.com", "s1", ["job.completed"])
        db.create_webhook("http://b.com", "s2", ["job.failed"])
        webhooks = db.list_webhooks()
        assert len(webhooks) == 2

    def test_update_webhook_active(self, db):
        wid = db.create_webhook("http://x.com", "s", ["job.completed"])
        updated = db.update_webhook(wid, active=False)
        assert updated["active"] is False

    def test_update_webhook_events(self, db):
        wid = db.create_webhook("http://x.com", "s", ["job.completed"])
        updated = db.update_webhook(wid, events=["job.completed", "job.failed"])
        assert updated["events"] == ["job.completed", "job.failed"]

    def test_update_nonexistent_webhook(self, db):
        assert db.update_webhook(999, active=False) is None

    def test_delete_webhook(self, db):
        wid = db.create_webhook("http://x.com", "s", ["job.completed"])
        assert db.delete_webhook(wid) is True
        assert db.get_webhook(wid) is None

    def test_delete_nonexistent_webhook(self, db):
        assert db.delete_webhook(999) is False

    def test_get_webhooks_for_event(self, db):
        db.create_webhook("http://a.com", "s1", ["job.completed", "verdict.completed"])
        db.create_webhook("http://b.com", "s2", ["job.failed"])
        db.create_webhook("http://c.com", "s3", ["job.completed"])
        # Deactivate the third
        db.update_webhook(3, active=False)
        hooks = db.get_webhooks_for_event("job.completed")
        assert len(hooks) == 1
        assert hooks[0]["url"] == "http://a.com"

    def test_get_verdict_by_id(self, db):
        rid = db.store_verdict("claim", {"verdict": "true"})
        row = db.get_verdict_by_id(rid)
        assert row["claim"] == "claim"
        assert row["data"]["verdict"] == "true"

    def test_get_analysis_by_id(self, db):
        rid = db.store_analysis("claim", {"method": "method_2"})
        row = db.get_analysis_by_id(rid)
        assert row["claim"] == "claim"
        assert row["data"]["method"] == "method_2"


class TestHistory:
    def test_recent_verdicts_empty(self, db):
        result = db.get_recent_verdicts(limit=10)
        assert result == []

    def test_recent_verdicts_returns_stored(self, db):
        db.store_verdict("claim A", {"verdict": "true", "confidence": 0.9})
        db.store_verdict("claim B", {"verdict": "false", "confidence": 0.3})
        result = db.get_recent_verdicts(limit=10)
        assert len(result) == 2
        # Most recent first
        assert result[0]["claim"] == "claim B"
        assert result[1]["claim"] == "claim A"

    def test_recent_verdicts_respects_limit(self, db):
        for i in range(5):
            db.store_verdict(f"claim {i}", {"verdict": "true"})
        result = db.get_recent_verdicts(limit=3)
        assert len(result) == 3

    def test_recent_analyses_empty(self, db):
        result = db.get_recent_analyses(limit=10)
        assert result == []

    def test_recent_analyses_returns_stored(self, db):
        db.store_analysis("claim X", {"method": "method_2", "overall_confidence": 0.7})
        result = db.get_recent_analyses(limit=10)
        assert len(result) == 1
        assert result[0]["claim"] == "claim X"
        assert result[0]["data"]["method"] == "method_2"
