"""Claude Code native scenario runner.

Runs the full 6-agent pipeline within Claude Code's own context,
using Opus as the LLM backend via subagent calls. No external API key needed.

Usage (from Claude Code):
    1. Read this file
    2. Call run_scenario_pipeline(claim) from within the session
    3. Results are written to tests/results/

This script is designed to be executed step-by-step by the main Claude Code agent,
NOT as a standalone Python process. Each agent step produces a JSON prompt that
the main agent feeds to a subagent, collects the response, and passes to the next step.
"""
from __future__ import annotations

import json
from pathlib import Path

# Import the prompt builders from the actual agents
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from huginn_muninn.prompt import sanitize_claim, sanitize_for_prompt
from huginn_muninn.sources import load_disarm_techniques


def build_agent_prompts(claim: str) -> dict:
    """Build all 6 agent prompts for a claim.

    Returns a dict with keys: decomposer, tracer, mapper, classifier, bridge, auditor.
    Each value is a dict with 'system' and 'user' prompt strings.

    The main Claude Code agent should:
    1. Send decomposer prompt to a subagent, collect JSON response
    2. Feed decomposer output into tracer prompt, send, collect
    3. Continue through the pipeline
    4. Write final result to disk
    """
    safe_claim = sanitize_claim(claim)

    prompts = {}

    # Stage 1: Decomposer (needs only the claim)
    prompts["decomposer"] = {
        "system": (
            "You are a claim decomposition specialist. Your job is to break "
            "complex claims into individual, verifiable sub-claims. Classify "
            "each sub-claim by type: factual (can be checked against data), "
            "opinion (subjective judgment), prediction (about the future), "
            "value (moral/ethical stance), or causal (X causes Y)."
        ),
        "user": f"""Decompose the following claim into its component sub-claims.

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
- "simple" = single factual claim, "moderate" = 2-3 sub-claims, "complex" = 4+ or nested logic, "multi_actor" = involves multiple groups/entities""",
    }

    # Stages 2-6 are template functions that take upstream data
    prompts["_templates"] = {
        "tracer": _tracer_template,
        "mapper": _mapper_template,
        "classifier": _classifier_template,
        "bridge": _bridge_template,
        "auditor": _auditor_template,
    }

    return prompts


def _tracer_template(claim: str, decomposition: dict) -> dict:
    safe_claim = sanitize_claim(claim)
    sub_claims_json = sanitize_for_prompt(json.dumps(decomposition.get("sub_claims", []), indent=2))
    return {
        "system": (
            "You are an origin tracer for information analysis. Your job is "
            "to identify where claims first appeared, how they propagated, "
            "and how the narrative mutated as it spread. Track the chain from "
            "original source to current form."
        ),
        "user": f"""Trace the origins and propagation of these sub-claims from the claim: "<claim>{safe_claim}</claim>"

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

Source tiers: 1=scientific/governmental, 2=established journalism, 3=regional/specialized, 4=social media/unknown""",
    }


def _mapper_template(claim: str, decomposition: dict, origins: dict) -> dict:
    safe_claim = sanitize_claim(claim)
    sub_claims_json = sanitize_for_prompt(json.dumps(decomposition.get("sub_claims", []), indent=2))
    origins_json = sanitize_for_prompt(json.dumps(origins, indent=2))
    return {
        "system": (
            "You are an intelligence analyst specializing in information networks. "
            "Your job is to identify the key actors involved in spreading a narrative, "
            "their motivations, their relationships, and how they form a network. "
            "Be specific about evidence. Do not speculate without flagging uncertainty."
        ),
        "user": f"""Analyze the actor network behind this claim: "<claim>{safe_claim}</claim>"

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
- Include both supporters AND opponents of the narrative""",
    }


def _classifier_template(claim: str, decomposition: dict, origins: dict, intelligence: dict) -> dict:
    techniques = load_disarm_techniques()
    tech_ref = "\n".join(
        f"- {t['id']}: {t['name']} ({t['tactic']}) -- {t['description']}"
        for t in techniques
    )
    upstream = sanitize_for_prompt(json.dumps({
        "sub_claims": decomposition.get("sub_claims", []),
        "origins": origins,
        "intelligence": intelligence,
    }, indent=2))
    safe_claim = sanitize_claim(claim)

    return {
        "system": (
            "You are a disinformation tactics, techniques, and procedures (TTP) "
            "classifier. You map observed information manipulation behaviors to "
            "the DISARM framework (the MITRE ATT&CK equivalent for disinformation). "
            "Only classify TTPs you have evidence for."
        ),
        "user": f"""Classify the disinformation techniques used in this claim: "<claim>{safe_claim}</claim>"

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
- Confidence reflects strength of evidence, not severity""",
    }


