# Changelog

All notable changes to Huginn & Muninn are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

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
