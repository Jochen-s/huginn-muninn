"""E2E smoke test for Method 2 pipeline against a real model (see conftest E2E_PROVIDER)."""
import pytest

from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.orchestrator import Orchestrator
from conftest import E2E_STRICT, assert_no_agent_failures


@pytest.mark.e2e
class TestMethod2E2E:
    def test_simple_claim_produces_valid_report(self, llm_client):
        """A simple claim should pass through all 6 agents without degradation."""
        orch = Orchestrator(llm_client)
        result = orch.run("The Earth revolves around the Sun")
        assert_no_agent_failures(result)

        # Must validate against the full contract
        report = AnalysisReport(**result)
        assert report.method == "method_2"
        assert len(report.decomposition.sub_claims) >= 1
        assert report.overall_confidence > 0
        # Simple science claim should not degrade (unless LLM produces bad JSON)
        if not report.degraded:
            assert report.audit.verdict.value in ("pass", "pass_with_warnings")

    def test_polarizing_claim_activates_bridge(self, llm_client):
        """A polarizing claim should produce meaningful Bridge Builder output."""
        orch = Orchestrator(llm_client)
        result = orch.run("Immigration increases crime rates in the United States")
        assert_no_agent_failures(result)

        report = AnalysisReport(**result)
        assert report.method == "method_2"
        # Bridge should produce meaningful output for a polarizing claim;
        # a veto withholds the bridge, so it is checked only without one
        if not report.degraded:
            assert len(report.bridge.universal_needs) >= 1
            assert report.bridge.universal_needs != ["unknown"]
            assert len(report.bridge.socratic_dialogue) >= 1
        # The actor analysis ships under a veto too
        if not report.degraded or E2E_STRICT:
            assert len(report.intelligence.actors) >= 1
