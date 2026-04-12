# Huginn & Muninn: Release Evolution

> From foundation to cognitive warfare detection in 38 days.
> This document traces every shipped version, what each added, and the design decisions behind the arc.
> Use it as the basis for LinkedIn posts, article changelogs, and conference talks.

---

## The Arc

Huginn & Muninn started as a two-pass fact-checker and evolved into a 6-agent disinformation analysis framework with cognitive warfare detection, scoped diagnostic fields grounded in peer-reviewed literature, and an external-surface hardening layer that projects all results through a regulated envelope. Every feature ships with adversarial review, every rejection is documented with falsification criteria, and every new field declares a safe default so nothing breaks.

The mission has not changed: de-polarize the world by helping people find each other as human beings. The tool is a cognitive gymnasium that teaches a transferable mental framework (the Three Questions), then makes itself unnecessary.

---

## v0.1.0 "Foundation" (2026-03-05)

**What shipped:**
- Method 1: Quick Check (two-pass LLM verification, ~10 seconds)
- Method 2: 6-agent analysis pipeline
  - [1] Claim Decomposer: breaks input into verifiable sub-claims
  - [2] Origin Tracer: tracks claim origins and spread patterns
  - [3] Network Mapper: maps information flow and actor relationships
  - [4] TTP Classifier: labels manipulation techniques (DISARM framework)
  - [5] Bridge Builder: common humanity layer
  - [6] Adversarial Auditor: red-teams the analysis for bias and errors
- REST API (FastAPI) with health, check, analyze, feedback, and history endpoints
- CLI (click) with `check`, `analyze`, and `feedback` commands
- Docker deployment with docker-compose
- Web UI serving a single-page application
- Pydantic v2 inter-agent contracts enforcing schema at every boundary
- DISARM framework TTP classification
- Ollama integration (local-first, no cloud dependency)
- SQLite persistence with caching
- 304 tests passing

**Design foundation:**
- Local-first architecture: your data never leaves your machine
- The Three Questions as a transferable mental model
- Anti-Weaponization Charter with 8 non-negotiable commitments

---

## v0.2.0 "Open Source Launch" (2026-03-13)

**What shipped:**
- README.md with the Three Questions framework
- Anti-Weaponization Charter (8 commitments)
- MIT License
- Research foundation documentation (~240 sources across two research waves)
- Dependency paradox analysis: AI dialogue reduces conspiracy beliefs by 21% but degrades independent discernment by 15% (Rani et al. 2025). Solved via 4-pillar mitigation: genuine Socratic method, mandatory fading, desirable difficulties, system-regulated access.

**Why it matters:** This is when the project became public. The charter and dependency paradox documentation established that the tool is honest about its own risks.

---

## v0.3.0 "Bridge Builder Test Suite" (2026-03-26)

**What shipped:**
- Bridge Builder v2: inferential gap mapping, feasibility assessment, commercial motive analysis
- 20 real-world test scenarios across 6 categories (health & science, geopolitics, environment, events, technology, media)
- Test runner with 10 weighted evaluation checks
- Scientific research enhancement (~370 sources, citation verification)
- Comprehensive findings DOCX generator (19 scenarios)
- Socratic dialogue Round 2: systemic patterns over individual blame

**Why it matters:** The first empirical validation. 20 scenarios gave the Bridge Builder concrete evidence of what works and what doesn't.

---

## v0.3.1 "Temporal Context" (2026-03-27)

**What shipped:**
- Origin Tracer tracks how claims migrate between ideological camps over time
- Ideological migration and inversion mutation types
- TemporalContext Pydantic model (era, date_range, dominant_framing, key_actors, power_context, irony_or_inversion)

**Why it matters:** Claims don't exist in isolation. A talking point that started as left-wing environmentalism in the 1970s can become right-wing anti-globalism by 2020. Temporal context makes this visible.

---

## v0.4.0 "360-Degree View" (2026-03-27)

