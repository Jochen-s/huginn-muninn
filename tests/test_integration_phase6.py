"""Integration tests for Phase 6: batch, comparison, search enrichment, model registry."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from huginn_muninn.batch import BatchStore
from huginn_muninn.comparison import ComparisonEngine
from huginn_muninn.db import HuginnDB
from huginn_muninn.jobs import JobStatus, JobStore
from huginn_muninn.llm import OllamaClient
from huginn_muninn.model_registry import ModelRegistry
from huginn_muninn.search import SearchClient, enrich_evidence


# --- Fixtures ---

@pytest.fixture
def db(tmp_path):
    return HuginnDB(tmp_path / "test.db")


@pytest.fixture
def job_store():
    return JobStore(max_jobs=100)


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


class FakeLLMClient:
    def __init__(self, response: str):
        self._response = response
        self.closed = False

    def generate(self, prompt: str) -> str:
        return self._response

    def close(self):
        self.closed = True


# --- Batch lifecycle ---

class TestBatchLifecycle:
    def test_submit_and_complete_batch(self, job_store):
        bs = BatchStore(job_store)
        j1 = job_store.create("Earth is round", "check")
        j2 = job_store.create("Water is wet", "check")
        j3 = job_store.create("Sky is blue", "check")

        batch_id = bs.create([j1, j2, j3])
        assert bs.get(batch_id)["status"] == "pending"

        # Simulate running
        job_store.update(j1, status=JobStatus.RUNNING)
        assert bs.get(batch_id)["status"] == "running"

        # Simulate completion
        job_store.update(j1, status=JobStatus.COMPLETED, result={"verdict": "true"})
        job_store.update(j2, status=JobStatus.COMPLETED, result={"verdict": "true"})
        job_store.update(j3, status=JobStatus.COMPLETED, result={"verdict": "true"})
        assert bs.get(batch_id)["status"] == "completed"

    def test_partial_failure_batch(self, job_store):
        bs = BatchStore(job_store)
        j1 = job_store.create("claim 1", "check")
        j2 = job_store.create("claim 2", "check")
        j3 = job_store.create("claim 3", "check")

        batch_id = bs.create([j1, j2, j3])

        job_store.update(j1, status=JobStatus.COMPLETED, result={"verdict": "true"})
        job_store.update(j2, status=JobStatus.FAILED, error="timeout")
        job_store.update(j3, status=JobStatus.COMPLETED, result={"verdict": "false"})

        batch = bs.get(batch_id)
        assert batch["status"] == "partial"


# --- Comparison lifecycle ---

class TestComparisonLifecycle:
    def test_agreement_comparison(self, db, registry):
        response = _check_result("true", 0.9)
        with patch.object(registry, "create_client") as mock:
            mock.return_value = FakeLLMClient(response)
            engine = ComparisonEngine(registry, db)
            result = engine.compare("test claim", ["model-a", "model-b"], method="check")
            engine.shutdown()

        assert result["comparison"]["verdict_agreement"] is True
        assert result["comparison"]["confidence_spread"] == 0.0
        assert result["comparison"]["key_differences"] == []
        assert result["id"] is not None
        assert db.get_comparison(result["id"]) is not None

    def test_divergence_comparison(self, db, registry):
        call_count = [0]

        def mock_create(name):
            call_count[0] += 1
            if name == "model-a":
                return FakeLLMClient(_check_result("true", 0.9))
            return FakeLLMClient(_check_result("false", 0.8))

        with patch.object(registry, "create_client", side_effect=mock_create):
            engine = ComparisonEngine(registry, db)
            result = engine.compare("disputed claim", ["model-a", "model-b"], method="check")
            engine.shutdown()

        assert result["comparison"]["verdict_agreement"] is False
        assert len(result["comparison"]["key_differences"]) == 1


# --- Source enrichment ---

class TestSourceEnrichment:
    def test_enrichment_replaces_urls(self, httpx_mock):
        brave_response = {
            "web": {
                "results": [
                    {
                        "url": "https://real-source.com/article",
                        "title": "Real Article",
                        "description": "A real result",
                        "page_age": "2024-06-01",
                    },
                ]
            }
        }
        httpx_mock.add_response(json=brave_response)

        client = SearchClient(api_key="test-key")
        evidence = [
            {"text": "Vaccines are safe and effective", "source_url": "http://fake-llm-url.com"},
        ]
        enriched = enrich_evidence(evidence, client, max_items=1)
        assert enriched[0]["source_url"] == "https://real-source.com/article"
        assert enriched[0]["publication_date"] == "2024-06-01"
        client.close()

    def test_enrichment_graceful_without_client(self):
        evidence = [
            {"text": "Some evidence", "source_url": "http://original.com"},
        ]
        result = enrich_evidence(evidence, None)
        assert result[0]["source_url"] == "http://original.com"


# --- Model registry round-trip ---

class TestModelRegistryRoundTrip:
    def test_load_and_create_clients(self, registry):
        names = registry.list_names()
        assert "model-a" in names
        assert "model-b" in names
        assert "reconciler" in names

        with patch("huginn_muninn.model_registry.create_client") as mock_factory:
            mock_factory.return_value = MagicMock()
            client_a = registry.create_client("model-a")
            assert client_a is not None
            mock_factory.assert_called_once()

    def test_reconcile_model_identified(self, registry):
        assert registry.get_reconcile_model() == "reconciler"

    def test_empty_config(self, tmp_path):
        path = tmp_path / "empty.json"
        reg = ModelRegistry(path)
        assert reg.list_names() == []
        assert reg.get_reconcile_model() is None


# --- DB comparison storage ---

class TestDBComparisonStorage:
    def test_store_retrieve_recent(self, db):
        id1 = db.store_comparison("c1", ["a", "b"], "check", {"a": {"verdict": "true"}}, {"verdict_agreement": True})
        id2 = db.store_comparison("c2", ["a", "b"], "check", {"a": {"verdict": "false"}}, {"verdict_agreement": False})

        assert db.get_comparison(id1)["claim"] == "c1"
        assert db.get_comparison(id2)["claim"] == "c2"

        recent = db.get_recent_comparisons(limit=10)
        assert len(recent) == 2
        assert recent[0]["claim"] == "c2"  # Most recent first
