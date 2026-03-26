"""Intelligence Mapper -- network + actors + motivations (merged agent)."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import MapperOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class MapperAgent(BaseAgent):
    name = "intelligence_mapper"

    def system_prompt(self) -> str:
        return (
            "You are an intelligence analyst specializing in information networks. "
            "Your job is to identify the key actors involved in spreading a narrative, "
            "their motivations, their relationships, and how they form a network. "
            "Be specific about evidence. Do not speculate without flagging uncertainty."
        )

    def build_prompt(self, input_data: dict) -> str:
        safe_claim = sanitize_claim(input_data["original_claim"])
        sub_claims_json = sanitize_for_prompt(json.dumps(input_data["sub_claims"], indent=2))
        origins_json = sanitize_for_prompt(json.dumps(input_data["origins"], indent=2))
        return f"""Analyze the actor network behind this claim: "<claim>{safe_claim}</claim>"

<sub_claims>
{sub_claims_json}
</sub_claims>

<origin_data>
{origins_json}
</origin_data>

Identify:
1. Key actors (who is involved in creating/spreading this narrative)
2. Their motivations (why they promote this narrative)
3. Relationships between actors (who amplifies, funds, coordinates with whom)
4. A narrative summary of the information network

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "actors": [
    {{
      "name": "Actor name or description",
      "type": "CHOOSE ONE: state, media, influencer, organization, bot_network, unknown",
      "motivation": "Why they promote this narrative",
      "credibility": 0.0-1.0,
      "evidence": "What supports this assessment"
    }}
  ],
  "relations": [
    {{
      "source_actor": "actor name",
      "target_actor": "actor name",
      "relation_type": "CHOOSE ONE: amplifies, funds, coordinates, opposes, cites",
      "confidence": 0.0-1.0
    }}
  ],
  "narrative_summary": "How the information network operates"
}}

Guidelines:
- Only include actors you have evidence for
- Credibility 0.0 = known disinformation source, 1.0 = highly credible
- Flag speculative assessments explicitly in the evidence field
- Include both supporters AND opponents of the narrative"""

    def parse_output(self, raw: dict) -> dict:
        return MapperOutput(**raw).model_dump()
