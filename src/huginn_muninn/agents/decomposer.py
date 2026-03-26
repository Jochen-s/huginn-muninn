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
    {{"text": "individual verifiable statement", "type": "CHOOSE ONE: factual, opinion, prediction, value, causal", "verifiable": true or false}}
  ],
  "original_claim": "the original claim text",
  "complexity": "CHOOSE ONE: simple, moderate, complex, multi_actor"
}}

Rules:
- Each sub-claim should be independently verifiable where possible
- Identify implicit assumptions as separate sub-claims
- Mark causal claims explicitly (X causes/leads to Y)
- "simple" = single factual claim, "moderate" = 2-3 sub-claims, "complex" = 4+ or nested logic, "multi_actor" = involves multiple groups/entities"""

    def parse_output(self, raw: dict) -> dict:
        return DecomposerOutput(**raw).model_dump()
