# Huginn & Muninn

**De-polarize. Find common ground. Then make the tool unnecessary.**

Odin had two ravens. Muninn (Memory) flew out each day and returned with information. Huginn (Thought) flew out and returned with understanding. Odin feared the loss of Huginn more than Muninn. You can always gather more information. The capacity to think about what it means is harder to replace.

The AI industry built an ecosystem around Muninn: retrieval, context windows, RAG pipelines, recommendation engines. Huginn, the layer that asks "what does this information mean for the humans it touches," barely exists.

This project is an attempt to build it.

Huginn & Muninn is an open-source, local-first AI framework for disinformation analysis. It goes beyond verdict delivery. Telling people they are wrong does not work. What works is helping them see how they are being manipulated, and what they share with the people they have been taught to fear.

This is a cognitive gymnasium. The goal is to teach you a mental framework you carry forever, then make the tool unnecessary.

---

## Why This Exists

It started in a community I care about. People dedicated to human flourishing. One evening, a discussion spiraled into exactly the dynamics I coach founders through: doubling down, zero common ground, manufactured outrage crowding out curiosity. I could name every pattern. What actually helped was simpler. Take a step back. Be curious instead of right.

That planted a question I couldn't let go of. If connecting on a human level is the answer, how do you help people do that when the information environment is designed to make connection harder?

So I spent a year with the research. Six peer-reviewed domains. 370+ sources. 20 test scenarios. Built a framework. Presented it at the PKM Summit in Utrecht. Someone asked: "How do you reach someone who believes in chemtrails without calling them stupid?"

I didn't have the worked answer. That bothered me enough to build one.

The chemtrails exercise is in the article. But the real answer is simpler than any pipeline: be interested in the person standing in front of you. Forget about being interesting. Ask what they're worried about. Ask who profits from the framing. Ask what you actually share underneath the disagreement.

You don't need an AI for that. You just need to see the human.

---

## The Three Questions

Every analysis answers three questions. These are designed as a transferable mental model you internalize and apply independently, even without the tool.

**1. What is true?**

Deconstruct claims. Trace actors and their objectives. Map the evidence. Not declaring truth from authority, but laying out evidence so you can reason for yourself.

**2. Who benefits from me feeling this way?**

The manipulation literacy question. Who profits from your anger, fear, or distrust? What tactics are being used? Once you learn to ask this reflexively, you become resistant to manipulation across every domain. You don't need a tool for this. You need the habit.

**3. What do we share?**

The healing question. Not "we're all human" in the abstract, but concrete shared circumstances: "You and the people you disagree with both worry about providing for your families. Polling shows 73% agreement on the underlying concern. The disagreement was manufactured."

These three questions work as a system. Truth-checking alone creates dependency on verdicts. Manipulation literacy alone creates cynicism. Common humanity alone risks false equivalence. Together, they build lasting discernment.

---

## Architecture

Two analysis methods, one pipeline.

**Method 1: Quick Check** (~10 seconds). Two-pass LLM verification. Verdict, confidence, evidence, common ground.

**Method 2: Full Analysis** (30-90 seconds). Six agents, each with a distinct mandate:

| Agent | What It Does |
|-------|-------------|
| **Claim Decomposer** | Breaks input into verifiable sub-claims. Flags hypothesis crowding (v0.7.0) and assigns verification priority (v0.8.0). |
| **Origin Tracer** | Tracks claim origins, spread patterns, and how narratives migrate between ideological camps over time. |
| **Network Mapper** | Maps information flow and actor relationships. |
| **TTP Classifier** | Labels manipulation techniques using the DISARM framework, including cognitive warfare techniques (v0.7.0). |
| **Bridge Builder** | The common humanity layer. Identifies universal needs, surfaces concrete overlap, deconstructs manufactured narratives, presents scientific consensus with equal depth (v0.4.0), and advises communication approach grounded in 27 peer-reviewed citations (v0.8.0). |
| **Adversarial Auditor** | Red-teams the entire analysis for bias, errors, and frame capture risk. First-class cognitive warfare and frame capture categories (v0.10.0). Exfiltration-guarded (v0.11.0). |

Everything flows through an orchestrator. Output passes through a regulated envelope (v0.9.0) that projects results through field suppression and scope scrubbing before reaching any external boundary.

---

## Cognitive Warfare Detection (v0.7.0)

Classical disinformation analysis asks: is this claim true? A newer class of attack doesn't depend on false claims at all. It floods the information space until audiences can't decide which interpretation the evidence supports. Every individual claim can be technically true. The confusion IS the weapon.

v0.7.0 detects three techniques from the Briggs, Danyk, and Weiss (2026) cognitive warfare taxonomy:

| Technique | How It Works |
|-----------|-------------|
| **White Noise (GT-001)** | High-volume, low-signal flooding that crowds the hypothesis space. |
| **Black Noise (GT-002)** | Ecosystem-level source suppression before primary narratives are seeded. |
| **Pattern Injection (GT-003)** | Synchronized narratives mimicking expert consensus through fabricated sourcing or credential laundering. |

