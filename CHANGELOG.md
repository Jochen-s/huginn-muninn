# Changelog

All notable changes to Huginn & Muninn are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.9.0] - 2026-04-12 -- "External Surface Hardening"

Sprint 3 PR 1. Closes the compound defamation-surface blocker from Sprint 2 by projecting all Method 2 analysis results through an `AnalysisResponse` envelope at every external serialization boundary. Adds operator field-suppression configuration, CLI rendering for Sprint 2 Bridge fields, and OpenAPI advisory descriptions.

### Added
- **`AnalysisResponse` envelope model** in `contracts.py`: wraps projected `AnalysisReport` in a `data` field with `suppressed_fields` disclosure (Charter Commitment 5: transparent uncertainty) and `api_version` metadata. Constructed via `from_report()` classmethod from a validated `AnalysisReport` instance. `data` is a strict subset of `AnalysisReport` (machine-enforced by test). Response-envelope metadata is exempt from the strict-subset constraint.
- **`project_analysis()` helper** in `projection.py`: single entry point for all 10 serialization boundaries. Handles BG-050 normalization (legacy cache hits get all schema defaults) followed by AnalysisResponse envelope construction.
- **Operator field suppression** via `HUGINN_SUPPRESS_FIELDS` environment variable: comma-separated list of BridgeOutput field names to replace with safe defaults in all external responses. Valid fields: `communication_posture`, `pattern_density_warning`, `vacuum_filled_by`, `prebunking_note`. Validated against allowlist at startup (unknown names raise ValueError). Defaults to unsuppressed (backward compatible). Suppression takes effect at process startup via frozen Settings singleton.
- **CLI rendering** for 4 Sprint 2 Bridge fields: `communication_posture` as labeled badge (hidden when default), `pattern_density_warning` as conditional warning, `vacuum_filled_by` and `prebunking_note` as conditional paragraphs. `[scope:redacted-named-entity]` marker handled gracefully. JSON output path (`--json-output`) applies full AnalysisResponse projection.
- **OpenAPI `Field(description=...)` advisory restrictions** on 5 regulated fields: `communication_posture` (GDPR Art. 22 / EU AI Act Annex III advisory-only), `verification_priority` (not a legal/clinical/regulatory determination), `pattern_density_warning` (not a moderation signal), `vacuum_filled_by` (narrative pattern only), `prebunking_note` (technique-recognition cue).
- **Operator documentation** in README: field suppression guide, valid fields, s.179 audit limitation disclaimer, Auditor-exfiltration known limitation.
- **~58 new tests**: `TestSuppressedFieldsConfig` (8), `TestAnalysisResponse` (8), `TestProjectAnalysis` (7), plus 22 previously-erroring tests resolved by `pytest-httpx` installation, plus CLI and API projection tests.

### Changed
- **10 serialization boundaries now projected** through `AnalysisResponse`: `/api/analyze`, `/api/jobs/{id}`, `/api/batch/{id}`, `/api/check-and-escalate` (method_2 key), `/api/history` (normalize then project), `/api/compare` (post-comparison projection), webhook dispatch, callback dispatch, CLI JSON output. All boundaries project at READ time only; the internal job store retains the full `AnalysisReport`.
- **Orchestrator return normalized**: `orchestrator.py` now returns `AnalysisReport(**result).model_dump(mode="json")` instead of the raw dict, ensuring all downstream consumers receive schema-valid data with computed defaults populated (Borg AP-1 fix).
- **Webhook secret prefix leak fixed**: `GET /api/webhooks` and `GET /api/webhooks/{id}` and `PATCH /api/webhooks/{id}` now return `secret_configured: true` instead of exposing the first 8 hex characters of the HMAC secret (Klingon security fix). The full secret is still returned once on `POST /api/webhooks` creation.

