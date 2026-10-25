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
from huginn_muninn.contracts import AnalysisReport, _sanitize_for_log, absent_bridge
from huginn_muninn.llm import LLMClient
from huginn_muninn.sources import known_source_tier

log = logging.getLogger(__name__)


_SOURCE_TIER_SCORES: dict[int, float] = {1: 0.95, 2: 0.80, 3: 0.50, 4: 0.20}


def _effective_source_tier(entry: object) -> int:
    """Tier for one Tracer origin: the domain registry wins where it knows the domain.

    The Tracer assigns `source_tier` to itself, so the deterministic registry in
    `sources.py` is consulted first: when `earliest_source` is a URL on a listed
    domain, that tier is used, including the listed tier-4 platforms (a Telegram
    post cannot be self-reported as tier 1); unknown domains and non-URL sources
    keep the LLM tier. Before 2026-09-03 the registry had no caller and the
    number rested on the model's self-report alone."""
    if not isinstance(entry, dict):
        return 4
    llm_tier = entry.get("source_tier", 4)
    src = entry.get("earliest_source", "")
    if isinstance(src, str) and src.strip().lower() == "unknown":
        return 4  # a source nobody can name cannot be rated above the floor
    if isinstance(src, str) and src.lower().startswith(("http://", "https://")):
        registry_tier = known_source_tier(src)
        if registry_tier is not None:
            return registry_tier
    return llm_tier if isinstance(llm_tier, int) else 4

_CONFIDENCE_COMPLEXITY_DAMPENER: dict[str, float] = {
    "simple": 1.0,
    "moderate": 0.9,
    "complex": 0.8,
    "multi_actor": 0.7,
}


def _compute_source_quality_base(origins: dict, decomposition: dict) -> float:
    """Derive confidence base from upstream signal quality. Deterministic.

    When the Tracer returns valid origins with source tiers, the base reflects
    the mean quality of those sources dampened by claim complexity. When the
    Tracer fails (empty origins), falls back to 0.5 (unknown quality).
    """
    entries = origins.get("origins", [])
    if not entries:
        return 0.5
    scores = [
        _SOURCE_TIER_SCORES.get(_effective_source_tier(e), 0.20)
        for e in entries
    ]
    tier_mean = sum(scores) / len(scores)
    complexity = decomposition.get("complexity", "simple")
    dampener = _CONFIDENCE_COMPLEXITY_DAMPENER.get(complexity, 1.0)
    return round(min(1.0, tier_mean * dampener), 3)


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


