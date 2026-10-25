"""Intelligence Mapper -- network + actors + motivations (merged agent)."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import MapperOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class MapperAgent(BaseAgent):
    name = "intelligence_mapper"
    output_model = MapperOutput

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

ACCURACY OVER COMPLETENESS: You have no search tool, only what you already know. Name a person, outlet, organization or state as an actor ONLY if you are confident it publicly promoted, amplified or opposed this specific claim. If you know only that the claim circulates, describe the actor generically with type "unknown" rather than naming someone. Use type "bot_network" only for coordinated inauthentic activity that a published investigation documented for this claim; widespread sharing is not evidence of bots. Use the relation types "funds" and "coordinates" only for documented financial or organizational links; shared views or similar wording are at most "cites" or "amplifies", and otherwise no relation. Do not label any actor a disinformation source unless that rating is documented; describe its record neutrally instead. Do not drop an actor whose role in this claim is well documented (by public investigations, court records, internal documents or its own statements): name it, because leaving out a documented actor is also an error. Fewer actors and no relations are better than invented ones: readers will check names and links, and one invented connection discredits the whole analysis.

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "actors": [
    {{
      "name": "Actor name or description",
      "type": "CHOOSE ONE: state, media, influencer, organization, bot_network, unknown",
      "motivation": "Why they promote this narrative",
      "credibility_basis": "What is documented about the actor's record, or 'not assessed'. Do NOT use numeric scores.",
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
- In the evidence field, say what the assessment rests on; mark anything uncertain as uncertain
- Include documented opponents of the narrative as well as supporters; do not invent either"""

    def parse_output(self, raw: dict) -> dict:
        return MapperOutput(**raw).model_dump()
