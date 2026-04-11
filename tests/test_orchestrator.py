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
        # Sprint 2 PR 3 fields carried in the base fixture per the plan
        # constraint "every new field gets a MOCK_RESPONSES update atomic
        # with the contract change" (Federation PR 3 review, Major #1).
        # Previously omitted and silently relying on Pydantic defaults;
        # the fleet convergence flagged this as a pattern divergence from
        # PR 2. All four are at their safe defaults here so existing
        # tests that dynamically override individual fields via dict
        # spread continue to work unchanged.
        "communication_posture": "direct_correction",
        "pattern_density_warning": False,
        "vacuum_filled_by": "",
        "prebunking_note": "",
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


class TestVerificationPriorityFallback:
    """Sprint 2 P2-7 regression guards for the orchestrator integration.

    These tests exist to prevent three specific regressions:
    (1) The degraded fallback drops the verification_priority default on the
        lone sub-claim it manufactures (would trigger the PR 1 validation
        marker blind-spot #2 path in production).
    (2) The MOCK_RESPONSES fixture's pre-Sprint-2 Decomposer output stops
        parsing (would mean we broke backwards-compat with every cached or
        historical Decomposer JSON in the wild).
    (3) The pipeline produces an AnalysisReport whose sub-claims lose the
        field after round-tripping through Pydantic validation at the
        production boundary."""

    def test_degraded_fallback_includes_verification_priority(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = Exception("total failure")
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        report = AnalysisReport(**result)
        # The degraded sub-claim must carry the explicit "low" default so
        # that the contract boundary validation does not trip the blind-spot
        # #2 validation marker path in PR 1.
        assert report.decomposition.sub_claims[0].verification_priority == "low"

    def test_degraded_fallback_raw_dict_carries_priority_key(self):
        """Dict-level regression guard: the fallback dict literal at
        orchestrator.py:_degraded_result must contain the key explicitly,
        not rely solely on the Pydantic default. This matters because the
        fallback dict is also observed by the API / CLI serializers before
        it passes through AnalysisReport validation."""
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = Exception("total failure")
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        sub_claim = result["decomposition"]["sub_claims"][0]
        assert "verification_priority" in sub_claim
        assert sub_claim["verification_priority"] == "low"

    def test_legacy_mock_responses_still_parse_with_default(self):
        """MOCK_RESPONSES predates Sprint 2; its Decomposer entry has no
        verification_priority key. The full pipeline must still succeed and
        the resulting AnalysisReport must show "low" as the default."""
        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)
        result = orch.run("X is true because Y")
        report = AnalysisReport(**result)
        for sc in report.decomposition.sub_claims:
            assert sc.verification_priority == "low"

    def test_explicit_priority_round_trips_through_pipeline(self):
        """An explicit "critical" priority from the Decomposer must survive
        every downstream contract validation and land in the final report."""
        responses = {**MOCK_RESPONSES}
        responses["claim_decomposer"] = {
            "sub_claims": [
                {
                    "text": "X caused N deaths",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "critical",
                },
                {
                    "text": "X is divisive",
                    "type": "opinion",
                    "verifiable": False,
                    "verification_priority": "low",
                },
            ],
            "original_claim": "X caused N deaths and X is divisive",
            "complexity": "moderate",
        }
        client = make_mock_client(responses)
        orch = Orchestrator(client)
        result = orch.run("X")
        report = AnalysisReport(**result)
        assert report.decomposition.sub_claims[0].verification_priority == "critical"
        assert report.decomposition.sub_claims[1].verification_priority == "low"

    def test_unknown_priority_literal_triggers_degraded_path(self):
        """LLM drift guard: if the Decomposer emits an unknown priority
        literal ("urgent"), the pipeline must either reject it at the agent
        boundary (AgentError -> degraded) or at the final AnalysisReport
        validation (blind-spot #2 marker). Under no circumstance may an
        invalid literal reach the final report silently.

        Federation #1 strengthening: asserting merely `degraded is True`
        is insufficient because any agent failure sets that flag; the test
        must also assert that degraded_reason surfaces an agent-boundary
        failure, not a generic critical-agent-failure mask."""
        responses = {**MOCK_RESPONSES}
        responses["claim_decomposer"] = {
            "sub_claims": [
                {
                    "text": "X",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "urgent",  # not in the literal
                },
            ],
            "original_claim": "X",
            "complexity": "simple",
        }
        client = make_mock_client(responses)
        orch = Orchestrator(client)
        result = orch.run("X")
        # Pipeline degrades rather than ships an invalid literal upstream.
        assert result["degraded"] is True
        assert result["degraded_reason"] is not None
        # The decomposer failure shows up in degraded_reason via the agent
        # boundary (DecomposerAgent.parse_output raises, orchestrator
        # catches, appends "claim_decomposer" to failures).
        assert "decomposer" in result["degraded_reason"].lower()


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

    def test_communication_posture_does_not_co_vary_with_overall_confidence(self):
        """Sprint 2 PR 3 load-bearing safeguard (Codex Risk #6 survival):
        communication_posture is orthogonal to numeric confidence by
        design. Varying posture across all three literals for otherwise-
        identical inputs must not move overall_confidence. This is the
        BG-042 Confidence-Posture Separation contract enforced at the
        pipeline level, not just at the schema level.

        If this test fails, the Bridge posture has been wired into the
        confidence formula -- an architectural violation that invalidates
        Sprint 1's confidence-adjustment discipline and re-opens the
        Sprint 1 Codex Risk #6 attack surface."""
        confidences = []
        for posture in ["direct_correction", "inoculation_first", "relational_first"]:
            responses = {**MOCK_RESPONSES}
            responses["bridge_builder"] = {
                **MOCK_RESPONSES["bridge_builder"],
                "communication_posture": posture,
            }
            client = make_mock_client(responses)
            orch = Orchestrator(client)
            result = orch.run("X is true because Y")
            confidences.append(result["overall_confidence"])
        assert len(set(confidences)) == 1, (
            f"communication_posture moved overall_confidence: {confidences}. "
            f"BG-042 violation: posture is communicative register, not "
            f"confidence input."
        )
        assert confidences[0] == 0.7  # unchanged baseline

    def test_communication_posture_not_referenced_in_confidence_computation(self):
        """Architectural grep-style lock (Klingon + Codex + Sprint 2 PR 3
        fleet convergence): the orchestrator confidence-computation block
        must not reference communication_posture or pattern_density_warning.
        If a future edit wires the posture into the scalar, this test fails
        before the runtime invariance test can trigger.

        Fleet review Round 2 findings (Federation #2, Klingon #2, Borg #2,
        Ferengi redundancy): the sentinel-string-index approach is fragile
        to duplicate sentinels or sentinel renames. Hardening:

        1. Assert BOTH sentinels appear EXACTLY once. Duplicate sentinels
           silently slice the wrong region; zero sentinels raise ValueError
           which may be reported as error rather than failure in CI.
        2. Assert the sentinel START appears BEFORE the sentinel END in
           the source text. A reordered refactor must trip this test.
        3. Use explicit error messages so sentinel drift fails loud.
        """
        import inspect
        from huginn_muninn import orchestrator as orch_module

        source = inspect.getsource(orch_module.Orchestrator.run)
        start_sentinel = "# Compute overall confidence"
        end_sentinel = "# Check for veto"

        # (1) Each sentinel must appear exactly once in the run() source.
        start_count = source.count(start_sentinel)
        end_count = source.count(end_sentinel)
        assert start_count == 1, (
            f"Sentinel {start_sentinel!r} must appear EXACTLY once in "
            f"Orchestrator.run source (found {start_count}). Sprint 2 PR 3 "
            f"fleet-review convergence: duplicate sentinels silently slice "
            f"the wrong region. If you are refactoring the confidence "
            f"block, update this test to reference the new sentinel or "
            f"switch to a line-range extraction."
        )
        assert end_count == 1, (
            f"Sentinel {end_sentinel!r} must appear EXACTLY once in "
            f"Orchestrator.run source (found {end_count})."
        )

        start = source.index(start_sentinel)
        end = source.index(end_sentinel)
        # (2) Sentinel ordering must be preserved.
        assert start < end, (
            f"Sentinel ordering corrupted: {start_sentinel!r} must precede "
            f"{end_sentinel!r} in the source. A refactor may have moved "
            f"the confidence block; update this test or the orchestrator."
        )
        block = source[start:end]
        assert "communication_posture" not in block, (
            "communication_posture referenced inside confidence computation. "
            "Posture is advisory register; must not move overall_confidence."
        )
        assert "pattern_density_warning" not in block, (
            "pattern_density_warning referenced inside confidence computation. "
            "The flag is content-descriptive; must not move confidence."
        )

    def test_priority_does_not_co_vary_with_overall_confidence(self):
        """Holodeck P-roles mitigation / BG-042 Confidence-Posture
        Separation: varying verification_priority across critical/high/low
        must not move overall_confidence for otherwise-identical pipeline
        inputs. This catches any future regression that wires the triage
        field into the confidence computation at orchestrator.py:150-153."""
        from huginn_muninn import orchestrator as orch_module

        confidences = []
        for priority in ["critical", "high", "low"]:
            responses = {**MOCK_RESPONSES}
            responses["claim_decomposer"] = {
                "sub_claims": [
                    {
                        "text": "X happened",
                        "type": "factual",
                        "verifiable": True,
                        "verification_priority": priority,
                    },
                ],
                "original_claim": "X happened",
                "complexity": "simple",
            }
            client = make_mock_client(responses)
            orch = Orchestrator(client)
            result = orch.run("X happened")
            confidences.append(result["overall_confidence"])
        # All three priorities must yield identical overall_confidence
        assert len(set(confidences)) == 1, (
            f"verification_priority moved overall_confidence: {confidences}. "
            f"BG-042 (Confidence-Posture Separation) violation: priority is "
            f"epistemic triage, not confidence input."
        )
        # And the unchanged value must still be the expected baseline (0.7)
        assert confidences[0] == 0.7

    def test_auditor_receives_all_sub_claims_regardless_of_priority(self):
        """Klingon #1 mitigation: the pipeline must pass every sub-claim to
        the Auditor regardless of its verification_priority. A priority of
        'low' must not silently collapse a sub-claim before it reaches the
        Auditor stage. This is the load-bearing invariance guard against
        the suppression-drift exploit: a future UI collapsing 'low'
        sub-claims would be downstream; the pipeline itself must never
        drop a sub-claim based on triage."""
        import json as _json

        captured: list[dict] = []

        def capturing_auditor(self, input_data):
            captured.append(input_data)
            return MOCK_RESPONSES["adversarial_auditor"]

        responses = {**MOCK_RESPONSES}
        responses["claim_decomposer"] = {
            "sub_claims": [
                {
                    "text": "X1",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "critical",
                },
                {
                    "text": "X2",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "high",
                },
                {
                    "text": "X3",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "low",
                },
            ],
            "original_claim": "X1 and X2 and X3",
            "complexity": "complex",
        }
        client = make_mock_client(responses)
        orch = Orchestrator(client)

        # Intercept the auditor run to capture what it actually receives.
        original_run = orch.auditor.run

        def wrapped_run(input_data):
            captured.append(input_data)
            return original_run(input_data)

        orch.auditor.run = wrapped_run
        orch.run("X1 and X2 and X3")

        assert len(captured) == 1, "Auditor must run exactly once per pipeline"
        auditor_input = captured[0]
        decomposition = auditor_input["decomposition"]
        assert len(decomposition["sub_claims"]) == 3, (
            f"Auditor received {len(decomposition['sub_claims'])} sub-claims, "
            f"expected 3. Pipeline must not drop sub-claims based on "
            f"verification_priority."
        )
        priorities = [
            sc["verification_priority"] for sc in decomposition["sub_claims"]
        ]
        assert priorities == ["critical", "high", "low"], (
            f"Auditor received priorities {priorities}, expected "
            f"['critical', 'high', 'low'] in insertion order."
        )

    def test_corrupt_verification_priority_triggers_validation_marker(self, monkeypatch):
        """Codex PR 2 Q3 blind-spot coverage: if the Decomposer parse
        succeeds but something downstream (a buggy post-processor, a cache
        write that mutates the dict, a future agent that edits sub-claims)
        corrupts verification_priority to an unknown literal before the
        final AnalysisReport validation at orchestrator.py:183-188, the
        validation marker must fire and the degraded_reason must contain
        'validation_error'. This is the PR-2-specific version of the
        generic blind-spot #2 test above."""
        from huginn_muninn.agents.base import BaseAgent

        client = make_mock_client(MOCK_RESPONSES)
        orch = Orchestrator(client)

        # Wrap the Decomposer's run() to corrupt verification_priority
        # after parse but before the orchestrator validates the final
        # assembly. This simulates a downstream mutation that schema drift
        # or a buggy normalizer could introduce in production.
        real_run = orch.decomposer.run

        def corrupting_run(input_data):
            out = real_run(input_data)
            for sc in out.get("sub_claims", []):
                sc["verification_priority"] = "urgent"  # invalid literal
            return out

        monkeypatch.setattr(orch.decomposer, "run", corrupting_run)
        result = orch.run("X is true because Y")

        assert result["degraded"] is True
        assert result["degraded_reason"] is not None
        assert "validation_error" in result["degraded_reason"].lower(), (
            f"Expected 'validation_error' in degraded_reason, got: "
            f"{result['degraded_reason']}"
        )
