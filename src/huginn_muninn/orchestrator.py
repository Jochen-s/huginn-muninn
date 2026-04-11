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


# Zero-token deterministic helper: computes a hypothesis-space expansion score
# from existing Decomposer output fields. Not an entropy calculation and not a
# quantum formalism -- literal density-matrix math was deliberately avoided as
# false precision without a concrete Hilbert-space construction. Score feeds
# the Auditor's context under "gorgon_signals" so frame-capture assessment can
# be gated on a reproducible signal rather than LLM re-inference.
_COMPLEXITY_SCORES: dict[str, float] = {
    "simple": 1.0,
    "moderate": 1.25,
    "complex": 1.5,
    "multi_actor": 1.75,
}


def _compute_hypothesis_expansion_score(decomposition: dict) -> float:
    """Derive a hypothesis-expansion signal from the Decomposer output.

    Bounded 0.0-1.0. Rises with sub-claim count, density of causal sub-claims,
    and declared complexity. Deterministic: adds zero LLM tokens.
    """
    sub_claims = decomposition.get("sub_claims") or []
    if not sub_claims:
        return 0.0
    causal_count = sum(
        1 for s in sub_claims if isinstance(s, dict) and s.get("type") == "causal"
    )
    causal_weight = 1.5 if causal_count > 2 else 1.0
    complexity_weight = _COMPLEXITY_SCORES.get(
        decomposition.get("complexity", "simple"), 1.0,
    )
    raw = (len(sub_claims) / 5) * causal_weight * complexity_weight
    return round(min(1.0, raw), 3)


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
        origins = origins or {"origins": [], "mutations": [], "notable_omissions": []}
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
            "consensus_explanation": "",
            "inferential_gap": "",
            "feasibility_check": "",
            "commercial_motives": "",
            "techniques_revealed": [],
            "perception_gap": "",
            "moral_foundations": {},
            "reframe": "",
            "socratic_dialogue": ["Bridge analysis unavailable"],
        }

        # Stage 5: Adversarial Audit
        # Gorgon Trap P1 #5: compute deterministic hypothesis-expansion signal
        # from the Decomposer output and pass it to the Auditor so it can gate
        # frame_capture_risk assessment without an additional LLM call.
        gorgon_signals = {
            "hypothesis_expansion_score": _compute_hypothesis_expansion_score(decomposition),
            "hypothesis_crowding": decomposition.get("hypothesis_crowding", "low"),
            "notable_omissions_count": len(origins.get("notable_omissions", []) or []),
            "has_gt_ttps": any(
                (m.get("disarm_id") or "").startswith("GT-")
                for m in ttps.get("ttp_matches", []) or []
            ),
        }
        audit = self._run_agent(
            self.auditor,
            {
                "original_claim": claim,
                "decomposition": decomposition,
                "origins": origins,
                "intelligence": intelligence,
                "ttps": ttps,
                "bridge": bridge,
                "gorgon_signals": gorgon_signals,
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
            "frame_capture_risk": "none",
            "frame_capture_evidence": "",
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

        # Validate against the contract at the production boundary. If the
        # final assembly does not match the schema -- typically because a new
        # contract field was added but the orchestrator fallback path was not
        # updated to carry its default -- surface the failure in the degraded
        # reason rather than masking it as a generic "critical agent failure".
        try:
            AnalysisReport(**result)
        except ValidationError as e:
            log.error("Pipeline produced invalid output: %s", e)
            # Sprint 2 PR 2 / Federation mitigation: include the exception
            # type name in the marker so downstream log aggregators can
            # distinguish schema drift from other validation failures. The
            # existing "validation_error" prefix is preserved so earlier
            # regression tests continue to match via substring / lowercase
            # containment.
            failures.append(f"validation_error:{type(e).__name__}")
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
                "sub_claims": [
                    {
                        "text": claim,
                        "type": "factual",
                        "verifiable": False,
                        # Sprint 2 P2-7: triage default is "low" in the
                        # fallback path. When every agent has failed, we have
                        # no evidence that this sub-claim deserves higher
                        # verification priority; inflating it would violate
                        # the anti-inflation discipline shipped in PR 2.
                        "verification_priority": "low",
                    },
                ],
                "original_claim": claim,
                "complexity": "simple",
                # Fallback must carry every schema default so AnalysisReport
                # validation succeeds even when every agent call failed.
                "hypothesis_crowding": "low",
                "manipulation_vector_density": 0.0,
                "complexity_explosion_flag": False,
            },
            "origins": {"origins": [], "mutations": [], "notable_omissions": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["unknown"], "issue_overlap": "", "narrative_deconstruction": "",
                "consensus_explanation": "",
                "inferential_gap": "", "feasibility_check": "", "commercial_motives": "",
                "techniques_revealed": [],
                "perception_gap": "", "moral_foundations": {}, "reframe": "",
                "socratic_dialogue": ["Analysis unavailable"],
            },
            "audit": {
                "verdict": "fail", "findings": [], "confidence_adjustment": 0,
                "veto": False, "summary": "Pipeline degraded due to critical agent failure",
                "frame_capture_risk": "none",
                "frame_capture_evidence": "",
            },
            "overall_confidence": 0.0,
            "method": "method_2",
            "degraded": True,
            "degraded_reason": f"Critical agent failure: {', '.join(failures)}. Use Method 1 (huginn check) for this claim.",
        }
