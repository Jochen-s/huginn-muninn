"""Origin Tracer -- finds earliest mentions and tracks narrative mutations."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import TracerOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class TracerAgent(BaseAgent):
    name = "origin_tracer"

    def system_prompt(self) -> str:
        return (
            "You are an origin tracer for information analysis. Your job is "
            "to identify where claims first appeared, how they propagated, "
            "and how the narrative mutated as it spread. Track the chain from "
            "original source to current form. "
            "Report only what is evident in the claim text or sources you can "
            "identify. Do not attribute motive, intent, or suppression where "
            "none is explicitly visible."
        )

    def build_prompt(self, input_data: dict) -> str:
        safe_claim = sanitize_claim(input_data["original_claim"])
        sub_claims_json = sanitize_for_prompt(json.dumps(input_data["sub_claims"], indent=2))
        return f"""Trace the origins and propagation of these sub-claims from the claim: "<claim>{safe_claim}</claim>"

<sub_claims>
{sub_claims_json}
</sub_claims>

For each sub-claim, identify:
1. The earliest known source and approximate date
2. The propagation path (how it spread)
3. Any mutations in the narrative as it spread

CRITICAL: Track TEMPORAL CONTEXT SHIFTS. Many claims migrate between ideological camps over time as power dynamics change. For example, "media is controlled by elites" was a left-wing critique (Chomsky 1988) that was adopted by right-wing populism (Trump 2017) and now applies paradoxically to the adopters' own media ecosystem. Map these ideological migrations explicitly.

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "origins": [
    {{
      "sub_claim": "the sub-claim text",
      "earliest_source": "URL or description of earliest source",
      "earliest_date": "YYYY-MM-DD or null if unknown",
      "source_tier": 1-4,
      "propagation_path": ["source1", "source2", "..."]
    }}
  ],
  "mutations": [
    {{
      "original": "original statement from source",
      "mutated": "how it was changed",
      "mutation_type": "CHOOSE ONE: distortion, amplification, recontextualization, fabrication, ideological_migration, inversion",
      "relay_type": "CHOOSE ONE: knowing, unknowing, ambiguous",
      "source": "where the mutation occurred"
    }}
  ],
  "temporal_context": [
    {{
      "era": "descriptive label for the time period",
      "date_range": "YYYY to YYYY",
      "dominant_framing": "which ideological camp primarily used this claim and how",
      "key_actors": ["who promoted it in this era"],
      "power_context": "what power dynamics made this framing relevant",
      "irony_or_inversion": "if the claim now applies to those who adopted it, describe the paradox"
    }}
  ],
  "notable_omissions": ["source type string", "..."]
}}

Source tiers: 1=scientific/governmental, 2=established journalism, 3=regional/specialized, 4=social media/unknown

Mutation types:
- distortion: factual claim altered to change meaning
- amplification: claim exaggerated beyond evidence
- recontextualization: claim placed in misleading context
- fabrication: claim invented without factual basis
- ideological_migration: claim adopted by a different political camp with altered framing
- inversion: claim now applies to those who adopted it (the paradox you must detect)

relay_type (per mutation):
- knowing: mutation was clearly intentional based on explicit context in the claim or identified sources
- unknowing: mutation appears to result from honest misunderstanding or error, based on explicit context
- ambiguous: intent is not clearly visible; DEFAULT to this when in doubt. Do not speculate about mental states.

notable_omissions rules:
- List SOURCE TYPES (e.g., "peer-reviewed primary research on this topic", "contemporaneous official statements", "regional news coverage from the era") that would be expected for this claim's topic and time period but are MISSING from the claim text or the context you identified.
- Phrasing must reflect absence relative to expectation. Do NOT use language such as censored, suppressed, hidden, blocked, or deliberately omitted.
- Do NOT invent specific source names, journal titles, or author names. Report only source type categories.
- Return an empty list when no clear omissions are evident. Default behavior is an empty list.
- Only add an entry when there is a specific, topic-anchored absence you can articulate.
- Maximum 3 entries. If you identify more than 3 candidates, select the 3 most salient."""

    def parse_output(self, raw: dict) -> dict:
        return TracerOutput(**raw).model_dump()