---

## Bridge Builder: Scoped Diagnostics (v0.8.0)

The Bridge Builder went from "here is what is true" to "here is how to communicate this effectively to someone who currently believes otherwise." Every diagnostic field is grounded in peer-reviewed literature:

| Field | What It Does | Research Foundation |
|-------|-------------|-------------------|
| `communication_posture` | Advises direct correction, inoculation-first, or relational-first approach | McGuire 1964, van der Linden, Roozenbeek, Costello/Pennycook/Rand 2024 |
| `pattern_density_warning` | Flags claims whose structural features predispose over-connection | Alter & Oppenheimer 2009, Schwarz 1998 |
| `vacuum_filled_by` | Describes what filled an information vacuum (pattern-only, no named publishers) | Golebiewski & boyd, Starbird et al. 2019 |
| `prebunking_note` | One-sentence technique-recognition cue | Roozenbeek et al. 2022 |
| `consensus_explanation` | 6,000-10,000 character mechanism-level scientific explanation | (v0.4.0) |

A scope scrubber converts editorial policy into a mechanical guarantee. Publisher names are blocked with word-boundary regex and proper-noun-run detection. A model swap cannot accidentally emit content that names and accuses.

---

## External Surface Hardening (v0.9.0-v0.11.0)

The diagnostic fields from v0.8.0 are powerful. They also create a defamation surface. Three releases closed that surface systematically.

**v0.9.0** wrapped every external boundary in a regulated envelope:
- 10 serialization surfaces projected through a single `project_analysis()` helper
- Operator field suppression via environment variable (validated against allowlist at startup)
- OpenAPI advisory descriptions documenting GDPR Art. 22 and EU AI Act Annex III limitations
- Webhook secret prefix leak fixed

**v0.10.0** promoted cognitive warfare and frame capture from description-prefix workarounds to first-class `AuditFinding` categories. The Auditor prompt now emits these directly instead of encoding them as tagged strings inside other categories. Gallery rendering for all four Bridge diagnostic fields shipped in the same release.

**v0.11.0** closed the remaining exfiltration channel. Suppressed Bridge field content could still leak through Auditor free-text descriptions. A sentence-level scrubber now catches references to suppressed field names (underscore, space, short-form variants, case-insensitive) and replaces matching sentences with a redaction marker. An `audit_redacted` flag on every response discloses when scrubbing fired. Best-effort, honest about its limits.

The engineering discipline: diagnostic power and legal safety shipped in the same pipeline.

---

## Quick Start

