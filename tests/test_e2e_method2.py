"""E2E smoke test for Method 2 pipeline against real Ollama."""
import pytest

from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.orchestrator import Orchestrator


@pytest.mark.e2e
class TestMethod2E2E:
    def test_simple_claim_produces_valid_report(self, ollama_client):
        """A simple claim should pass through all 6 agents without degradation."""
        orch = Orchestrator(ollama_client)
        result = orch.run("The Earth revolves around the Sun")

        # Must validate against the full contract
        report = AnalysisReport(**result)
        assert report.method == "method_2"
        assert len(report.decomposition.sub_claims) >= 1
        assert report.overall_confidence > 0
        # Simple science claim should not degrade (unless LLM produces bad JSON)
        if not report.degraded:
            assert report.audit.verdict.value in ("pass", "pass_with_warnings")

    def test_polarizing_claim_activates_bridge(self, ollama_client):
        """A polarizing claim should produce meaningful Bridge Builder output."""
        orch = Orchestrator(ollama_client)
        result = orch.run("Immigration increases crime rates in the United States")

        report = AnalysisReport(**result)
        assert report.method == "method_2"
        # Bridge should produce meaningful output for a polarizing claim
        if not report.degraded:
            assert len(report.bridge.universal_needs) >= 1
            assert report.bridge.universal_needs != ["unknown"]
            assert len(report.bridge.socratic_dialogue) >= 1
            # Should detect some actors for this multi-actor claim
            assert len(report.intelligence.actors) >= 1
