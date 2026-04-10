"""Tests for Method 2 orchestrator."""
import json
from unittest.mock import MagicMock

import pytest

from huginn_muninn.agents.base import AgentError
from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.llm import OllamaClient
from huginn_muninn.orchestrator import Orchestrator, _compute_hypothesis_expansion_score


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

    def test_pre_gorgon_mock_responses_still_parse(self):
        """Regression guard: MOCK_RESPONSES lacks the cognitive-warfare fields.
        The pipeline must still produce a valid AnalysisReport by relying on
        Pydantic defaults on every new Decomposer/Tracer/Auditor field."""
        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        report = AnalysisReport(**result)
        # All Gorgon defaults should be populated
        assert report.decomposition.hypothesis_crowding == "low"
        assert report.decomposition.manipulation_vector_density == 0.0
        assert report.decomposition.complexity_explosion_flag is False
        assert report.origins.notable_omissions == []
        assert report.audit.frame_capture_risk == "none"
        assert report.audit.frame_capture_evidence == ""

    def test_degraded_result_conforms_to_contract_with_gorgon_fields(self):
        """The degraded fallback must populate every new cognitive-warfare field."""
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = Exception("total failure")
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        report = AnalysisReport(**result)
        assert report.decomposition.hypothesis_crowding == "low"
        assert report.origins.notable_omissions == []
        assert report.audit.frame_capture_risk == "none"


class TestHypothesisExpansionScore:
    """P1 #5: deterministic zero-token hypothesis-expansion signal."""

    def test_empty_subclaims_returns_zero(self):
        assert _compute_hypothesis_expansion_score({"sub_claims": []}) == 0.0

    def test_missing_subclaims_key_returns_zero(self):
        assert _compute_hypothesis_expansion_score({}) == 0.0

    def test_single_simple_factual_claim_is_low(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "complexity": "simple",
        })
        # 1/5 * 1.0 * 1.0 = 0.2
        assert score == 0.2

    def test_five_simple_claims_without_causal_is_moderate(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": f"X{i}", "type": "factual"} for i in range(5)],
            "complexity": "simple",
        })
        # 5/5 * 1.0 * 1.0 = 1.0
        assert score == 1.0

    def test_three_causal_claims_amplify_score(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": [
                {"text": "X1", "type": "causal"},
                {"text": "X2", "type": "causal"},
                {"text": "X3", "type": "causal"},
            ],
            "complexity": "moderate",
        })
        # 3/5 * 1.5 * 1.25 = 1.125 -> capped at 1.0
        assert score == 1.0

    def test_score_bounded_at_one(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": f"X{i}", "type": "causal"} for i in range(10)],
            "complexity": "multi_actor",
        })
        assert 0.0 <= score <= 1.0
        assert score == 1.0

    def test_multi_actor_complexity_weighted_higher(self):
        simple = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "complexity": "simple",
        })
        multi_actor = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "complexity": "multi_actor",
        })
        assert multi_actor > simple

    def test_unknown_complexity_defaults_to_simple(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "complexity": "unknown_value",
        })
        assert score == 0.2

    def test_handles_none_subclaims(self):
        assert _compute_hypothesis_expansion_score({"sub_claims": None}) == 0.0

    def test_ignores_non_dict_subclaim_entries(self):
        score = _compute_hypothesis_expansion_score({
            "sub_claims": ["not-a-dict", {"text": "X", "type": "causal"}],
            "complexity": "simple",
        })
        # Non-dict entries count toward len() but not toward causal_count.
        # 2/5 * 1.0 * 1.0 = 0.4
        assert score == 0.4


class TestValidationFailureMarker:
    """Sprint 2 PR 1: when AnalysisReport validation fails at the production
    boundary (orchestrator.py:181-183), the degraded result must surface the
    failure via degraded_reason instead of masking it as a generic
    'Critical agent failure'. This catches schema/fallback drift early."""

    def test_validation_failure_surfaces_marker_in_reason(self, monkeypatch):
        """Force a Pydantic ValidationError at the final-assembly boundary
        and assert degraded_reason contains the validation_error marker."""
        from huginn_muninn import orchestrator as orch_module

        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)

        real_cls = orch_module.AnalysisReport

        class _AlwaysFailReport:
            def __init__(self, **_kwargs):
                # Trigger a real ValidationError via the genuine schema so we
                # hit the except-branch we actually care about.
                real_cls.model_validate({})

        monkeypatch.setattr(orch_module, "AnalysisReport", _AlwaysFailReport)
        result = orch.run("X is true because Y")

        assert result["degraded"] is True
        assert result["degraded_reason"] is not None
        assert "validation_error" in result["degraded_reason"].lower(), (
            f"Expected 'validation_error' in degraded_reason, got: "
            f"{result['degraded_reason']}"
        )

    def test_validation_failure_result_parses_against_real_contract(self, monkeypatch):
        """Even after forcing a boundary-validation failure, the returned
        degraded result must still parse against the REAL AnalysisReport."""
        from huginn_muninn import orchestrator as orch_module
        from huginn_muninn.contracts import AnalysisReport as RealReport

        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)

        real_cls = orch_module.AnalysisReport

        class _AlwaysFailReport:
            def __init__(self, **_kwargs):
                real_cls.model_validate({})

        monkeypatch.setattr(orch_module, "AnalysisReport", _AlwaysFailReport)
        result = orch.run("X is true because Y")

        # The degraded result must still satisfy the real contract
        report = RealReport(**result)
        assert report.degraded is True
