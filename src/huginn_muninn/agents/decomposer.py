"""Claim Decomposer -- breaks claims into verifiable sub-claims."""
from __future__ import annotations

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import DecomposerOutput
from huginn_muninn.prompt import sanitize_claim


class DecomposerAgent(BaseAgent):
    name = "claim_decomposer"

    def system_prompt(self) -> str:
        return (
            "You are a claim decomposition specialist. Your job is to break "
            "complex claims into individual, verifiable sub-claims. Classify "
            "each sub-claim by type: factual (can be checked against data), "
            "opinion (subjective judgment), prediction (about the future), "
            "value (moral/ethical stance), or causal (X causes Y)."
        )

    def build_prompt(self, input_data: dict) -> str:
        safe_claim = sanitize_claim(input_data["claim"])
        return f"""Decompose the following claim into its component sub-claims.

<claim>{safe_claim}</claim>

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "sub_claims": [
    {{"text": "individual verifiable statement", "type": "CHOOSE ONE: factual, opinion, prediction, value, causal", "verifiable": true or false, "verification_priority": "CHOOSE ONE: critical, high, low"}}
  ],
  "original_claim": "the original claim text",
  "complexity": "CHOOSE ONE: simple, moderate, complex, multi_actor",
  "hypothesis_crowding": "CHOOSE ONE: low, medium, high",
  "manipulation_vector_density": 0.0,
  "complexity_explosion_flag": false
}}

Rules:
- Each sub-claim should be independently verifiable where possible
- Identify implicit assumptions as separate sub-claims
- Mark causal claims explicitly (X causes/leads to Y)
- "simple" = single factual claim, "moderate" = 2-3 sub-claims, "complex" = 4+ or nested logic, "multi_actor" = involves multiple groups/entities

Annotation rules for the four new fields:
- hypothesis_crowding: Count the number of plausible competing interpretations of the INPUT FRAMING itself — not claim severity, not claim falsehood, not sub-claim count. low = 1 dominant interpretive framing; medium = 2 competing framings visible; high = 3+ competing framings OR the input appears designed to invite multiple incompatible readings. When not clearly evident, default to "low". Sub-claim count is determined by the claim's actual structure, NOT by this field. Do not increase the sub-claim list to justify a higher crowding rating. This is a qualitative heuristic. Do not attempt to compute entropy, density matrices, or numeric probability distributions.
- manipulation_vector_density: Estimated ratio (0.0-1.0) of sub-claims whose most natural interpretation opens a manipulation surface (causal insinuation, selective framing, implicit premises), versus total sub-claims. Default 0.0 when no such surfaces are apparent. This is a qualitative estimate.
- complexity_explosion_flag: Set to true only when (sub-claim count >= 5 AND at least 40% of sub-claims are of type "causal"). Otherwise false.
- verification_priority: INTERNAL TRIAGE SIGNAL ONLY -- describes how urgently a sub-claim needs independent verification by the downstream pipeline. This is not an evidentiary rating, not a credibility judgement, and not a legal classification; it is a resource-allocation heuristic for downstream fact-checking work. The "critical" label does NOT assert that any allegation in the sub-claim is true; it asserts that IF false, the sub-claim would be high-impact enough to warrant prioritised verification. Use EXACTLY these values: "critical" = the sub-claim makes a specific falsifiable assertion about a named actor's actions, a documented numeric harm threshold, or a public-safety-relevant factual claim that, if false, would cause material downstream harm; "high" = the sub-claim carries substantive factual weight that meaningfully shapes the reader's conclusion but does not meet the critical bar; "low" = the sub-claim is interpretive, subjective, opinion, widely-established background, or non-falsifiable. When in doubt, choose "low". Anti-inflation clause: marking everything "critical" defeats the triage purpose and degrades downstream resource allocation; a well-triaged output for most claims is mostly "low" with one or two "high" items, with "critical" reserved for structurally high-impact factual assertions. This is a qualitative triage heuristic; do not mark a sub-claim critical merely because its topic is politically charged or emotionally loaded, or because the claim references a named individual or institution. Opinion and value sub-claims default to "low" unless the opinion makes a falsifiable factual assertion embedded inside it. Do not use legal-register language ("guilty", "culpable", "unlawful") in the triage decision; the classifier reasoning must stay at the structural-signature level."""

    def parse_output(self, raw: dict) -> dict:
        return DecomposerOutput(**raw).model_dump()