### Review discipline
- **Six-faction fleet review** of the Sprint 3 plan (Federation 67/100, Klingon 34/100 pre-hardening, Romulan 4/10->7/10, Ferengi 7/10 ROI, Borg 7/10, Holodeck 7/10). ~4,800 lines of independent review across 6 reviewers. Highest fleet convergence of any H&M sprint: 6/6 factions independently found the 8th serialization boundary.
- **Adversarial plan review** found the strict-subset/disclosure contradiction (Medium-High), comparison projection point error, and bidirectional completeness test gap. All mitigated in the final plan.
- **16 zero-regression constraints** locked (expanded from Sprint 2's 14).

## [0.8.0] - 2026-04-11 -- "Scoped Diagnostics"

Sprint 2 completion release. Charter and symmetry foundations, verification priority triage, and Bridge Builder scoped diagnostics. Every shipping item is grounded in peer-reviewed literature and enforced by adversarial tests.

### Added (Sprint 2 PR 3 -- Bridge Scoped Diagnostics)
- **`communication_posture` on `BridgeOutput`**: A `Literal["direct_correction","inoculation_first","relational_first"]` field that selects the communicative register of the analysis, orthogonal to numeric confidence. `direct_correction` is the default and classical-refutation posture. `inoculation_first` follows the McGuire 1964 / van der Linden 2017/2020 / Roozenbeek & van der Linden 2022 prebunking literature and leads with naming the manipulation technique before introducing counter-evidence. `relational_first` follows the Common Humanity (Perry et al.) / Costello protocol (Costello, Pennycook, Rand 2024) literature and starts from acknowledgment of the kernel of truth before any correction. Posture is advisory to downstream communicators; it is mechanically separated from `overall_confidence` by runtime invariance tests and a grep-style architectural lock (BG-042 Confidence-Posture Separation).
- **`pattern_density_warning` on `BridgeOutput`**: A content-describing boolean that flags claims whose structural features (repeated numeric coincidences, rhythmic lexical choices, escalating concept chains) predispose readers to over-connect. Grounded in Alter & Oppenheimer 2009 / Schwarz 1998 on processing-fluency effects. The flag describes the claim, never the reader.
- **`vacuum_filled_by` on `BridgeOutput`**: A narrative-pattern-only description of what filled an expertise or information vacuum around the claim. Grounded in the Golebiewski & boyd data-voids literature and Starbird et al. 2019 on collaborative disinformation. Prompt-enforced strict scope: no named publishers, no named individuals, no named organisations.
- **`prebunking_note` on `BridgeOutput`**: A one-sentence technique-recognition cue a reader can carry forward. Grounded in Roozenbeek, van der Linden, Goldberg, Rathje & Lewandowsky 2022 on technique-specific prebunking durability. Additive to the Inferential Gap Map; never a substitute.
- **P2-11 Inferential Gap Map labeling**: The existing Layer 4 inferential-gap instruction is now explicitly labeled in the Bridge Builder prompt as "[REPARATIVE PATTERN-INJECTION RESPONSE -- load-bearing]", making the intent legible to future editors. The underlying kernel-and-leap instruction is unchanged; a new `TestBridgePromptPreservation` class enforces that it cannot drift.
- **35 new tests**: `TestBridgeCommunicationPosture` (8), `TestBridgePatternDensityWarning` (3), `TestBridgeVacuumFilledByAndPrebunkingNote` (7), `TestBridgePromptPreservation` (4), `TestBridgeCommunicationPosturePrompt` (4), `TestBridgeScopedP26Prompt` (5), and four confidence-invariance / integration tests.
- **Research note**: `research/bridge-scoped-diagnostics-scientific-grounding.md` -- a ~3,500-word record of the peer-reviewed literature behind each new field, with revisit triggers for replication failures.
- **Sprint 2 PR 3 Codex mitigations** (5 must-fixes): Codex GPT-5.4 adversarial review returned HOLD with a High-severity blind spot -- `vacuum_filled_by` and `prebunking_note` were prompt-constrained to narrative patterns only, but the schema accepted toxic strings naming publishers/organisations/individuals if the LLM ignored the prompt. The policy guarantee was not yet an implementation guarantee. Fixes shipped: (1) schema-level scope scrubber at `contracts.py::_scope_scrub_narrative_pattern_fields` with blocklist + proper-noun-run detection, replacing scope violations with `[scope:redacted-named-entity]` marker (degrade-do-not-crash); (2) 12 new negative tests in `TestBridgeScopeScrubber` covering named publishers, state-aligned outlets for symmetric enforcement, multi-token Capitalised runs, and narrative-pattern preservation; (3) integration test `test_pipeline_scrubs_named_publisher_in_vacuum_filled_by` proving the scrubber fires through the full orchestrator boundary; (4) symmetric-actor integration test `test_pipeline_symmetric_actor_swap_on_bridge_fields` extending BG-044 invariance to the four PR 3 fields; (5) `TestBridgePromptTokenBudget` locking the Sprint 2 Zero-Regression Constraint #5 of <6,500 input tokens against accidental prompt drift. Science note §3.4 rewritten to hedge the `relational_first` posture's Common Humanity / Costello grounding explicitly as design-informed synthesis rather than a validated posture-taxonomy finding.
- **Sprint 2 PR 3 fleet mitigations round 2** (follow-up commit after 6-faction review returned post-merge): (1) `MOCK_RESPONSES["bridge_builder"]` fixture in `test_orchestrator.py` extended with all four new fields, closing the Federation-flagged pattern divergence from PR 2. (2) Grep-style architectural lock in `test_communication_posture_not_referenced_in_confidence_computation` hardened against duplicate-sentinel false-pass by adding `count == 1` assertions and sentinel-ordering check -- four-faction convergence (Federation, Klingon, Borg, Ferengi). (3) `inoculation_first` prompt line rewritten from "only then introduce counter-evidence" to "then introduce counter-evidence within the same response" plus explicit POSTURE SCOPE clause stating all four analytical layers must be produced in full regardless of posture, closing the Klingon/Romulan convergent P2-9-regression concern. (4) `vacuum_filled_by` prompt example "astroturf-grade citizen testimonials" replaced with neutral "repeated numeric coincidences stacking toward a single conclusion" plus Charter Commitment 3 guard against conflating authentic grassroots voice with engineered campaigns, closing Holodeck I-roles. (5) `communication_posture` schema docstring extended with advisory-only disclaimer explicitly warning against automated routing-gate use (GDPR Art. 22 / EU AI Act Annex III prophylactic, Romulan MUST #2). (6) `prebunking_note` gains `max_length=500` Field constraint, mirroring `socratic_dialogue` max_length=3 discipline from Sprint 1 (Borg Minor #4). (7) Vacuous `assert "not" in lower` in `test_prebunking_note_forbids_new_factual_assertions` replaced with an anchored assertion on the section I header canonical phrase "NOT a new factual assertion" (Federation + Klingon Minor). (8) `test_consensus_explanation_instruction_preserved` tightened to assert on the fuller canonical phrase "equal depth and specificity" at its canonical section A location (Federation Minor #3). (9) `pattern_density_warning` prompt section G gains upstream-signal gating hints (`hypothesis_crowding=high`, `complexity_explosion_flag=true`) plus explicit rhetorical-form exclusion list (protest chants, liturgy, legal argument, poetry, educational mnemonics), closing the Borg BG-043 gate gap and Holodeck I3 Commitment 3 exposure. (10) Science note citation corrections: Roozenbeek et al. 2022 *Science Advances* identified as the primary empirical durability source; van der Linden 2020 relabeled as theoretical synthesis; Kappes et al. 2020 mischaracterisation corrected to "mechanistic building block, theoretical extension, not a direct empirical finding"; "five-month durability" claim for Common Humanity removed entirely; Briggs/Danyk/Weiss 2026 author initials unified across research notes to the Sprint 1 gorgon-trap-integration.md canonical form pending Zenodo record verification; effect-size + decay caveat added to the inoculation durability claim per Holodeck P-roles convergent findings. (11) Revisit-trigger section extended with Tiwari & Elmufti 2024 in-press resolution and Briggs Zenodo verification pending triggers. (12) Symmetric-actor integration test strengthened to actually vary upstream MOCK_MAPPER actor categories (state vs commercial) rather than being a pure idempotency check, making the BG-044 extension a genuine symmetry test.

### Added (Sprint 2 PR 2 -- Verification Priority)
- **`verification_priority` on `SubClaim`**: A `Literal["critical","high","low"] = "low"` triage field with a strict anti-inflation discipline in the Decomposer prompt. The anti-inflation clause ("marking everything critical defeats the triage purpose and degrades downstream resource allocation") is load-bearing and test-enforced. Structural triggering criteria only -- the prompt explicitly forbids triage based on legal-register language, politically-charged topics, or named-individual references.
- **Schema-level coherence validator**: `verifiable=False + verification_priority="critical"` is an incoherent combination; the schema silently downgrades to `"high"` rather than raising, mirroring Sprint 1's "degrade, do not crash" discipline.
- **Cache normalization**: `HuginnDB._normalize_cached_analysis` runs every cache read through `AnalysisReport.model_validate().model_dump()` so pre-Sprint-2 analyses surface every new Pydantic default on cache hit. Fixes a High-severity blind spot where fresh runs would carry new fields and cache hits would silently omit them.
- **Validation-failure marker enhancement**: The production-boundary marker at `orchestrator.py` now includes the exception class name (`validation_error:<ClassName>`) so downstream log aggregators can distinguish schema drift from other validation failures.
- **77 new tests** covering triage defaults, literal drift (trailing-space, punctuation, capitalization, None, comma-separated, pipe-separated), cross-field coherence, cache normalization, Auditor count-invariance, priority-confidence invariance, and Decomposer prompt preservation.

### Added (Sprint 2 PR 1 -- Charter and Symmetry Foundations)
- **Actor-category symmetric invariance test suite**: `tests/test_gorgon_symmetry.py` with 5 adversarial pairs asserting bit-equivalent TTP classification and severity counts across 10 actor categories (state and non-state). Operationalises Anti-Weaponization Charter Commitment 7.
- **Symmetric actor extension plan**: `research/gorgon-trap-symmetric-actor-extension.md` as the parent research note for the invariance discipline.
- **Documentation language lint**: `tests/test_docs_language.py` with a word-bounded regex lint + 60-character proximity gate enforcing the charter's vocabulary discipline across public-facing docs.
- **Charter Commitment 7 expansion**: `ANTI-WEAPONIZATION-CHARTER.md` expanded to operationalise anti-bias vigilance as actor-category symmetry.
- **Validation-failure marker**: The production-boundary `AnalysisReport` validator at `orchestrator.py` now surfaces schema failures in `degraded_reason` instead of masking them as generic "critical agent failure". Closes a Codex-identified blind spot from Sprint 1.
- **28 new tests**: `test_docs_language.py` (8), `test_gorgon_symmetry.py` (18), and 2 validation-marker regression tests.

### Changed
- Bridge Builder prompt in `agents/bridge.py` gains five new sections (F/G/H/I plus the reparative-Pattern-Injection labeling) while preserving the existing load-bearing inferential_gap, narrative_deconstruction, and consensus_explanation instructions verbatim. A dedicated `TestBridgePromptPreservation` class enforces this preservation at the assertion level.
- `BridgeOutput` and `SubClaim` Pydantic schemas each gain safe defaults on every new field so that older LLM outputs, cached JSON, and the orchestrator's degraded-result fallback paths continue to parse against `AnalysisReport`.
- Both the normal and degraded orchestrator bridge-fallback paths explicitly carry every new field default -- a zero-regression requirement restated in the Sprint 2 plan.
- Decomposer prompt legal-register language removed per Romulan / Holodeck legal-review convergence. "Legal liability" and "criminal conduct" are no longer triggering criteria; structural ("material downstream harm", "falsifiable numeric assertion") language replaces them.

### Review discipline
- **Six-faction fleet review** on every PR (Federation, Klingon, Romulan, Ferengi, Borg, Holodeck).
- **Codex GPT-5.4 adversarial review** on every PR as an independent cross-model check.
- **Zero regression** against the Sprint 1 Codex-mandated constraints. Every Sprint 2 PR closed with the baseline plus net-new tests passing; Sprint 1 PR 1 shipped at 86 baseline -> 116 passing; PR 2 shipped at 116 -> 193; PR 3 shipped at 193 -> 228.

### Rejected in Sprint 2 (with falsification criteria)
- **P2-8 `timing_suspicion`**: Rejected as specified. Six factions plus Codex converged on the judgement that an LLM-generated "suspicious timing" flag creates structural false-positive exposure on legitimate journalism, protest, and grassroots activity -- a Charter Commitment 3 violation vector. Revisit only with a labeled-corpus 0% false-positive gate and observational-only scope.
- **P2-9 Frame-Amplification Pre-Check**: Deferred. The "route to inoculation-style response *instead of* direct refutation" framing recreates the Sprint 1 rejection by letting frame-risk suppress verification. An acceptable reformulation is an additive-only posture overlay, which `communication_posture` partially addresses.
- **P2-13 self-poisoning triad**: Rejected entirely. Charter Commitment 1 (no surveillance / dossiers / profiling) is dispositive. No Sprint 2 reformulation path.
- **S1 AuditFinding enum expansion**: Deferred. A hidden consumer in `docs/generate-comprehensive-findings.js` groups `AuditFinding.category` into report buckets; adding new literals would create unlabeled buckets in generated reports until the docs generator is updated.

## [0.7.0] - 2026-04-10 -- "Frame Capture"

### Added
- **Cognitive warfare taxonomy**: Three new DISARM technique entries covering attacks that target the sense-making phase of decision-making rather than the belief-formation phase. GT-001 (White Noise) flags information flooding that crowds the hypothesis space; GT-002 (Black Noise) flags ecosystem-level source suppression; GT-003 (Pattern Injection) flags synchronized narratives that mimic expert-consensus structure through fabricated sourcing, credential laundering, or investigative-journalism mimicry. All three are written in actor-neutral language and ship as heuristics pending community empirical validation. See `research/gorgon-trap-integration.md`.
- **`hypothesis_crowding` signal on the Decomposer**: A qualitative `low` / `medium` / `high` field on `DecomposerOutput` describing how many plausible competing interpretations the input framing admits. Narrowly scoped in the prompt so that the Decomposer cannot justify inflating sub-claim count to claim a higher rating.
- **`manipulation_vector_density` and `complexity_explosion_flag`**: Companion fields on `DecomposerOutput` that capture the ratio of sub-claims opening a manipulation surface and a boolean threshold flag on claim structure.
- **`notable_omissions` on the Origin Tracer**: A capped list (up to three entries) of source *types* that would be expected to exist for a claim's topic and era but are missing from the available context. The Tracer prompt enforces "missing from context" framing and disallows intent attribution and invented source names.
- **`relay_type` on `NarrativeMutation`**: Classifies each amplification step as `knowing`, `unknowing`, or `ambiguous`, defaulting to `ambiguous` when the relay's awareness is not explicit.
- **`frame_capture_risk` on the Adversarial Auditor**: A three-valued audit signal (`none` / `possible` / `high`) that detects when the pipeline's own analysis has adopted the input claim's framing, labels, or implied causality without independently restating the question. Deliberately chosen over the paper's "verification trap" terminology to prevent priming the Auditor against legitimate fact-checking. Assessment is gated on upstream signals (`hypothesis_crowding="high"`, non-empty `notable_omissions`, or a matched `GT-` TTP) so that the check does not degrade into speculative flagging.
- **`_compute_hypothesis_expansion_score` orchestrator helper**: A deterministic zero-token helper that derives a bounded 0.0-1.0 score from the Decomposer's existing output. Feeds the Auditor's context as part of a `gorgon_signals` dictionary so that `frame_capture_risk` gating relies on a reproducible signal rather than LLM re-inference.
- **25 new tests**: `TestGorgonFieldDefaults` (15) in `tests/test_contracts.py`, `TestHypothesisExpansionScore` (10) in `tests/test_orchestrator.py`, plus 3 Auditor prompt-shape tests and 2 backward-compatibility regression guards.
- **Research note**: `research/gorgon-trap-integration.md` documenting what was integrated from the Briggs et al. 2026 cognitive-warfare taxonomy, what was deliberately rejected (density-matrix formalism, weaponized absurdity counter-tactic, victim framing, population-level claims), the falsification criteria for each rejection, and the revisit triggers for future re-review.

### Changed
- `data/disarm_techniques.json` is now tracked in the repository. Previously `.gitignore` excluded the entire `data/` directory, which left a new checkout unable to run the classifier without manual intervention. The DISARM seed is now a committed first-class asset; transient `data/` artifacts remain ignored via a targeted pattern.
- The Adversarial Auditor's `build_prompt` now serializes `gorgon_signals` when present, so the deterministic hypothesis-expansion signal actually reaches the LLM. Without this step the helper would be dead code from the Auditor's perspective.
- All new `contracts.py` fields declare safe defaults so older LLM outputs, cached JSON, and the orchestrator's degraded-result fallback paths continue to parse against `AnalysisReport`.

### Rejected (with falsification criteria)
- **Literal density-matrix / von Neumann entropy computation**. No concrete Hilbert space, no measurement protocol, no falsifiable prediction, no predictive advantage over classical information theory. Falsification criterion: a paper that specifies a concrete construction with measurable interference effects.
- **Weaponized Absurdity as a counter-tactic**. Cited doctrinal support is a single satirical blog post, structurally opposed to the Bridge Builder, violates Anti-Weaponization Charter Commitments 4 and 6, and is inconsistent with Costello, Pennycook, and Rand (2024) on dignity-preserving belief change. Falsification criterion: a peer-reviewed randomized trial showing weaponized absurdity outperforms Socratic dialogue on depolarization metrics without compromising user dignity.
- **"Victim of cognitive warfare" framing**. Removes agency and creates a rescuer-victim dynamic inconsistent with the deep-canvassing evidence base. We use "people navigating information environments designed to exploit trust" instead.
- **Population-level mechanism claims**. Huginn & Muninn operates at the individual-claim level; the paper's systemic claims are not extrapolated into individual diagnostics.

## [0.6.0] - 2026-03-29 -- "Follow the Breadcrumbs"

### Added
- **Knowledge Graph**: Cross-scenario entity extraction into a NetworkX graph (587 nodes, 1,157 edges) using POLE-Extended schema. Reveals shared actors, recycled techniques, and narrative patterns across 20 disinformation scenarios.
- **Interactive Visualization**: Cytoscape.js graph page with filter controls (node type, category, text search), neighbor highlighting on click, and detail panels linking back to scenario analyses.
- **Cross-Scenario Deduplication**: Same actors (e.g., "Fossil Fuel Industry") and techniques (e.g., DISARM T0023 "Distort Facts") appearing in multiple scenarios are unified into single nodes with proportional sizing.
- **7 Entity Types**: Scenario, Actor, Technique (DISARM TTP), TechniqueReveal (Named Trick), Claim, Mutation, TemporalEra.
- **Graph Builder CLI**: `python graph/build_graph.py` extracts entities from JSON results and exports Cytoscape.js-compatible JSON.
- **Gallery Navigation**: Nav bar added to all gallery pages (index, 20 scenarios, knowledge graph).
- **Implementation Plan**: `docs/plans/2026-03-28-knowledge-graph-phase1.md` (17 tasks, TDD).
- **18 new tests** for graph builder (total 273 passing).

### Changed
- Gallery builder generates graph.html alongside scenario pages.
- `networkx>=3.0` added to dependencies.

## [0.5.0] - 2026-03-28 -- "Name the Trick"

### Added
- **Technique Reveal (v5)**: Each manipulation technique named in plain language, like revealing a magic trick. Includes mechanic explanation, historical precedent, and pattern classification.
- **Asymmetric Weight Principle**: Systematic multi-campaign strategies receive proportionally more analysis than isolated framing choices. Prevents false equivalence.
- **GP-06 Scenario**: Brexit/Farage sanewashing -- tests technique recycling, media normalization, and asymmetric weight across a multi-decade political playbook.
- **TechniqueReveal Pydantic model**: 6 fields (technique, how_it_works, used_by, where_used_here, historical_precedent, pattern_type).
- **Evaluation**: 12 weighted checks including technique_naming (8%).
- **Setup Guide**: Step-by-step for non-technical users (Docker, CLI, Claude Code).
- **Scenario Gallery**: Static site generator for browsing pre-run analysis results.
- **LinkedIn article proposal**: Documented framework for public communication.

### Changed
- Bridge Builder prompt v5 with Section E and Round 2 "NAME IT" instruction.
- Evaluation weights redistributed across 12 checks (was 11).
- 21 test scenarios (was 20).

## [0.4.0] - 2026-03-27 -- "360-Degree View"

### Added
- **Scientific Consensus (v4)**: Presents established scientific explanation with equal depth to the conspiracy analysis. 6,000-10,000 chars of mechanism-level explanation.
- 6 new v4 scenario results (HS-01: 100%, HS-02: 94.7%, HS-04: 95.5%, EN-01: 97.3%, EV-03: 94.7%, GP-01: 94.7%).
- Comprehensive findings DOCX generator with v4 sections.

### Changed
- BridgeOutput gains consensus_explanation field.
- Evaluation: 11 weighted checks including consensus_explanation (12%).

## [0.3.1] - 2026-03-27 -- "Temporal Context"

### Added
- **Temporal Context (v3)**: Origin Tracer tracks how claims migrate between ideological camps over time.
- Ideological migration and inversion mutation types.
- TemporalContext Pydantic model (era, date_range, dominant_framing, key_actors, power_context, irony_or_inversion).

## [0.3.0] - 2026-03-26 -- "Bridge Builder Test Suite"

### Added
- **Bridge Builder v2**: Inferential gap mapping, feasibility assessment, commercial motive analysis.
- 20 real-world test scenarios across 6 categories.
- Test runner with 10 weighted evaluation checks.
- Claude Code native pipeline runner.
- Scientific research enhancement (370+ sources, citation verification).
- Comprehensive findings DOCX (19 scenarios).

### Changed
- Socratic dialogue Round 2 improved: systemic patterns over individual blame.

## [0.2.0] - 2026-03-13 -- "Open Source Launch"

### Added
- README.md with Three Questions framework.
- Anti-Weaponization Charter.
- MIT License.
- Research foundation documentation (~240 sources).
- Dependency paradox analysis and 4-pillar mitigation.

## [0.1.0] - 2026-03-05 -- "Foundation"

### Added
- Method 1: Quick Check (two-pass verification).
- Method 2: 6-agent pipeline (Decomposer, Tracer, Mapper, Classifier, Bridge Builder, Auditor).
- REST API (FastAPI).
- CLI (click).
- Docker deployment.
- Web UI.
- Pydantic inter-agent contracts.
- DISARM framework TTP classification.
- Ollama integration (local-first).
- 304 tests.