**Requirements:** Python 3.12+, [Ollama](https://ollama.ai) running locally

```bash
# Install from source
uv pip install -e .

# Pull a model
ollama pull qwen3.5:9b

# Quick check (~10 seconds)
huginn check "claim text here"

# Full 6-agent analysis (30-90 seconds)
huginn analyze "claim text here"

# Auto-choose method based on claim complexity
huginn analyze "claim text here" --auto-escalate
```

**Docker:**
```bash
cp .env.example .env   # Edit OLLAMA_BASE_URL
docker compose up -d   # Web UI at http://localhost:8000
```

**API:**
```bash
uvicorn huginn_muninn.api:app --host 0.0.0.0 --port 8000
```

---

## Designed Against Dependency

A 2025 study (Rani et al.) found that AI dialogue can reduce conspiracy beliefs by 21% while simultaneously degrading independent discernment by 15% over four weeks. This dependency paradox is a real risk for any AI fact-checking tool. I take it seriously enough to have redesigned the entire Bridge Builder around it.

Four architectural pillars address it:

1. **Genuine Socratic method.** The system asks questions that guide reasoning, not verdicts that replace it. Rani et al.'s own data shows guiding questions correlate positively with independent detection skills (r=0.29). Directive correction undermines them.
2. **Mandatory fading.** AI support withdraws as user competence grows. Without explicit fading, the learning zone collapses.
3. **Desirable difficulties.** Users attempt their own analysis before seeing the AI's. Slower short-term performance, better long-term retention (Bjork, 1994).
4. **System-regulated access.** Research from Wharton shows system-regulated AI access produces 64% learning gains versus 30% for unrestricted access. Users can't be trusted to self-limit AI reliance. The system enforces structure.

The graduation model: learn the Three Questions. Apply them yourself. Stop needing the tool. That's the goal.

---

## Manufactured Doubt Detection

28 tactics from Goldberg et al. (2021, Environmental Health), documented across the tobacco, fossil fuel, sugar, pesticide, and climate denial industries. Five appeared universally:

1. Attack Study Design (exaggerate methodological flaws)
2. Gain Reputable Support (recruit credible figures)
3. Misrepresent Data (cherry-pick, design studies to fail)
4. Hyperbolic Language ("junk science," absolutist framing)
5. Influence Government (regulatory capture, revolving door)

The system distinguishes manufactured doubt from genuine scientific uncertainty through structural signatures: manufactured doubt always concludes toward inaction, shows asymmetric scrutiny of evidence, and traces to concentrated funding sources. Genuine uncertainty is specific, bounded, and proposes research to resolve itself.

---

## Research Foundation

370+ sources across two research waves. Honest confidence ratings, because transparency matters more than appearance.

| Domain | Confidence | Key Research |
|--------|-----------|-------------|
| Socratic AI Dialogue | **Strong** | Costello et al. (Science, 2024): 20% durable reduction. AAAS Newcomb Cleveland Prize 2026. Dependency caveat addressed by design. |
| Inoculation / Prebunking | **Moderate-Strong** | van der Linden & Roozenbeek; Google/Jigsaw (5.4M users). Meta-analysis 2025 (N=37,075) confirms. Lab-to-field gap remains. |
| Manufactured Doubt | **Strong** | Goldberg et al. (2021): 28 tactics, 5 industries. Well-documented, cross-industry. |
| Cognitive Apprenticeship | **Strong** | Collins, Brown & Newman (1989): decades of replication. |
| Perception Gap | **Weak** | More in Common (2019): US-only, single study. Used cautiously. |
| Narrative Complexity | **Moderate** | Peter Coleman (Columbia): compelling theory, limited RCTs. |

**Downgraded pillars:**
- **Moral Reframing** (Feinberg & Willer): 6+ preregistered replication failures. Experimental only until a successful large-N replication.
- **Redirect Method** (Moonshot): measures engagement, not belief change. Complementary signal, not a primary mechanism.

Full research corpus in the `research/` directory.

**Applied framework notes.** Philosophical foundations are examined in companion essays. The first is [The Sophists and the Three Questions](research/sophists-and-the-three-questions.md), which applies the framework to a claim about its own Socratic inheritance. Web version at `gallery/dist/essays/sophists-and-the-three-questions.html`.

---

## Rejection Log

Every rejected feature ships with documented falsification criteria. The decision can be revisited if the evidence changes.

| Rejected | Why | Revisit When |
|----------|-----|-------------|
| Density-matrix entropy | No concrete Hilbert space | Paper with measurable construction |
| Weaponized Absurdity | Violates Charter 4 + 6 | Peer-reviewed RCT showing superiority to Socratic dialogue |
| "Victim" framing | Removes agency | Never (philosophical commitment) |
| `timing_suspicion` | False-positive on legitimate journalism | Labeled corpus with 0% false-positive gate |
| Self-Poisoning Triad | Charter 1: no surveillance/dossiers | Never (charter commitment) |
| Moral Reframing | 6+ replication failures | Successful large-N replication |

Intellectual honesty takes longer than shipping features. That's the point.

Full log with falsification criteria: [REJECTIONS.md](REJECTIONS.md).

---

## Test Suite

| Version | Tests |
|---------|-------|
| v0.1.0 | 304 |
| v0.7.0 | 86 (public repo after restructure) |
| v0.8.0 | 228 |
| v0.9.0 | 511 |
| v0.11.0 | 544 |

20 real-world scenarios validated across health & science, geopolitics, environment, events, technology, and media.

---

## Privacy

Your data never leaves your machine. Huginn & Muninn runs entirely on local hardware using open-source models through Ollama. No cloud dependency. No API keys required for base usage. No data collection.

If you are analyzing sensitive political claims, you should not have to trust a third party with that data.

---

## Anti-Weaponization Charter

This matters enough to build before the features.

The [Anti-Weaponization Charter](ANTI-WEAPONIZATION-CHARTER.md) defines 8 non-negotiable commitments. The system cannot manufacture false common ground. It cannot be used as a persuasion engine for any agenda. It acknowledges when moral positions are genuinely irreconcilable. Actor-category symmetry tests (v0.8.0) ensure structurally equivalent attack signatures classify identically regardless of whether the actor is a state or non-state entity. Any divergence is a charter violation.

Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen.

---

## Contributing

Contributions welcome. Open an issue first to discuss what you'd like to change.

Areas where contributions are particularly valuable:
- Cross-cultural validation of the Three Questions framework
- Multilingual support (the Socratic dialogue principles are culturally specific)
- Manufactured doubt detection for non-Western contexts
- Integration with PKM tools (Obsidian plugin, browser extension)

---

## Built With AI

I built this with Claude (Anthropic). All research synthesis, design decisions, editorial voice, and final calls are mine. Claude helped with code generation, adversarial testing, and literature review.

Transparency matters. If I'm building a tool that teaches people to evaluate information sources, I should be upfront about my own.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Citation

If you reference this work in an academic context, please cite the underlying research directly:

> Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*, 385(6714).

> Goldberg, R. F., Vandenberg, L. N., et al. (2021). The science of spin: targeted strategies to manufacture doubt. *Environmental Health*, 20, 33.

> Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the crafts of reading, writing, and mathematics.

---

*Current version: v0.11.0 "Auditor Exfiltration Guard". 544 tests. The mission hasn't changed: de-polarize, find common ground, then make the tool unnecessary.*

*Author: Jochen Schmiedbauer*