**What shipped:**
- Scientific Consensus layer (v4): presents the established scientific explanation with equal depth to the conspiracy analysis (6,000-10,000 characters of mechanism-level explanation)
- 6 new v4 scenario results (HS-01: 100%, HS-02: 94.7%, HS-04: 95.5%, EN-01: 97.3%, EV-03: 94.7%, GP-01: 94.7%)
- Comprehensive findings DOCX generator with v4 sections
- `consensus_explanation` field on BridgeOutput
- Evaluation: 11 weighted checks including consensus_explanation (12%)

**Why it matters:** A fact-checker that only deconstructs conspiracy theories without explaining the actual science creates an information vacuum. The 360-degree view fills it.

---

## v0.5.0 "Name the Trick" (2026-03-28)

**What shipped:**
- Technique Reveal (v5): each manipulation technique named in plain language, like revealing how a magic trick works
  - technique, how_it_works, used_by, where_used_here, historical_precedent, pattern_type
- Asymmetric Weight Principle: systematic multi-campaign strategies get proportionally more analysis than isolated framing choices
- GP-06 Scenario: Brexit/Farage sanewashing (technique recycling, media normalization, asymmetric weight across a multi-decade playbook)
- TechniqueReveal Pydantic model (6 fields)
- Evaluation: 12 weighted checks including technique_naming (8%)
- Setup Guide for non-technical users (Docker, CLI, Claude Code)
- Scenario Gallery: static site generator for browsing pre-run analysis results

**Why it matters:** "Before you know the mechanic, the illusion is seamless. The moment someone shows you the palm, the misdirection, the force, the spell breaks. You can never be fooled by that trick again." This is the inoculation principle made concrete.

---

## v0.6.0 "Follow the Breadcrumbs" (2026-03-29)

**What shipped:**
- Knowledge Graph: cross-scenario entity extraction into a NetworkX graph (587 nodes, 1,157 edges) using POLE-Extended schema
- Interactive Visualization: Cytoscape.js graph page with filter controls, neighbor highlighting, detail panels
- Cross-Scenario Deduplication: same actors and techniques across multiple scenarios unified into single nodes with proportional sizing
- 7 entity types: Scenario, Actor, Technique (DISARM TTP), Named Trick, Claim, Mutation, Temporal Era
- Graph Builder CLI
- Gallery Navigation across all pages
- 18 new tests (total 273 passing)

**Why it matters:** The same actors, techniques, and playbooks appear across multiple disinformation campaigns. The knowledge graph makes these cross-scenario connections visible. Click an actor and see every scenario they touch, every technique they deploy.

---

## v0.7.0 "Frame Capture" (2026-04-10)

**What shipped:**
- Cognitive warfare taxonomy from Briggs, Danyk, and Weiss (2026), cross-referenced against RAND "Firehose of Falsehood" and OODA-loop literature
- Three new DISARM technique entries:
  - **GT-001 White Noise**: high-volume, low-signal flooding that crowds the hypothesis space
  - **GT-002 Black Noise**: ecosystem-level source suppression before primary narratives are seeded
  - **GT-003 Pattern Injection**: synchronized narratives mimicking expert-consensus structure through fabricated sourcing, credential laundering, or investigative-journalism mimicry
- `hypothesis_crowding` on the Decomposer (low/medium/high qualitative scale)
- `manipulation_vector_density` and `complexity_explosion_flag` companion fields on Decomposer
- `notable_omissions` on the Origin Tracer (up to 3 missing source types)
- `relay_type` on NarrativeMutation (knowing/unknowing/ambiguous)
- `frame_capture_risk` on the Adversarial Auditor (none/possible/high)
- `_compute_hypothesis_expansion_score` deterministic orchestrator helper (zero LLM tokens)
- 25 new tests, research note at `research/gorgon-trap-integration.md`

**What was rejected (with falsification criteria):**
- Literal density-matrix / von Neumann entropy computation (no concrete Hilbert space)
- Weaponized Absurdity as counter-tactic (violates Charter Commitments 4 and 6)
- "Victim of cognitive warfare" framing (removes agency)
- Population-level mechanism claims (tool operates at individual-claim level)

