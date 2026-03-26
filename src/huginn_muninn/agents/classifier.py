"""TTP Classifier -- maps findings to DISARM framework TTPs."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import ClassifierOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt
from huginn_muninn.sources import load_disarm_techniques


class ClassifierAgent(BaseAgent):
    name = "ttp_classifier"

    def system_prompt(self) -> str:
        return (
            "You are a disinformation tactics, techniques, and procedures (TTP) "
            "classifier. You map observed information manipulation behaviors to "
            "the DISARM framework (the MITRE ATT&CK equivalent for disinformation). "
            "Only classify TTPs you have evidence for."
        )

    def build_prompt(self, input_data: dict) -> str:
        techniques = load_disarm_techniques()
        tech_ref = "\n".join(
            f"- {t['id']}: {t['name']} ({t['tactic']}) -- {t['description']}"
            for t in techniques
        )
        upstream = sanitize_for_prompt(json.dumps({
            "sub_claims": input_data.get("sub_claims", []),
            "origins": input_data.get("origins", {}),
            "intelligence": input_data.get("intelligence", {}),
        }, indent=2))
        safe_claim = sanitize_claim(input_data["original_claim"])

        return f"""Classify the disinformation techniques used in this claim: "<claim>{safe_claim}</claim>"

<upstream_analysis>
{upstream}
</upstream_analysis>

DISARM Framework reference:
{tech_ref}

Match observed behaviors to DISARM TTPs. For each match, provide evidence.

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "ttp_matches": [
    {{
      "disarm_id": "TXXXX",
      "technique_name": "Technique name from DISARM",
      "confidence": 0.0-1.0,
      "evidence": "Specific evidence from the analysis that maps to this TTP"
    }}
  ],
  "primary_tactic": "CHOOSE ONE: Plan, Prepare, Execute, Assess"
}}

Rules:
- Only include TTPs with evidence from the upstream analysis
- If no TTPs match, return an empty ttp_matches list
- Confidence reflects strength of evidence, not severity"""

    def parse_output(self, raw: dict) -> dict:
        return ClassifierOutput(**raw).model_dump()
