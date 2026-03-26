"""Adversarial Auditor -- quality gate with veto power."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import BaseAgent
from huginn_muninn.contracts import AuditorOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class AuditorAgent(BaseAgent):
    name = "adversarial_auditor"

    def system_prompt(self) -> str:
        return (
            "You are an Adversarial Auditor for disinformation analysis. Your job "
            "is to find flaws, biases, and errors in the analysis produced by other "
            "agents. You are a constructive quality gate: document issues as findings "
            "with severity ratings so they can be fixed. You rarely veto -- almost "
            "all issues should be reported as findings with verdict=pass_with_warnings. "
            "Be rigorous but proportionate."
        )

    def build_prompt(self, input_data: dict) -> str:
        all_outputs = sanitize_for_prompt(json.dumps({
            "decomposition": input_data.get("decomposition", {}),
            "origins": input_data.get("origins", {}),
            "intelligence": input_data.get("intelligence", {}),
            "ttps": input_data.get("ttps", {}),
            "bridge": input_data.get("bridge", {}),
        }, indent=2))
        safe_claim = sanitize_claim(input_data["original_claim"])

        return f"""Audit this complete analysis of the claim: "<claim>{safe_claim}</claim>"

<analysis>
{all_outputs}
</analysis>

Check for:
1. **Bias**: Are sources one-sided? Is the framing balanced? Does the analysis favor one perspective?
2. **Accuracy**: Are claims supported by evidence? Are source tiers appropriate?
3. **Completeness**: Are important perspectives missing? Are there blind spots?
4. **Manipulation**: Could this analysis itself be used to manipulate? Does the Bridge Builder manufacture false common ground?
5. **Quality**: Is the reasoning sound? Are causal claims justified?

VETO is a RARE NUCLEAR OPTION. You should almost never use it.

For MOST issues, use verdict=pass_with_warnings with detailed findings. This lets
the reader see the analysis AND your critique together. Only veto when the analysis
is so broken that showing it would actively mislead the reader even with your
warnings attached.

VETO CRITERIA -- ALL THREE must be true simultaneously:
1. The flaw makes the ENTIRE analysis misleading (not just one section)
2. The issue cannot be adequately addressed by noting it in findings
3. A reader seeing the analysis WITH your findings would still be deceived

EXAMPLES OF WHAT TO VETO:
- Every agent's output contradicts the others (total incoherence)
- The analysis actively promotes the disinformation it should analyze
- All sources are fabricated (not just some dates being wrong)

EXAMPLES OF WHAT IS **NOT** A VETO (use pass_with_warnings + findings):
- Some dates, timelines, or attributions are inaccurate -> severity=high finding
- Bridge Builder common ground seems forced or naive -> category=manipulation finding
- Missing an important actor or perspective -> category=completeness finding
- One agent hallucinated details -> severity=high finding
- The original claim is false or debunked -> NOT relevant (false claims are valid analysis targets)
- Individual factual errors in origin tracing -> severity=high finding
- Bridge section equates unequal positions -> category=manipulation finding

IMPORTANT: This pipeline ANALYZES narrative networks around claims. False,
debunked, and conspiratorial claims are VALID analysis targets. The analysis
examines HOW narratives spread and WHO amplifies them -- it does not endorse
the claim. Do NOT veto because the claim being analyzed is wrong.

Respond in JSON. IMPORTANT: Each enum field must be EXACTLY ONE value, not combined.

{{
  "verdict": "CHOOSE ONE: pass, pass_with_warnings, fail",
  "findings": [
    {{
      "category": "CHOOSE ONE: bias, accuracy, completeness, manipulation, quality",
      "severity": "CHOOSE ONE: low, medium, high, critical",
      "description": "What is wrong",
      "recommendation": "How to fix it"
    }}
  ],
  "confidence_adjustment": -1.0 to 1.0,
  "veto": true or false,
  "summary": "Overall assessment in one sentence"
}}

DECISION GUIDE:
- No issues found -> verdict=pass, findings=[], veto=false
- Minor issues -> verdict=pass_with_warnings, list findings, veto=false
- Serious issues -> verdict=fail, list findings, veto=false (reader sees analysis + your critique)
- Catastrophic (meets ALL THREE veto criteria) -> verdict=fail, veto=true"""

    def parse_output(self, raw: dict) -> dict:
        return AuditorOutput(**raw).model_dump()
