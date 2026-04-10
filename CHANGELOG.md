# Changelog

All notable changes to Huginn & Muninn are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

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
