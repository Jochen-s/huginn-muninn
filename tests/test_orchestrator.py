"""Tests for Method 2 orchestrator."""
import json
from unittest.mock import MagicMock

import pytest

from huginn_muninn.agents.base import AgentError
from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.llm import OllamaClient
from huginn_muninn.orchestrator import Orchestrator


MOCK_RESPONSES = {
    "claim_decomposer": {
        "sub_claims": [{"text": "X is true", "type": "factual", "verifiable": True}],
        "original_claim": "X is true because Y",
        "complexity": "simple",
    },
    "origin_tracer": {
        "origins": [{"sub_claim": "X is true", "earliest_source": "source.com", "earliest_date": None, "source_tier": 2, "propagation_path": []}],
        "mutations": [],
    },
    "intelligence_mapper": {
        "actors": [{"name": "Actor A", "type": "media", "motivation": "clicks", "credibility": 0.5, "evidence": "pattern"}],
        "relations": [],
        "narrative_summary": "Simple narrative",
    },
    "ttp_classifier": {
        "ttp_matches": [],
        "primary_tactic": "Execute",
    },
    "bridge_builder": {
        "universal_needs": ["fairness"],
        "issue_overlap": "Both sides agree on X",
        "narrative_deconstruction": "N/A for simple claim",
        "perception_gap": "Minimal",
        "moral_foundations": {},
        "reframe": "This is about fairness",
        "socratic_dialogue": ["Round 1", "Round 2", "Round 3?"],
    },
    "adversarial_auditor": {
        "verdict": "pass",
        "findings": [],
        "confidence_adjustment": 0.0,
        "veto": False,
        "summary": "Analysis is solid",
    },
}


def make_mock_client(responses: dict) -> MagicMock:
    """Create a mock OllamaClient that returns agent-specific responses."""
    client = MagicMock(spec=OllamaClient)
    call_order = [
        "claim_decomposer", "origin_tracer", "intelligence_mapper",
        "ttp_classifier", "bridge_builder", "adversarial_auditor",
    ]
    client.generate.side_effect = [
        json.dumps(responses[name]) for name in call_order
    ]
    return client


class TestOrchestrator:
    def test_full_pipeline_success(self):
        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["claim"] == "X is true because Y"
        assert result["method"] == "method_2"
        assert not result["degraded"]
        assert result["overall_confidence"] > 0

    def test_auditor_veto_sets_degraded(self):
        responses = {**MOCK_RESPONSES}
        responses["adversarial_auditor"] = {
            "verdict": "fail",
            "findings": [{"category": "bias", "severity": "critical", "description": "Bad", "recommendation": "Fix"}],
            "confidence_adjustment": -0.5,
            "veto": True,
            "summary": "Vetoed",
        }
        client = make_mock_client(responses)
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["degraded"]
        assert "veto" in result["degraded_reason"].lower()

    def test_agent_failure_degrades_gracefully(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = [
            json.dumps(MOCK_RESPONSES["claim_decomposer"]),
            Exception("LLM timeout"),  # tracer fails
            json.dumps(MOCK_RESPONSES["intelligence_mapper"]),
            json.dumps(MOCK_RESPONSES["ttp_classifier"]),
            json.dumps(MOCK_RESPONSES["bridge_builder"]),
            json.dumps(MOCK_RESPONSES["adversarial_auditor"]),
        ]
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["degraded"] is True
        assert "origin_tracer" in result["degraded_reason"]

    def test_decomposer_failure_returns_degraded(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = Exception("LLM timeout")
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["degraded"] is True
        assert "decomposer" in result["degraded_reason"].lower()
        # Degraded result must still conform to the AnalysisReport contract
        report = AnalysisReport(**result)
        assert len(report.decomposition.sub_claims) == 1

    def test_confidence_with_many_failures(self):
        """5 failures (0.5 penalty) + audit fallback (-0.1) from base 0.7 = 0.1."""
        client = MagicMock(spec=OllamaClient)
        # Only decomposer succeeds, all others fail
        client.generate.side_effect = [
            json.dumps(MOCK_RESPONSES["claim_decomposer"]),
            Exception("fail"), Exception("fail"), Exception("fail"),
            Exception("fail"), Exception("fail"),
        ]
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["overall_confidence"] == 0.1
        assert result["degraded"] is True

    def test_confidence_no_failures(self):
        """Base confidence 0.7 with no failures and no adjustment."""
        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        assert result["overall_confidence"] == 0.7