def _bridge_template(claim: str, decomposition: dict, origins: dict, intelligence: dict, ttps: dict) -> dict:
    upstream = sanitize_for_prompt(json.dumps({
        "sub_claims": decomposition.get("sub_claims", []),
        "origins": origins,
        "intelligence": intelligence,
        "ttps": ttps,
    }, indent=2))
    safe_claim = sanitize_claim(claim)

    return {
        "system": (
            "You are a Bridge Builder -- a Common Humanity analyst. Your job is "
            "to find the shared human values beneath divisive narratives, show HOW "
            "people are being manipulated, and find common ground between polarized "
            "positions. You speak with warmth, curiosity, and directness. You never "
            "use controlling language ('the truth is...', 'experts agree...') and "
            "never confront identity ('you were misled', 'you fell for...'). "
            "Your goal is to unite, not divide, while maintaining factual rigor."
        ),
        "user": f"""Analyze the common humanity beneath this claim: "<claim>{safe_claim}</claim>"

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
- If no genuine common ground exists, say so honestly rather than forcing synthesis""",
    }


def _auditor_template(claim: str, decomposition: dict, origins: dict, intelligence: dict, ttps: dict, bridge: dict) -> dict:
    all_outputs = sanitize_for_prompt(json.dumps({
        "decomposition": decomposition,
        "origins": origins,
        "intelligence": intelligence,
        "ttps": ttps,
        "bridge": bridge,
    }, indent=2))
    safe_claim = sanitize_claim(claim)

    return {
        "system": (
            "You are an Adversarial Auditor for disinformation analysis. Your job "
            "is to find flaws, biases, and errors in the analysis produced by other "
            "agents. You are a constructive quality gate: document issues as findings "
            "with severity ratings so they can be fixed. You rarely veto -- almost "
            "all issues should be reported as findings with verdict=pass_with_warnings. "
            "Be rigorous but proportionate."
        ),
        "user": f"""Audit this complete analysis of the claim: "<claim>{safe_claim}</claim>"

<analysis>
{all_outputs}
</analysis>

Check for:
1. **Bias**: Are sources one-sided? Is the framing balanced?
2. **Accuracy**: Are claims supported by evidence? Are source tiers appropriate?
3. **Completeness**: Are important perspectives missing?
4. **Manipulation**: Could this analysis itself be used to manipulate?
5. **Quality**: Is the reasoning sound?

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
  "veto": false,
  "summary": "Overall assessment in one sentence"
}}""",
    }


# Pipeline execution order for the main agent to follow
PIPELINE_STEPS = """
## Claude Code Native Pipeline Execution

For each scenario, the main agent should execute these steps:

### Step 1: Decomposer
- Send prompts["decomposer"]["system"] + prompts["decomposer"]["user"] to a subagent
- Parse the JSON response as `decomposition`

### Step 2: Tracer
- Call `_tracer_template(claim, decomposition)` to get the prompt
- Send to a subagent, parse as `origins`

### Step 3: Mapper
- Call `_mapper_template(claim, decomposition, origins)` to get the prompt
- Send to a subagent, parse as `intelligence`

### Step 4: Classifier
- Call `_classifier_template(claim, decomposition, origins, intelligence)` to get the prompt
- Send to a subagent, parse as `ttps`

### Step 5: Bridge Builder
- Call `_bridge_template(claim, decomposition, origins, intelligence, ttps)` to get the prompt
- Send to a subagent, parse as `bridge`

### Step 6: Auditor
- Call `_auditor_template(claim, decomposition, origins, intelligence, ttps, bridge)` to get the prompt
- Send to a subagent, parse as `audit`

### Step 7: Evaluate
- Import evaluate_bridge_output from tests.scenarios
- Run evaluation against scenario expectations
- Write results to tests/results/{scenario_id}.json
"""
