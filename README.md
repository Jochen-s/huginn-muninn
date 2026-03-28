# Huginn & Muninn

**The fact-checker that finds common ground**

Huginn & Muninn is an open-source AI framework for disinformation analysis that goes beyond
verdict delivery. Named after Odin's two ravens (Thought and Memory), it is built on a simple
premise: telling people they are wrong does not work. What works is helping them see how they
are being manipulated, and what they share with the people they have been taught to fear.

This is not an oracle. It is a cognitive gymnasium. The goal is to teach you a mental framework
you carry forever, then make the tool unnecessary.

---

## The Three Questions

Every analysis answers three questions. These are designed as a transferable mental model
that users internalize and apply independently, even without the tool.

1. **What is true?**
   Deconstruct claims. Trace actors and their objectives. Map the evidence landscape.
   Not declaring truth from authority, but laying out evidence so you can reason for yourself.

2. **Who benefits from me feeling this way?**
   The manipulation literacy question. Who profits from your anger, fear, or distrust?
   What tactics are being used? Once you learn to ask this reflexively, you become resistant
   to manipulation across every domain. You do not need a tool for this. You need the habit.

3. **What do we share?**
   The healing question. Not "we're all human" in the abstract, but concrete shared
   circumstances: "You and the people you disagree with both worry about providing for your
   families. Polling shows 73% agreement on the underlying concern. The disagreement was
   manufactured."

These three questions work as a system. The first grounds you in evidence. The second builds
manipulation literacy. The third reconnects you to the people you have been taught to fear.
Each corrects the weaknesses of the others: truth-checking alone creates dependency on
verdicts, manipulation literacy alone creates cynicism, common humanity alone risks false
equivalence. Together, they build lasting discernment.

---

## Architecture

Two analysis methods, one pipeline:

```
METHOD 1: Quick Check (~10 seconds)
--------------------------------------
Claim
  |
  v
Two-Pass Verification
  |
  v
Verdict + Confidence + Evidence + Common Ground


METHOD 2: Full Analysis (30-90 seconds)
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
   layer                for bias and errors
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

## Quick Start: CLI

**Requirements:** Python 3.12+, [Ollama](https://ollama.ai) running locally

```bash
# Install from source
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

## Quick Start: API

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

## Quick Start: Docker

```bash
cp .env.example .env   # Edit OLLAMA_BASE_URL
docker compose up -d   # Web UI at http://localhost:8000
```

---

## The Common Humanity Layer

The Bridge Builder agent is what separates Huginn & Muninn from a conventional fact-checker.
Rather than issuing a verdict and stopping, it identifies the universal human need underneath
the disputed claim (safety, belonging, fairness, autonomy), then surfaces the concrete overlap
between opposing positions using primary evidence. It deconstructs how the same underlying
concern was split into irreconcilable-seeming narratives, and generates a three-round Socratic
dialogue based on Costello, Pennycook & Rand (Science, 2024).

The output is not a corrected belief. It is a cleared path toward one.

The design follows cognitive apprenticeship principles (Collins, Brown & Newman, 1989):
the tool models the reasoning process, coaches users through application, then progressively
withdraws support until users apply the three questions independently. The goal is
internalization, not dependency.

---

## Designed Against Dependency

A 2025 follow-up study (Bao et al., arXiv:2510.01537) found that AI dialogue can reduce
conspiracy beliefs by 21% while simultaneously degrading independent discernment by 15%
over four weeks. This dependency paradox is a real risk for any AI fact-checking tool.

Huginn & Muninn addresses this through four architectural pillars:

1. **Genuine Socratic method**: The system asks questions that guide reasoning rather than
   delivering verdicts. Bao et al.'s own data shows "guiding and probing questions" correlate
   positively with independent detection skills (r=0.29), while directive correction undermines them.

2. **Mandatory fading**: AI support progressively withdraws as user competence grows,
   following Vygotsky's Zone of Proximal Development. Without explicit fading, the ZPD collapses
   into a "Zone of No Development" (arXiv:2511.12822).

3. **Desirable difficulties**: Spacing, interleaving, retrieval practice, and generation effects
   (Bjork, 1994) slow short-term performance but improve long-term retention by up to 80%.
   Users must attempt their own analysis before seeing the AI's.

4. **System-regulated access**: Research from Wharton shows system-regulated AI access
   produces 64% learning gains versus 30% for unrestricted on-demand access. Users cannot be
   trusted to self-limit AI reliance; the system enforces structure.

The graduation model: Huginn & Muninn is designed to make itself unnecessary. The three
questions are yours to keep.

---

## Manufactured Doubt Detection

Huginn & Muninn identifies manufactured doubt using a 28-tactic taxonomy derived from
Goldberg et al. (2021, Environmental Health, PMC7996119), which documented strategies used
across the tobacco, fossil fuel, sugar, pesticide, and climate denial industries.

Five tactics appeared universally across all five industries:

| # | Tactic | Description |
|---|--------|-------------|
| 1 | Attack Study Design | Exaggerate minor methodological flaws to discredit research |
| 2 | Gain Reputable Support | Recruit credible figures to defend industry positions |
| 3 | Misrepresent Data | Cherry-pick findings, design studies intended to fail |
| 4 | Hyperbolic Language | Loaded buzzwords ("junk science"), absolutist framing |
| 5 | Influence Government | Regulatory capture, revolving door, pro-industry legislation |

The system distinguishes manufactured doubt from genuine scientific uncertainty through
structural signatures: manufactured doubt always concludes toward inaction, shows asymmetric
scrutiny of evidence, and traces back to concentrated funding sources. Genuine uncertainty is
specific, bounded, and proposes research to resolve itself.

---

## Research Foundation

