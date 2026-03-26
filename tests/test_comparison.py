"""Tests for ComparisonEngine and comparison analysis."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from huginn_muninn.comparison import ComparisonEngine, _compute_comparison
from huginn_muninn.db import HuginnDB
from huginn_muninn.model_registry import ModelConfig, ModelRegistry


class FakeLLMClient:
    """Minimal LLM client that returns a pre-set response."""

    def __init__(self, response: str):
        self._response = response
        self.closed = False

    def generate(self, prompt: str) -> str:
        return self._response

    def close(self):
        self.closed = True


def _check_result(verdict="true", confidence=0.85):
    return json.dumps({
        "verdict": verdict,
        "confidence": confidence,
        "evidence_for": [],
        "evidence_against": [],
        "unknowns": [],
        "common_ground": {
            "shared_concern": "test",
            "framing_technique": "none_detected",
            "technique_explanation": "test",
            "reflection": "test?",
        },
        "escalation": {"score": 0.1, "should_escalate": False, "reason": "test"},
    })


@pytest.fixture
def db(tmp_path):
    return HuginnDB(tmp_path / "test.db")


@pytest.fixture
def registry(tmp_path):
    config = [
        {"name": "model-a", "provider": "ollama", "base_url": "http://localhost:11434", "model": "test-a"},
        {"name": "model-b", "provider": "ollama", "base_url": "http://localhost:11434", "model": "test-b"},
        {"name": "reconciler", "provider": "ollama", "base_url": "http://localhost:11434", "model": "test-r", "reconcile": True},
    ]
    path = tmp_path / "models.json"
    path.write_text(json.dumps(config))
    return ModelRegistry(path)


class TestComputeComparison:
    def test_full_agreement(self):
        results = {
            "model-a": {"verdict": "true", "confidence": 0.9},
            "model-b": {"verdict": "true", "confidence": 0.85},
        }
        comp = _compute_comparison(results, "check")
        assert comp["verdict_agreement"] is True
        assert comp["confidence_spread"] == 0.05
        assert comp["key_differences"] == []

    def test_disagreement(self):
        results = {
            "model-a": {"verdict": "true", "confidence": 0.9},
            "model-b": {"verdict": "false", "confidence": 0.8},
        }
        comp = _compute_comparison(results, "check")
        assert comp["verdict_agreement"] is False
        assert len(comp["key_differences"]) == 1
        assert "model-a (true) vs model-b (false)" in comp["key_differences"][0]

    def test_error_result_excluded_from_agreement(self):
        results = {
            "model-a": {"verdict": "true", "confidence": 0.9},
            "model-b": {"error": "timeout"},
        }
        comp = _compute_comparison(results, "check")
        assert comp["verdict_agreement"] is True
        assert comp["verdicts"]["model-b"] == "error"

    def test_method2_uses_overall_confidence(self):
        results = {
            "model-a": {"overall_confidence": 0.7},
            "model-b": {"overall_confidence": 0.5},
        }
        comp = _compute_comparison(results, "analyze")
        assert comp["confidence_spread"] == 0.2

    def test_single_model(self):
        results = {"model-a": {"verdict": "mixed", "confidence": 0.6}}
        comp = _compute_comparison(results, "check")
        assert comp["verdict_agreement"] is True
        assert comp["confidence_spread"] == 0.0

    def test_all_errors(self):
        results = {
            "model-a": {"error": "fail"},
            "model-b": {"error": "fail"},
        }
        comp = _compute_comparison(results, "check")
        assert comp["verdict_agreement"] is False


class TestComparisonEngine:
    def test_compare_two_models(self, db, registry):
        fake_response = _check_result("true", 0.9)
        with patch.object(registry, "create_client") as mock_create:
            mock_create.return_value = FakeLLMClient(fake_response)
            engine = ComparisonEngine(registry, db)
            result = engine.compare("test claim", ["model-a", "model-b"], method="check")
            engine.shutdown()

        assert result["claim"] == "test claim"
        assert "model-a" in result["results"]
        assert "model-b" in result["results"]
        assert "comparison" in result
        assert "id" in result

    def test_compare_stores_in_db(self, db, registry):
        fake_response = _check_result()
        with patch.object(registry, "create_client") as mock_create:
            mock_create.return_value = FakeLLMClient(fake_response)
            engine = ComparisonEngine(registry, db)
            result = engine.compare("test", ["model-a", "model-b"], method="check")
            engine.shutdown()

        stored = db.get_comparison(result["id"])
        assert stored is not None
        assert stored["claim"] == "test"

    def test_model_failure_captured(self, db, registry):
        def failing_create(name):
            client = MagicMock()
            client.generate.side_effect = RuntimeError("boom")
            client.close = MagicMock()
            return client

        with patch.object(registry, "create_client", side_effect=failing_create):
            engine = ComparisonEngine(registry, db)
            result = engine.compare("test", ["model-a"], method="check")
            engine.shutdown()

        assert "error" in result["results"]["model-a"]

    def test_reconciliation(self, db, registry):
        check_response = _check_result("true", 0.9)
        reconcile_response = json.dumps({
            "meta_verdict": "true",
            "meta_confidence": 0.92,
            "reasoning": "Both models agree",
            "agreements": ["verdict"],
            "disagreements": [],
        })

        call_count = [0]

        def mock_create(name):
            call_count[0] += 1
            if name == "reconciler":
                return FakeLLMClient(reconcile_response)
            return FakeLLMClient(check_response)

        with patch.object(registry, "create_client", side_effect=mock_create):
            engine = ComparisonEngine(registry, db)
            result = engine.compare(
                "test", ["model-a", "model-b"],
                method="check", reconcile=True,
            )
            engine.shutdown()

        assert "reconciliation" in result
        assert result["reconciliation"]["meta_verdict"] == "true"

    def test_no_reconcile_without_model(self, db, tmp_path):
        config = [
            {"name": "model-a", "provider": "ollama", "base_url": "http://localhost:11434", "model": "test-a"},
        ]
        path = tmp_path / "models.json"
        path.write_text(json.dumps(config))
        reg = ModelRegistry(path)

        fake_response = _check_result()
        with patch.object(reg, "create_client") as mock_create:
            mock_create.return_value = FakeLLMClient(fake_response)
            engine = ComparisonEngine(reg, db)
            result = engine.compare("test", ["model-a"], method="check", reconcile=True)
            engine.shutdown()

        assert "reconciliation" not in result

    def test_clients_closed_after_use(self, db, registry):
        clients = []

        def tracking_create(name):
            c = FakeLLMClient(_check_result())
            clients.append(c)
            return c

        with patch.object(registry, "create_client", side_effect=tracking_create):
            engine = ComparisonEngine(registry, db)
            engine.compare("test", ["model-a", "model-b"], method="check")
            engine.shutdown()

        assert all(c.closed for c in clients)


class TestDBComparisons:
    def test_store_and_retrieve(self, db):
        cid = db.store_comparison(
            claim="test",
            models=["a", "b"],
            method="check",
            results={"a": {"verdict": "true"}},
            comparison={"verdict_agreement": True},
        )
        stored = db.get_comparison(cid)
        assert stored["claim"] == "test"
        assert stored["models"] == ["a", "b"]
        assert stored["results"]["a"]["verdict"] == "true"

    def test_get_missing_returns_none(self, db):
        assert db.get_comparison(999) is None

    def test_get_recent(self, db):
        db.store_comparison("c1", ["a"], "check", {}, {})
        db.store_comparison("c2", ["b"], "check", {}, {})
        recent = db.get_recent_comparisons(limit=10)
        assert len(recent) == 2
        assert recent[0]["claim"] == "c2"

    def test_recent_respects_limit(self, db):
        for i in range(5):
            db.store_comparison(f"c{i}", ["a"], "check", {}, {})
        recent = db.get_recent_comparisons(limit=2)
        assert len(recent) == 2
