# Huginn & Muninn

**The fact-checker that finds common ground**

Huginn & Muninn is an open-source AI framework for disinformation analysis that goes beyond
verdict delivery. Grounded in peer-reviewed research, it answers not just what is false, but
how the manipulation works and what the people on both sides of an issue actually share.
The goal is durable attitude change, not argument-winning.

---

## The Three Questions

Every analysis answers three questions:

1. **What is true?** — Fact-check with cited evidence and confidence score
2. **How are you being played?** — Specific manipulation mechanics, labeled by technique
3. **What do we actually share?** — Common ground, universal needs, and perception gap data

---

## Architecture

Two analysis methods, one pipeline:

```
METHOD 1 — Quick Check (~10 seconds)
--------------------------------------
Claim
  |
  v
Two-Pass Verification
  |
  v
Verdict + Confidence + Evidence + Common Ground


METHOD 2 — Full Analysis (30-90 seconds)
------------------------------------------
Claim
  |
  v
[1] Claim Decomposer
       Breaks input into verifiable sub-claims
  |
  v
[2] Origin Tracer
       Tracks claim origins and spread patterns
  |
  v
[3] Network Mapper
       Maps information flow and actor relationships
  |
  v
[4] TTP Classifier
       Labels manipulation techniques (DISARM framework)
  |
  +-------------------+
  v                   v
[5] Bridge Builder  [6] Adversarial Auditor
   Common humanity      Red-teams the analysis
   layer
  +-------------------+
  |
  v
Orchestrator
  |
  v
Comprehensive Report
  (narrative deconstruction, perception gaps, Socratic dialogue)
```

---

## Quick Start — CLI

**Requirements:** Python 3.12+, [Ollama](https://ollama.ai) running locally

```bash
# Install
pip install huginn-muninn
# or from source
uv pip install -e .

# Pull a model
ollama pull qwen3.5:9b

# Method 1: Quick check (~10 seconds)
huginn check "claim text here"

# Method 2: Full 6-agent analysis (30-90 seconds)
huginn analyze "claim text here"

# Auto-choose method based on claim complexity
huginn analyze "claim text here" --auto-escalate
```

---

## Quick Start — API

```bash
# Start the server
uvicorn huginn_muninn.api:app --host 0.0.0.0 --port 8000

# Quick check
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"claim": "claim text here"}'

# Full 6-agent analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"claim": "claim text here"}'
```

---

## Quick Start — Docker

```bash
# Configure environment
cp .env.example .env
# Edit OLLAMA_BASE_URL to point to your Ollama instance

# Start
docker compose up -d
# Web UI available at http://localhost:8000
```

---

## The Common Humanity Layer

The Bridge Builder agent is what separates Huginn & Muninn from a conventional fact-checker.
Rather than issuing a verdict and stopping there, it identifies the universal human need
underneath the disputed claim — safety, belonging, fairness, autonomy — then surfaces the
concrete overlap between opposing positions using primary evidence. It deconstructs how the
same underlying concern was split into irreconcilable-seeming narratives, and generates a
three-round Socratic dialogue based on the methodology of Costello, Pennycook & Rand
(Science, 2024), which demonstrated a 20% durable reduction in conspiracy beliefs through
personalized AI conversation. The output is not a corrected belief — it is a cleared path
toward one.

---

## Research Foundation

| Domain | Key Research | How H&M Uses It |
|--------|-------------|-----------------|
| Socratic AI Dialogue | Costello, Pennycook & Rand (Science, 2024) — 20% durable reduction in conspiracy beliefs | Bridge Builder dialogue protocol |
| Inoculation / Prebunking | van der Linden & Roozenbeek (Cambridge); Google/Jigsaw (5.4M users, 5-10% improvement) | Technique labeling in every output |
| Perception Gap | More in Common (2019) — Americans overestimate opponent extremism by 2x | Surfaces what the other side actually thinks |
| Moral Reframing | Feinberg & Willer (Stanford/Toronto, 2015-2019) | Bridge Builder adapts framing to moral foundations |
| Narrative Complexity | Peter Coleman (Columbia) — adding dimensions collapses false dichotomies | Three-layer narrative deconstruction |
| Redirect Method | Moonshot (2017-present) — 224% increase in counter-narrative engagement | Guides attention toward constructive alternatives |

---

## What Does Not Work

Design decisions made by explicitly ruling out common counter-disinformation anti-patterns:

| Anti-pattern | Why It Fails | How H&M Avoids It |
|-------------|-------------|-------------------|
| Controlling language ("the truth is...") | Triggers psychological reactance | Autonomy-supportive framing throughout |
| Identity confrontation | Attacking beliefs is experienced as attacking the person | Never labels users as misled or manipulated |
| Generic counter-narratives | Personalized content vastly outperforms generic responses | References the user's specific claim and evidence |
| Forced engagement | Unsolicited corrections trigger doubling-down effects | Dialogue is always opt-in |

---

## Contributing

Contributions welcome. Please open an issue first to discuss what you would like to change.

---

## License

MIT — see [LICENSE](LICENSE)

---

## Citation

If you reference this work in an academic context, please cite the underlying research papers
directly, particularly Costello et al. (2024):

> Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs
> through dialogues with AI. *Science*, 385(6714).