def _absent_audit(verdict: str, summary: str, findings: list[dict] | None = None,
                  confidence_adjustment: float = 0.0, veto: bool = False) -> dict:
    """An AuditorOutput-shaped dict for the paths where no Auditor output ships.

    veto is False unless the caller is preserving a veto the Auditor did
    issue (a vetoed report that failed final validation); the orchestrator
    never fabricates one."""
    return {
        "verdict": verdict,
        "findings": findings or [],
        "confidence_adjustment": confidence_adjustment,
        "veto": veto,
        "summary": summary,
        "frame_capture_risk": "none",
        "frame_capture_evidence": "",
        "confidence_profile": None,
        "cnqs": None,
    }


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
        # Write the registry-corrected tier back into the data the report
        # ships, so the tier a reader sees is the tier the score used
        # (review finding, 2026-09-03: a WHO link showed T4 beside 0.95).
        for entry in origins.get("origins", []) or []:
            if isinstance(entry, dict):
                entry["source_tier"] = _effective_source_tier(entry)
        context["origins"] = origins

        # Stage 3: Intelligence mapping
        intelligence = self._run_agent(self.mapper, {**context}, failures)
        intelligence = intelligence or {"actors": [], "relations": [], "narrative_summary": "", "convergence_matrix": None}
        context["intelligence"] = intelligence

        # Stage 4: TTP Classifier + Bridge Builder (sequential; async deferred)
        ttps = self._run_agent(self.classifier, {**context}, failures)
        ttps = ttps or {"ttp_matches": [], "primary_tactic": "Assess"}
        context["ttps"] = ttps

        bridge = self._run_agent(self.bridge, {**context}, failures)
        bridge = bridge or absent_bridge("Bridge analysis unavailable")

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
        # No Auditor ran, so nothing was checked: the label says so instead
        # of reading as a pass with warnings (decided 2026-09-03).
        audit = audit or _absent_audit(
            "unaudited", "Auditor agent failed; results unaudited",
            findings=[{"category": "quality", "severity": "medium",
                       "description": "Auditor unavailable", "recommendation": "Manual review"}],
            confidence_adjustment=-0.1,
        )

        # Compute overall confidence
        base_confidence = _compute_source_quality_base(origins, decomposition)
        confidence_adj = audit.get("confidence_adjustment", 0.0)
        failure_penalty = len(failures) * 0.1
        overall = max(0.0, min(1.0, base_confidence + confidence_adj - failure_penalty))

        # Check for veto
        vetoed = audit.get("veto", False)
        degraded = vetoed or len(failures) > 0
        degraded_reason = None
        if vetoed:
            degraded_reason = f"Auditor veto: {audit.get('summary', '')}"
            # Decided 2026-09-03: a veto is a stop, not a flag. The Bridge
            # layer is withheld and replaced by the veto reason; the evidence
            # layer (decomposition, origins, actors, TTPs, audit findings)
            # ships so the reader can see why the stop fired. The withholding
            # itself is done by AnalysisReport.veto_withholds_bridge at the
            # validation below, so cached and replayed reports get it too.
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
            "confidence_profile": audit.get("confidence_profile"),
            "cnqs": audit.get("cnqs"),
        }

        # Validate against the contract at the production boundary. If the
        # final assembly does not match the schema -- typically because a new
        # contract field was added but the orchestrator fallback path was not
        # updated to carry its default -- surface the failure in the degraded
        # reason rather than masking it as a generic "critical agent failure".
        try:
            AnalysisReport(**result)
        except ValidationError as e:
            log.error("Pipeline produced invalid output: %s", _sanitize_for_log(str(e)))
            # Sprint 2 PR 2 / Federation mitigation: include the exception
            # type name in the marker so downstream log aggregators can
            # distinguish schema drift from other validation failures. The
            # existing "validation_error" prefix is preserved so earlier
            # regression tests continue to match via substring / lowercase
            # containment.
            failures.append(f"validation_error:{type(e).__name__}")
            return self._degraded_result(
                claim, failures,
                veto_summary=str(audit.get("summary", "")) if vetoed else None,
            )

        return AnalysisReport(**result).model_dump(mode="json")

    def _run_agent(self, agent, input_data: dict, failures: list[str]) -> dict | None:
        """Run a single agent with error handling."""
        try:
            return agent.run(input_data)
        except AgentError as e:
            log.warning("Agent %s failed: %s", agent.name, _sanitize_for_log(str(e)))
            failures.append(agent.name)
            return None

    def _degraded_result(self, claim: str, failures: list[str],
                         veto_summary: str | None = None) -> dict:
        """Return a minimal degraded result when critical agents fail.

        veto_summary is set when a vetoed report failed final validation: the
        veto the Auditor issued is preserved instead of being replaced by a
        no-Auditor audit (review finding, 2026-09-03)."""
        if veto_summary is not None:
            audit = _absent_audit("fail", f"Auditor veto: {veto_summary}", veto=True)
            reason = (
                f"Auditor veto: {veto_summary}. Critical agent failure: {', '.join(failures)}. "
                "Use Method 1 (huginn check) for this claim."
            )
        else:
            audit = _absent_audit(
                "unaudited", "Pipeline degraded due to critical agent failure; no Auditor ran",
            )
            reason = f"Critical agent failure: {', '.join(failures)}. Use Method 1 (huginn check) for this claim."
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
            "intelligence": {"actors": [], "relations": [], "narrative_summary": "", "convergence_matrix": None},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": absent_bridge(
                f"Bridge layer withheld: Auditor veto: {veto_summary}" if veto_summary is not None
                else "Analysis unavailable",
                needs="withheld" if veto_summary is not None else "unknown",
            ),
            "audit": audit,
            "overall_confidence": 0.0,
            "confidence_profile": None,
            "cnqs": None,
            "method": "method_2",
            "degraded": True,
            "degraded_reason": reason,
            "bridge_withheld": veto_summary is not None,
        }
