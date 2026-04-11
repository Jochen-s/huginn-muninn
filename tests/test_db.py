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


class TestCachedAnalysisNormalization:
    """Sprint 2 PR 2 / Codex blind-spot #1 mitigation.

    Legacy Method 2 analyses cached before PR 1 and PR 2 predate the new
    Pydantic fields (verification_priority, hypothesis_crowding,
    frame_capture_risk, notable_omissions, etc.). On cache read, the DB
    layer must populate every schema default so API/CLI/gallery consumers
    see the same shape regardless of whether the entry was cached yesterday
    or a month ago. Without this normalization, fresh runs would ship the
    new fields and cache hits would silently omit them -- Codex rated this a
    High-severity blind spot and blocked PR 2 commit on it.

    The fallback behavior when normalization fails (schema mismatch,
    hand-edited rows, pre-Method-2 entries) is to return the raw dict so
    that the read path degrades gracefully rather than raising; the rest of
    the system already handles missing-key shapes defensively."""

    @staticmethod
    def _build_legacy_pre_pr2_analysis(claim: str) -> dict:
        """A complete-enough pre-PR-2 Method 2 analysis with no
        verification_priority on any sub-claim. This is the exact shape
        that older cached entries have on disk."""
        return {
            "claim": claim,
            "decomposition": {
                "sub_claims": [
                    {"text": "X happened", "type": "factual", "verifiable": True},
                ],
                "original_claim": claim,
                "complexity": "simple",
                "hypothesis_crowding": "low",
                "manipulation_vector_density": 0.0,
                "complexity_explosion_flag": False,
            },
            "origins": {
                "origins": [],
                "mutations": [],
                "temporal_context": [],
                "notable_omissions": [],
            },
            "intelligence": {
                "actors": [],
                "relations": [],
                "narrative_summary": "",
            },
            "ttps": {"ttp_matches": [], "primary_tactic": "Execute"},
            "bridge": {
                "universal_needs": ["safety"],
                "issue_overlap": "",
                "narrative_deconstruction": "",
                "consensus_explanation": "",
                "inferential_gap": "",
                "feasibility_check": "",
                "commercial_motives": "",
                "techniques_revealed": [],
                "perception_gap": "",
                "moral_foundations": {},
                "reframe": "",
                "socratic_dialogue": ["R1"],
            },
            "audit": {
                "verdict": "pass",
                "findings": [],
                "confidence_adjustment": 0.0,
                "veto": False,
                "summary": "ok",
                "frame_capture_risk": "none",
                "frame_capture_evidence": "",
            },
            "overall_confidence": 0.7,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

    def test_legacy_cache_hit_populates_verification_priority(self, tmp_path):
        """PR 2 blind-spot mitigation: a pre-PR-2 analysis written to the
        cache must surface verification_priority="low" on the sub-claim
        when read back, not an absent key."""
        db = HuginnDB(tmp_path / "test.db")
        legacy = self._build_legacy_pre_pr2_analysis("Test")
        # Sanity: the legacy shape has no verification_priority on the sub-claim
        assert "verification_priority" not in legacy["decomposition"]["sub_claims"][0]
        db.store_analysis("Test", legacy)
        cached = db.get_cached_analysis("Test")
        assert cached is not None
        sub_claim = cached["decomposition"]["sub_claims"][0]
        assert sub_claim["verification_priority"] == "low"
        db.close()

    def test_legacy_cache_hit_with_id_populates_priority(self, tmp_path):
        """Same invariant for the with_id variant used by the API path."""
        db = HuginnDB(tmp_path / "test.db")
        legacy = self._build_legacy_pre_pr2_analysis("Test")
        db.store_analysis("Test", legacy)
        result = db.get_cached_analysis_with_id("Test")
        assert result is not None
        cached, _ = result
        sub_claim = cached["decomposition"]["sub_claims"][0]
        assert sub_claim["verification_priority"] == "low"
        db.close()

    def test_fresh_analysis_priority_survives_cache_round_trip(self, tmp_path):
        """An analysis with an explicit 'critical' priority must preserve
        that value through a cache store+read round trip. Normalization must
        not downgrade explicit values."""
        db = HuginnDB(tmp_path / "test.db")
        fresh = self._build_legacy_pre_pr2_analysis("Test")
        fresh["decomposition"]["sub_claims"][0]["verification_priority"] = "critical"
        db.store_analysis("Test", fresh)
        cached = db.get_cached_analysis("Test")
        assert cached["decomposition"]["sub_claims"][0]["verification_priority"] == "critical"
        db.close()

    def test_unvalidatable_cache_entry_returns_raw(self, tmp_path):
        """Degrade-gracefully invariant: if the cached dict is too broken
        to validate, the normalization helper must return the raw dict so
        callers still receive something. This prevents the cache path from
        crashing production when a hand-edited row exists."""
        db = HuginnDB(tmp_path / "test.db")
        broken = {"claim": "X", "method": "method_2"}  # no decomposition at all
        db.store_analysis("X", broken)
        cached = db.get_cached_analysis("X")
        # Raw dict survives even though it would never pass AnalysisReport validation
        assert cached == broken
        db.close()

    def test_normalization_populates_all_sprint1_pr2_defaults(self, tmp_path):
        """A legacy entry that is missing EVERY Sprint 1 and Sprint 2 field
        must surface all of them as defaults on read. Regression guard
        against future sprints' new fields breaking the same way."""
        db = HuginnDB(tmp_path / "test.db")
        legacy = self._build_legacy_pre_pr2_analysis("Test")
        # Strip every new field to the absolute legacy baseline
        legacy["decomposition"]["sub_claims"][0] = {
            "text": "X",
            "type": "factual",
            "verifiable": True,
        }
        db.store_analysis("Test", legacy)
        cached = db.get_cached_analysis("Test")
        sc = cached["decomposition"]["sub_claims"][0]
        # Sprint 2 PR 2 field
        assert sc["verification_priority"] == "low"
        # Sprint 1 fields on decomposition/audit/origins carry through
        assert cached["decomposition"]["hypothesis_crowding"] == "low"
        assert cached["audit"]["frame_capture_risk"] == "none"
        assert cached["origins"]["notable_omissions"] == []
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
