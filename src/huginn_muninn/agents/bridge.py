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

Produce a four-layer Common Humanity analysis:

Layer 1 - Universal Human Needs: What fundamental need is at stake (safety, belonging, fairness, dignity, autonomy)?
Layer 2 - Issue-Specific Overlap: Where do opposing positions concretely agree? Cite evidence (polling, policy, stated positions).
Layer 3 - Narrative Deconstruction: How was the same underlying concern split into opposing narratives? Who performed the split and why?
Layer 4 - Inferential Gap Map: Where does the claim contain a kernel of truth, and what is the EXACT inferential leap from that truth to the conspiracy framing? Be specific: "X is documented fact; the leap to Y is unsupported because Z." If the claim is entirely false, state that clearly. If parts are true, map the precise boundary.

Also produce:

A) The scientific consensus / mainstream explanation: Present the established scientific or institutional explanation for the phenomena the claim addresses, with EQUAL depth and specificity as the conspiracy analysis. This is the "other side" -- what people who do NOT believe the claim understand to be true and WHY. Include:
- The physical, biological, or institutional mechanisms that explain what is observed
- Key studies, data points, or expert assessments with citations where possible
- Why this explanation accounts for the evidence better than the conspiracy version
- Common misconceptions that the conspiracy exploits and their corrections
This section must be substantive enough that a reader unfamiliar with the topic comes away understanding BOTH the conspiracy narrative AND the scientific explanation in equal depth.

B) A feasibility assessment: If the claim implies a physical, logistical, or organizational requirement (e.g., secret mass programs, technology that doesn't exist, coordination among thousands), briefly assess whether this is plausible and why or why not. Use quantitative reasoning where possible.

C) A commercial motive analysis: Who profits financially from people believing this claim? Name specific organizations, products, or revenue streams where known.

D) A 3-round Socratic dialogue script following the Costello protocol:
- Round 1: Perspective-getting (summarize their view, acknowledge the kernel of truth)
- Round 2: Personalized counter-evidence as question (address THEIR specific evidence). IMPORTANT: NAME THE MANIPULATION TECHNIQUE explicitly, like revealing a magic trick. Say "There's a pattern here called [technique name] -- it works by [simple mechanic]." Reference where the same pattern appeared before in other contexts (e.g., the same scapegoating technique used by the tobacco industry, or the same false dichotomy used in prior political campaigns). Frame around systemic patterns, not individual bad actors. Ask about patterns the person can verify themselves.
- Round 3: Complexity + common ground (add dimensions, present shared data, close with reflection question that redirects toward actionable shared goals)

E) Technique Reveal ("Name the Trick"): For each manipulation technique identified by the upstream TTP Classifier AND any additional framing techniques you detect, name it in plain language like revealing how a magic trick works. Once someone sees the palm, they see it everywhere. For each technique provide:
- technique: Human-readable name (e.g., "Cherry Picking", "Emotional Amplification", "Scapegoating")
- how_it_works: Simple explanation of the mechanic, as if showing someone how a magic trick is done
- used_by: Who is deploying this technique in THIS claim or context
- where_used_here: The specific evidence of this technique in this claim
- historical_precedent: Where was this same trick used before (e.g., tobacco industry, political campaigns)
- pattern_type: "isolated" (one-off framing choice), "repeated" (this actor has used it before), or "systematic" (documented multi-campaign, multi-year strategy)

CRITICAL -- Asymmetric Weight Principle (Pattern Gravity):
Do NOT treat all technique uses as equivalent. A private citizen using emotional amplification in a frustrated observation is categorically different from a political leader deploying scapegoating as a documented, multi-campaign strategy to gain power. Factors that increase weight:
- Pattern scope: multi-campaign > single instance
- Power asymmetry: political leader with media access > private citizen
- Documented intent: strategic deployment > imprecise framing
- Consequences: policy outcomes affecting millions > dinner table argument
Name the tricks on ALL sides (honesty builds credibility), but weight the analysis proportionally. A systematic playbook deserves detailed analysis. An isolated framing choice deserves a brief note. Treating them equally IS itself a false equivalence.

Respond in JSON:
{{
  "universal_needs": ["need1", "need2"],
  "issue_overlap": "Concrete agreement between opposing positions, with evidence",
  "narrative_deconstruction": "How the same concern was split into opposing narratives",
  "consensus_explanation": "The scientific/mainstream explanation for what is observed, with equal depth to the conspiracy analysis. Mechanisms, evidence, key studies, and why this explanation better accounts for the data.",
  "inferential_gap": "Where the kernel of truth ends and the unsupported leap begins, with specific boundary",
  "feasibility_check": "Brief quantitative/logical assessment of whether the claim's implied mechanism is physically or organizationally plausible",
  "commercial_motives": "Who profits from belief in this claim, with specific names/products/revenue where known",
  "techniques_revealed": [
    {{
      "technique": "Human-readable technique name",
      "how_it_works": "Simple explanation of the mechanic",
      "used_by": "Who uses this technique in this claim or context",
      "where_used_here": "Specific evidence of this technique here",
      "historical_precedent": "Where the same trick was used before",
      "pattern_type": "isolated | repeated | systematic"
    }}
  ],
  "perception_gap": "Where groups overestimate opponent extremism, with data if available",
  "moral_foundations": {{"side_a": ["foundation1"], "side_b": ["foundation2"]}},
  "reframe": "The claim reframed in terms of shared values",
  "socratic_dialogue": [
    "Round 1: Perspective-getting...",
    "Round 2: Counter-evidence as question (NAME the technique like revealing a magic trick)...",
    "Round 3: Complexity + common ground..."
  ]
}}

Critical constraints:
- NEVER more than 3 dialogue rounds
- NEVER use controlling language ('the truth is...', 'experts agree...', 'studies show...')
- NEVER confront identity ('you were misled', 'you fell for...', 'conspiracy theorists...')
- ALWAYS close dialogue with a question that points toward actionable shared goals
- ALWAYS ground claims in evidence where possible
- ALWAYS name at least one manipulation technique explicitly in the techniques_revealed array
- In Round 2, NAME the technique and explain the mechanic before asking the question
- If no genuine common ground exists, say so honestly rather than forcing synthesis
- If the claim is partially true, explicitly acknowledge what is true before addressing what is not
- When multiple sides use techniques, give proportional weight based on pattern gravity"""

    def parse_output(self, raw: dict) -> dict:
        # LLMs sometimes exceed the 3-round limit despite prompt constraints
        if "socratic_dialogue" in raw and len(raw["socratic_dialogue"]) > 3:
            raw["socratic_dialogue"] = raw["socratic_dialogue"][:3]
        return BridgeOutput(**raw).model_dump()
