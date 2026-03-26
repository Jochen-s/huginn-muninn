"""Bridge Builder -- Common Humanity analysis agent."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import BridgeOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class BridgeAgent(BaseAgent):
    name = "bridge_builder"

    def system_prompt(self) -> str:
        return (
            "You are a Bridge Builder -- a Common Humanity analyst. Your job is "
            "to find the shared human values beneath divisive narratives, show HOW "
            "people are being manipulated, and find common ground between polarized "
            "positions. You speak with warmth, curiosity, and directness. You never "
            "use controlling language ('the truth is...', 'experts agree...') and "
            "never confront identity ('you were misled', 'you fell for...'). "
            "Your goal is to unite, not divide, while maintaining factual rigor."
        )

    def build_prompt(self, input_data: dict) -> str:
        upstream = sanitize_for_prompt(json.dumps({
            "sub_claims": input_data.get("sub_claims", []),
            "origins": input_data.get("origins", {}),
            "intelligence": input_data.get("intelligence", {}),
            "ttps": input_data.get("ttps", {}),
        }, indent=2))
        safe_claim = sanitize_claim(input_data["original_claim"])

        return f"""Analyze the common humanity beneath this claim: "<claim>{safe_claim}</claim>"

<upstream_analysis>
{upstream}
</upstream_analysis>

Produce a three-layer Common Humanity analysis:

Layer 1 - Universal Human Needs: What fundamental need is at stake (safety, belonging, fairness, dignity, autonomy)?
Layer 2 - Issue-Specific Overlap: Where do opposing positions concretely agree? Cite evidence (polling, policy, stated positions).
Layer 3 - Narrative Deconstruction: How was the same underlying concern split into opposing narratives? Who performed the split and why?

Also produce a 3-round Socratic dialogue script following the Costello protocol:
- Round 1: Perspective-getting (summarize their view, acknowledge the kernel of truth)
- Round 2: Personalized counter-evidence as question (address THEIR specific evidence, introduce manipulation technique)
- Round 3: Complexity + common ground (add dimensions, present shared data, close with reflection question)

Respond in JSON:
{{
  "universal_needs": ["need1", "need2"],
  "issue_overlap": "Concrete agreement between opposing positions, with evidence",
  "narrative_deconstruction": "How the same concern was split into opposing narratives",
  "perception_gap": "Where groups overestimate opponent extremism, with data if available",
  "moral_foundations": {{"side_a": ["foundation1"], "side_b": ["foundation2"]}},
  "reframe": "The claim reframed in terms of shared values",
  "socratic_dialogue": [
    "Round 1: Perspective-getting...",
    "Round 2: Counter-evidence as question...",
    "Round 3: Complexity + common ground..."
  ]
}}

Critical constraints:
- NEVER more than 3 dialogue rounds
- NEVER use controlling language
- NEVER confront identity
- ALWAYS close dialogue with a question
- ALWAYS ground claims in evidence where possible
- If no genuine common ground exists, say so honestly rather than forcing synthesis"""

    def parse_output(self, raw: dict) -> dict:
        # LLMs sometimes exceed the 3-round limit despite prompt constraints
        if "socratic_dialogue" in raw and len(raw["socratic_dialogue"]) > 3:
            raw["socratic_dialogue"] = raw["socratic_dialogue"][:3]
        return BridgeOutput(**raw).model_dump()
