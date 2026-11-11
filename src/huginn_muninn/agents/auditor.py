"""Adversarial Auditor -- quality gate with veto power."""
from __future__ import annotations

import json

from huginn_muninn.agents.base import AgentError, BaseAgent
from huginn_muninn.contracts import AuditorOutput
from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt


class AuditorAgent(BaseAgent):
    name = "adversarial_auditor"
    output_model = AuditorOutput

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
        # Serialize gorgon_signals when the orchestrator provides it so the
        # deterministic hypothesis-expansion helper actually reaches the LLM.
        # Without this, the signal would be dead code from the Auditor's view.
        analysis_payload: dict[str, object] = {
            "decomposition": input_data.get("decomposition", {}),
            "origins": input_data.get("origins", {}),
            "intelligence": input_data.get("intelligence", {}),
            "ttps": input_data.get("ttps", {}),
            "bridge": input_data.get("bridge", {}),
        }
        gorgon_signals = input_data.get("gorgon_signals")
        if gorgon_signals:
            analysis_payload["gorgon_signals"] = gorgon_signals
        all_outputs = sanitize_for_prompt(json.dumps(analysis_payload, indent=2))
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

COGNITIVE WARFARE AND FRAME CAPTURE AUDIT:

Use category="cognitive_warfare" for findings related to GT-series cognitive warfare
signatures (White Noise, Black Noise, Pattern Injection). Use category="frame_capture"
for findings where the pipeline adopted the input claim's framing without independent
restatement. These are first-class audit categories alongside the original five.

**Frame capture** is when the analysis ADOPTS the claim's framing, labels, or implied
causality without independently restating the question. This is DISTINCT from
fact-checking, which remains central to your job. Frame capture is NOT a reason to
suppress verification of concrete factual claims. A claim can be rigorously
fact-checked AND have frame capture issues simultaneously.

**Trigger gate**: Explicitly assess frame_capture_risk only when upstream signals
indicate possible cognitive warfare: hypothesis_crowding="high" in the Decomposer
output, OR notable_omissions is non-empty in the Tracer output, OR the Classifier
matched any TTP with id starting "GT-". Otherwise default frame_capture_risk to
"none".

**Evidence requirement**: When flagging frame_capture_risk as "possible" or "high",
cite the SPECIFIC frame element in frame_capture_evidence: a label, a causal link,
a categorization, or a framing device that was imported from the input claim and
used by upstream agents without independent restatement. Do NOT flag on
pattern-recognition alone -- every flag must name a specific imported element.

**Rarity signal**: These are advanced audit categories. In most ordinary runs,
frame_capture_risk will be "none". Flag sparingly and only with explicit upstream
signals.

EVIDENCE CERTAINTY FRAMEWORK (ECF):
Rate the claim as stated, not this analysis and not the topic in general,
on five dimensions (0.0-1.0; 0.0 / 0.5 / 1.0 anchors, use values between for
in-between cases):
- evidence_quality: how strong is the evidence that SUPPORTS the claim?
  0.0 none, or anecdotes only; 0.5 some real evidence, mixed or indirect;
  1.0 strong direct evidence (controlled studies, official records).
- source_reliability: how reliable are the sources that make or carry the claim
  (its origins and proponents, never the sources that refute it)?
  0.0 anonymous posts, known fabricators; 0.5 partisan or commentary outlets,
  mixed record; 1.0 peer review, official statistics, corrections policies.
- claim_testability: can the claim be checked against observable data?
  0.0 unfalsifiable by design (secret plots, hidden intent); 0.5 partly
  checkable, key parts are not; 1.0 fully checkable against data.
- expert_consensus: how far do domain experts SUPPORT the claim?
  0.0 Experts reject it almost unanimously; 0.5 real expert debate;
  1.0 experts broadly agree with it.
- internal_coherence: do the claim's parts fit together logically?
  0.0 self-contradictory, or the parts do not connect; 0.5 loose links,
  some leaps; 1.0 parts support each other without leaps.

Strong evidence AGAINST the claim (for example a well-documented debunk)
lowers evidence_quality and expert_consensus and never raises any of the five
scores. These scores describe the claim's support, not the quality of this
analysis.

Anchor to upstream signals: use the Tracer source_tier distribution of the
claim's origins as a prior for source_reliability. Use the Decomposer
sub-claim verifiable count for claim_testability. If you cannot judge a
dimension at all, use 0.5 and say why in a finding. Do not invent precision.

LOCATING FINDINGS:
For each finding, list in "locations" up to three passages it is about, so a
reader sees the finding next to the text. "section" names the part of the
analysis the passage is in: decomposition, origins, intelligence, ttps or
bridge. "quote" is 5 to 25 consecutive words copied exactly from that
section's text, character for character, with no paraphrase, ellipsis or
added words. If a finding is about something missing, quote the passage
where it should have appeared, or leave "locations" empty.

VETO is a RARE NUCLEAR OPTION. You should almost never use it.

For MOST issues, use verdict=pass_with_warnings with detailed findings. This lets
the reader see the analysis AND your critique together. Only veto when the analysis
is so broken that showing it would actively mislead the reader even with your
warnings attached. A veto is enforced, not merely recorded: the Bridge layer
(common ground, dialogue, reframe) is withheld from the reader and replaced by
your summary, while the evidence layer ships with your findings attached.

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
      "category": "CHOOSE ONE: bias, accuracy, completeness, manipulation, quality, cognitive_warfare, frame_capture",
      "severity": "CHOOSE ONE: low, medium, high, critical",
      "description": "What is wrong",
      "recommendation": "How to fix it",
      "locations": [
        {{"section": "CHOOSE ONE: decomposition, origins, intelligence, ttps, bridge", "quote": "Words copied exactly from that section"}}
      ]
    }}
  ],
  "confidence_adjustment": -1.0 to 1.0,
  "veto": true or false,
  "summary": "Overall assessment in one sentence",
  "frame_capture_risk": "CHOOSE ONE: none, possible, high (default: none)",
  "frame_capture_evidence": "Specific imported frame element, or empty string if none",
  "confidence_profile": {{
    "evidence_quality": 0.0-1.0,
    "source_reliability": 0.0-1.0,
    "claim_testability": 0.0-1.0,
    "expert_consensus": 0.0-1.0,
    "internal_coherence": 0.0-1.0
  }}
}}

DECISION GUIDE:
- No issues found -> verdict=pass, findings=[], veto=false
- Minor issues -> verdict=pass_with_warnings, list findings, veto=false
- Serious issues -> verdict=fail, list findings, veto=false (reader sees analysis + your critique)
- Catastrophic (meets ALL THREE veto criteria) -> verdict=fail, veto=true"""

    def parse_output(self, raw: dict) -> dict:
        # "unaudited" is reserved for the orchestrator's no-Auditor path. A
        # model that emits it did not produce an audit, so it is treated like
        # any other malformed reply and the orchestrator labels the run
        # unaudited and degraded (review finding, 2026-09-03).
        verdict = raw.get("verdict")
        if isinstance(verdict, str) and verdict.strip().lower().startswith("unaudited"):
            raise AgentError("Auditor emitted the reserved verdict 'unaudited'")
        return AuditorOutput(**raw).model_dump()