**Why it matters:** Classical disinformation analysis focuses on whether a claim is true. A more recent class of attacks doesn't depend on individual false claims at all: they operate by overwhelming the audience's ability to decide which framings the evidence supports. v0.7.0 detects this class of attack.

---

## v0.8.0 "Scoped Diagnostics" (2026-04-11)

Sprint 2 completion. Three PRs, each grounded in peer-reviewed literature and enforced by adversarial tests.

### PR 1: Charter and Symmetry Foundations

**What shipped:**
- Actor-category symmetric invariance test suite: 5 adversarial pairs across 10 actor categories (6 state, 4 non-state). Structurally equivalent attack signatures must classify identically regardless of actor category. Any divergence is a charter violation.
- Documentation language lint with word-bounded regex + 60-character proximity gate
- Charter Commitment 7 expanded to operationalise anti-bias as actor-category symmetry
- Validation-failure marker: schema failures surface in `degraded_reason` instead of being masked
- 28 new tests

### PR 2: Verification Priority Triage

**What shipped:**
- `verification_priority` on SubClaim (critical/high/low, default low) with anti-inflation discipline: "marking everything critical defeats the triage purpose"
- Triggering criteria are strictly structural (falsifiable numeric assertion, material downstream harm), not legal-register
- Schema-level coherence validator: verifiable=False + critical silently downgrades to high
- Cache normalization: every cache read runs through AnalysisReport.model_validate().model_dump() so pre-Sprint-2 analyses surface every new default on cache hit
- Validation-failure marker enhancement with exception class name
- 77 new tests

### PR 3: Bridge Scoped Diagnostics

**What shipped:**
- `communication_posture` on BridgeOutput (direct_correction / inoculation_first / relational_first): advisory register orthogonal to numeric confidence. Grounded in McGuire 1964, van der Linden 2017/2020, Roozenbeek & van der Linden 2022, Perry et al. 2018, Costello, Pennycook & Rand 2024.
- `pattern_density_warning` boolean: flags claims whose structural features predispose over-connection. Grounded in Alter & Oppenheimer 2009, Schwarz 1998 on processing-fluency effects.
- `vacuum_filled_by`: narrative-pattern-only description of what filled an information vacuum. Grounded in Golebiewski & boyd data-voids literature, Starbird et al. 2019.
- `prebunking_note`: one-sentence technique-recognition cue. Grounded in Roozenbeek et al. 2022 on technique-specific prebunking durability.
- Schema-level scope scrubber: publisher blocklist with word-boundary regex + proper-noun-run detection. Replaces violations with `[scope:redacted-named-entity]` marker (degrade-do-not-crash). Converts prompt-level policy into implementation guarantee.
- Inferential Gap Map labeled as "[REPARATIVE PATTERN-INJECTION RESPONSE -- load-bearing]"
- Scientific grounding note: ~3,500 words, 27 peer-reviewed citations
- 35 new PR 3 tests + 12 scope scrubber tests + fleet round 2 mitigations

**What was rejected (with falsification criteria):**
- P2-8 `timing_suspicion`: structural false-positive exposure on legitimate journalism, protest, and grassroots activity (Charter Commitment 3 violation)
- P2-9 Frame-Amplification Pre-Check: letting frame-risk suppress verification recreates the Sprint 1 rejection
- P2-13 Self-Poisoning Triad: Charter Commitment 1 (no surveillance/dossiers/profiling) is dispositive

**Review discipline:**
- 6-faction fleet review on every PR (Federation, Klingon, Romulan, Ferengi, Borg, Holodeck)
- Codex GPT-5.4 adversarial cross-model review on every PR
- Zero regression against all Sprint 1 constraints
- Test evolution: 116 (PR 1) -> 193 (PR 2) -> 228 (PR 3)

