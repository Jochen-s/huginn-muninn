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
            "original source to current form."
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
      "mutation_type": "CHOOSE ONE: distortion, amplification, recontextualization, fabrication",
      "source": "where the mutation occurred"
    }}
  ]
}}

Source tiers: 1=scientific/governmental, 2=established journalism, 3=regional/specialized, 4=social media/unknown"""

    def parse_output(self, raw: dict) -> dict:
        return TracerOutput(**raw).model_dump()
