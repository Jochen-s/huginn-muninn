"""Method 2 pipeline orchestrator with circuit breakers and fallback."""
from __future__ import annotations

import logging

from pydantic import ValidationError

from huginn_muninn.agents.auditor import AuditorAgent
from huginn_muninn.agents.base import AgentError
from huginn_muninn.agents.bridge import BridgeAgent
from huginn_muninn.agents.classifier import ClassifierAgent
from huginn_muninn.agents.decomposer import DecomposerAgent
from huginn_muninn.agents.mapper import MapperAgent
from huginn_muninn.agents.tracer import TracerAgent
from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.llm import LLMClient

log = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the 6-agent Method 2 pipeline."""

    def __init__(self, client: LLMClient):
        self.client = client
        self.decomposer = DecomposerAgent(client)
        self.tracer = TracerAgent(client)
        self.mapper = MapperAgent(client)
        self.classifier = ClassifierAgent(client)
        self.bridge = BridgeAgent(client)
        self.auditor = AuditorAgent(client)

    def run(self, claim: str) -> dict:
        """Run the full Method 2 pipeline. Returns an AnalysisReport dict."""
        failures: list[str] = []

        # Stage 1: Decompose (critical -- if this fails, degrade immediately)
        decomposition = self._run_agent(
            self.decomposer, {"claim": claim}, failures,
        )
        if decomposition is None:
            return self._degraded_result(claim, failures)

        sub_claims = decomposition.get("sub_claims", [])
        context = {"original_claim": claim, "sub_claims": sub_claims}

        # Stage 2: Origin tracing
        origins = self._run_agent(self.tracer, {**context}, failures)
        origins = origins or {"origins": [], "mutations": []}
        context["origins"] = origins

        # Stage 3: Intelligence mapping
        intelligence = self._run_agent(self.mapper, {**context}, failures)
        intelligence = intelligence or {"actors": [], "relations": [], "narrative_summary": ""}
        context["intelligence"] = intelligence

        # Stage 4: TTP Classifier + Bridge Builder (sequential; async deferred)
        ttps = self._run_agent(self.classifier, {**context}, failures)
        ttps = ttps or {"ttp_matches": [], "primary_tactic": "Assess"}
        context["ttps"] = ttps

        bridge = self._run_agent(self.bridge, {**context}, failures)
        bridge = bridge or {
            "universal_needs": ["unknown"],
            "issue_overlap": "",
            "narrative_deconstruction": "",
            "inferential_gap": "",
            "feasibility_check": "",
            "commercial_motives": "",
            "perception_gap": "",
            "moral_foundations": {},
            "reframe": "",
            "socratic_dialogue": ["Bridge analysis unavailable"],
        }

        # Stage 5: Adversarial Audit
        audit = self._run_agent(
            self.auditor,
            {
                "original_claim": claim,
                "decomposition": decomposition,
                "origins": origins,
                "intelligence": intelligence,
                "ttps": ttps,
                "bridge": bridge,
            },
            failures,
        )
        audit = audit or {
            "verdict": "pass_with_warnings",
            "findings": [{"category": "quality", "severity": "medium",
                          "description": "Auditor unavailable", "recommendation": "Manual review"}],
            "confidence_adjustment": -0.1,
            "veto": False,
            "summary": "Auditor agent failed; results unverified",
        }

        # Compute overall confidence
        base_confidence = 0.7
        confidence_adj = audit.get("confidence_adjustment", 0.0)
        failure_penalty = len(failures) * 0.1
        overall = max(0.0, min(1.0, base_confidence + confidence_adj - failure_penalty))

        # Check for veto
        vetoed = audit.get("veto", False)
        degraded = vetoed or len(failures) > 0
        degraded_reason = None
        if vetoed:
            degraded_reason = f"Auditor veto: {audit.get('summary', '')}"
        elif failures:
            degraded_reason = f"Agent failures: {', '.join(failures)}"

        result = {
            "claim": claim,
            "decomposition": decomposition,
            "origins": origins,
            "intelligence": intelligence,
            "ttps": ttps,
            "bridge": bridge,
            "audit": audit,
            "overall_confidence": round(overall, 3),
            "method": "method_2",
            "degraded": degraded,
            "degraded_reason": degraded_reason,
        }

        # Validate against the contract at the production boundary
        try:
            AnalysisReport(**result)
        except ValidationError as e:
            log.error("Pipeline produced invalid output: %s", e)
            return self._degraded_result(claim, failures)

        return result

    def _run_agent(self, agent, input_data: dict, failures: list[str]) -> dict | None:
        """Run a single agent with error handling."""
        try:
            return agent.run(input_data)
        except AgentError as e:
            log.warning("Agent %s failed: %s", agent.name, e)
            failures.append(agent.name)
            return None

    def _degraded_result(self, claim: str, failures: list[str]) -> dict:
        """Return a minimal degraded result when critical agents fail."""
        return {
            "claim": claim,
            "decomposition": {
                "sub_claims": [{"text": claim, "type": "factual", "verifiable": False}],
                "original_claim": claim,
                "complexity": "simple",
            },
            "origins": {"origins": [], "mutations": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["unknown"], "issue_overlap": "", "narrative_deconstruction": "",
                "inferential_gap": "", "feasibility_check": "", "commercial_motives": "",
                "perception_gap": "", "moral_foundations": {}, "reframe": "",
                "socratic_dialogue": ["Analysis unavailable"],
            },
            "audit": {
                "verdict": "fail", "findings": [], "confidence_adjustment": 0,
                "veto": False, "summary": "Pipeline degraded due to critical agent failure",
            },
            "overall_confidence": 0.0,
            "method": "method_2",
            "degraded": True,
            "degraded_reason": f"Critical agent failure: {', '.join(failures)}. Use Method 1 (huginn check) for this claim.",
        }