**Why it matters:** The Bridge Builder went from "here is what is true" to "here is how to communicate this effectively to someone who currently believes otherwise, based on the peer-reviewed literature on what actually changes minds." The scope scrubber is a particularly important discipline: it converts the prompt-level "no named publishers" policy into a mechanical implementation guarantee, so a model swap cannot accidentally emit defamatory content.

---

## v0.9.0 "External Surface Hardening" (2026-04-12)

Sprint 3 PR 1. Closes the compound defamation-surface blocker from Sprint 2.

**What shipped:**
- `AnalysisResponse` envelope model: wraps projected AnalysisReport in `{data, suppressed_fields, api_version}`. The `data` field is a strict subset of the internal AnalysisReport (machine-enforced by test).
- `project_analysis()` helper: single entry point for all 10 serialization boundaries. Handles cache normalization + envelope construction.
- 10 serialization boundaries now projected: `/api/analyze`, `/api/jobs/{id}`, `/api/batch/{id}`, `/api/check-and-escalate`, `/api/history`, `/api/compare`, webhook dispatch, callback dispatch, CLI JSON output, and CLI pretty-print.
- Operator field suppression via `HUGINN_SUPPRESS_FIELDS` env var: comma-separated list of Bridge fields to replace with safe defaults. Validated against allowlist at startup.
- CLI rendering for all Sprint 2 Bridge fields (communication_posture badge, pattern_density_warning conditional warning, vacuum_filled_by and prebunking_note conditional paragraphs)
- OpenAPI advisory descriptions on 5 regulated fields (GDPR Art. 22 / EU AI Act Annex III prophylactic)
- Webhook secret prefix leak fixed (was exposing first 8 hex chars of HMAC secret)
- Orchestrator return normalized through AnalysisReport contract (BG-050 cache normalization)
- ~58 new tests (511 total on monorepo, 510 on public repo)