Huginn & Muninn is grounded in peer-reviewed research. Two comprehensive research waves
(~240 sources) inform the design. The project maintains an honest assessment of each
research pillar's strength.

| Domain | Key Research | Status | How H&M Uses It |
|--------|-------------|--------|-----------------|
| Socratic AI Dialogue | Costello et al. (Science, 2024): 20% durable reduction in conspiracy beliefs. AAAS Newcomb Cleveland Prize 2026. | STRONG (with dependency caveat, addressed by design) | Bridge Builder dialogue protocol with mandatory fading |
| Inoculation / Prebunking | van der Linden & Roozenbeek (Cambridge); Google/Jigsaw (5.4M users, 5-10% improvement). Meta-analysis 2025 (N=37,075) confirms. | MODERATE-STRONG (lab-to-field gap) | Technique labeling in every output |
| Perception Gap | More in Common (2019): 2x overestimation of opponent extremism | WEAK (US-only, single study) | Surfaces what the other side actually thinks. Used cautiously. |
| Manufactured Doubt | Goldberg et al. (2021): 28 tactics across 5 industries | STRONG (well-documented, cross-industry) | 28-tactic detection layer with epistemic asymmetry rules |
| Narrative Complexity | Peter Coleman (Columbia): adding dimensions collapses false dichotomies | MODERATE (compelling theory, limited RCTs) | Three-layer narrative deconstruction |
| Cognitive Apprenticeship | Collins, Brown & Newman (1989): 6-stage framework transfer model | STRONG (decades of replication) | Progressive scaffolding with mandatory fading |

**Downgraded pillars** (transparency matters more than appearance):

- **Moral Reframing** (Feinberg & Willer, 2015-2019): Originally a core pillar, now experimental
  only. Six or more preregistered replication attempts have failed, including a 2026 study with
  2,009 participants. The technique may work under specific conditions but not as a general tool.

- **Redirect Method** (Moonshot): The 224% figure measures engagement (watch time), not
  belief or behavior change. Useful as a complementary signal, not a primary mechanism.

Full research corpus available in the `research/` directory.

---

## What Does Not Work

Design decisions informed by explicitly ruling out documented anti-patterns:

| Anti-pattern | Why It Fails | How H&M Avoids It |
|-------------|-------------|-------------------|
| Controlling language ("the truth is...") | Triggers psychological reactance | Autonomy-supportive framing throughout |
| Identity confrontation | Attacking beliefs is experienced as attacking the person | Never labels users as misled or manipulated |
| Generic counter-narratives | Personalized content vastly outperforms generic responses | References the user's specific claim and evidence |
| Forced engagement | Unsolicited corrections trigger doubling-down effects | Dialogue is always opt-in |
| Directive AI correction | Creates dependency; -15.3% discernment decline (Bao et al. 2025) | Genuine Socratic questioning with progressive fading |
| False equivalence | "Both sides" framing can legitimize extremism | Epistemic asymmetry detection overrides bridge-building when scientific consensus is clear |

---

## The Ego Development Connection

Research on psychosocial maturity (Loevinger's ego development model, stages E2-E9)
suggests that susceptibility to conspiracy theories and authoritarian attitudes peaks at specific
developmental stages, independent of intelligence or education. Stage E4 (Conformist) shows
the highest overlap with Adorno's authoritarian character: outgroup rejection, authority
orientation, binary thinking.

Huginn & Muninn calibrates its Socratic dialogue to developmental capacity:
- **E3-E4** (Conformist): Authority-aligned framing, concrete language, social proof
- **E5** (Self-Aware): Guided perspective-taking and comparison
- **E6** (Conscientious): Classical Socratic questioning with evidence evaluation
- **E7+** (Individualistic/Autonomous): Systems thinking, meta-cognitive reflection

This calibration is informed by Bronlet (2025, Frontiers in Psychology), who demonstrated
LLM-based automated scoring of the Washington University Sentence Completion Test (WUSCT)
at kappa = 0.779, approaching the 0.80 threshold for reliable measurement.

---

## Privacy

Your data never leaves your machine. Huginn & Muninn runs entirely on local hardware using
open-source language models through Ollama. No cloud dependency, no API keys required for
base usage, no data collection. If you are analyzing sensitive political claims, you should not
have to trust a third party with that data.

For multi-model support beyond local Ollama, the API supports OpenAI-compatible providers
(including OpenRouter for access to 300+ models).

---

## Contributing

Contributions welcome. Please open an issue first to discuss what you would like to change.

Areas where contributions are particularly valuable:
- Cross-cultural validation of the three-question framework
- Multilingual support (the Socratic dialogue principles are culturally specific)
- Manufactured doubt detection for non-Western contexts
- Integration with PKM tools (Obsidian plugin, browser extension)

---

## License

MIT. See [LICENSE](LICENSE).

---

## Citation

If you reference this work in an academic context, please cite the underlying research
papers directly:

> Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs
> through dialogues with AI. *Science*, 385(6714).

> Goldberg, R. F., Vandenberg, L. N., et al. (2021). The science of spin: targeted strategies
> to manufacture doubt with detrimental effects on environmental and public health.
> *Environmental Health*, 20, 33.

> Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the
> crafts of reading, writing, and mathematics. In L. B. Resnick (Ed.), *Knowing, Learning,
> and Instruction*.

---

## Anti-Weaponization Charter

Huginn & Muninn includes an [Anti-Weaponization Charter](ANTI-WEAPONIZATION-CHARTER.md)
that defines what the system will not do: it cannot manufacture false common ground, cannot
be used as a persuasion engine for any agenda, and acknowledges when moral positions are
genuinely irreconcilable rather than forcing false synthesis.

"Not every disagreement is manufactured. Some are real. But the ones that are manufactured
deserve to be seen."