**Review discipline:**
- 6-faction fleet review of Sprint 3 plan (~4,800 lines across 6 independent reviewers)
- Highest fleet convergence ever: 6/6 factions independently found the 8th serialization boundary
- Adversarial plan review found the strict-subset/disclosure contradiction (resolved via envelope pattern)
- 16 zero-regression constraints locked (expanded from Sprint 2's 14)

**Why it matters:** Sprint 2 shipped powerful diagnostic fields. Sprint 3 ensures those fields cannot become a liability. Every external boundary now projects through a regulated envelope, operators can suppress sensitive fields, and the API documents its own regulatory limitations. The compound defamation-surface blocker is closed.

---

## Test Evolution

| Version | Tests | Delta |
|---------|-------|-------|
| v0.1.0 | 304 | baseline |
| v0.5.0 | ~255 | (restructured) |
| v0.6.0 | 273 | +18 |
| v0.7.0 | 86* | (public repo baseline after restructure) |
| v0.8.0 PR 1 | 116 | +30 |
| v0.8.0 PR 2 | 193 | +77 |
| v0.8.0 PR 3 | 228 | +35 |
| v0.9.0 | 511 (monorepo) / 510 (public) | +283 |

*v0.7.0 count reflects the public repo test suite after project restructure; monorepo count is higher.

---

## Cumulative Feature Count by Agent

| Agent | Fields Added | Version |
|-------|-------------|---------|
| **Decomposer** | hypothesis_crowding, manipulation_vector_density, complexity_explosion_flag, verification_priority | v0.7.0, v0.8.0 |
| **Origin Tracer** | notable_omissions, relay_type, temporal_context | v0.7.0, v0.3.1 |
| **Network Mapper** | (core from v0.1.0) | v0.1.0 |
| **TTP Classifier** | GT-001, GT-002, GT-003, technique_reveal | v0.7.0, v0.5.0 |
| **Bridge Builder** | consensus_explanation, inferential_gap_map, communication_posture, pattern_density_warning, vacuum_filled_by, prebunking_note, socratic_dialogue (3 rounds) | v0.4.0-v0.8.0 |
| **Adversarial Auditor** | frame_capture_risk, gorgon_signals | v0.7.0 |
| **Orchestrator** | hypothesis_expansion_score, AnalysisResponse projection | v0.7.0, v0.9.0 |

---

## Research Foundation

| Version | Research Contribution |
|---------|---------------------|
| v0.2.0 | ~240 sources, dependency paradox, 4-pillar mitigation |
| v0.3.0 | ~370 sources, 20-scenario empirical validation |
| v0.5.0 | Asymmetric Weight Principle, manufactured doubt taxonomy (Goldberg et al. 2021) |
| v0.7.0 | Briggs, Danyk, Weiss 2026 cognitive warfare taxonomy, 4 explicit rejections with falsification criteria |
| v0.8.0 | 27 peer-reviewed citations in scientific grounding note; McGuire 1964, van der Linden, Roozenbeek, Costello/Pennycook/Rand 2024, Schwarz, Alter & Oppenheimer, Golebiewski & boyd, Starbird et al. |
| v0.9.0 | GDPR Art. 22 / EU AI Act Annex III advisory descriptions |

---

## Rejection Log (Documented Falsification Criteria)

Every rejection includes the conditions under which the decision would be revisited.

| What | Why Rejected | Revisit When |
|------|-------------|--------------|
| Density-matrix / von Neumann entropy | No Hilbert space, no measurement protocol | Paper with concrete construction + measurable interference |
| Weaponized Absurdity counter-tactic | Violates Charter 4 + 6, contradicts Costello protocol | Peer-reviewed RCT showing superiority to Socratic dialogue |
| "Victim" framing | Removes agency, creates rescuer-victim dynamic | Never (philosophical commitment) |
| Population-level claims | Tool operates at individual-claim level | Replicable cross-claim validation methodology |
| P2-8 `timing_suspicion` | False-positive on legitimate journalism/protest | Labeled corpus with 0% false-positive gate |
| P2-9 Frame-Amplification Pre-Check | Frame-risk suppressing verification | Additive-only posture overlay (partially addressed by communication_posture) |
| P2-13 Self-Poisoning Triad | Charter Commitment 1: no surveillance/dossiers | Never (charter commitment) |
| Moral Reframing (Feinberg & Willer) | 6+ preregistered replication failures | Successful large-N replication |

---

## Architectural Patterns (BG Registry)

Key patterns established across the release history:

| ID | Pattern | Version |
|----|---------|---------|
| BG-042 | Confidence-Posture Separation: posture is orthogonal to confidence, enforced by runtime invariance + grep lock | v0.8.0 |
| BG-043 | Pattern Density Upstream Gating: warning requires upstream signal, not standalone LLM judgment | v0.8.0 |
| BG-044 | Symmetric Signature Invariance: equivalent signatures classify same regardless of actor category | v0.8.0 |
| BG-050 | Cache Normalization via Contract Round Trip: model_validate + model_dump on every cache read | v0.8.0 |
| BG-054 | API Surface Projection: dedicated projection model at every external boundary | v0.9.0 |
| BG-055 | Operator-Configurable Field Suppression: env-var driven with startup validation | v0.9.0 |

---

## What's Next

### Sprint 3 PR 2 (CONDITIONAL)

- AuditFinding.category Literal expansion (`cognitive_warfare`, `frame_capture`) with docs generator update
- Gallery/docs rendering for Sprint 2 Bridge fields
- Defers without liability if bandwidth is tight

### Sprint 4+ Backlog

- Auditor description exfiltration channel (suppressed field content can leak through audit findings)
- Unicode homoglyph scope scrubber hardening
- DNS rebinding TOCTOU on callback URLs
- `degraded_reason` agent name leak
- BG-051/052/053 pattern registry audit
- `frame_capture_risk` zero-consumer debt
- Bridge prompt refactor (headroom adequate, not urgent)

---

*Last updated: 2026-04-12. Current version: v0.9.0 "External Surface Hardening". 511 tests passing.*
