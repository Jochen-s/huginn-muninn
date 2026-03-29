# Phase B/C/D Evolution + SC-01 Cofnas Scenario Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to implement this design.

**Goal:** Evolve the Huginn & Muninn knowledge graph with cross-scenario connections (Phase B), lightweight perspective filtering (Phase C v1), advanced visualization modes (Phase D), and run the first Science Controversy scenario (SC-01: Cofnas IQ-race claims) with a LinkedIn engagement playbook.

**Approach:** Incremental ship per phase. Each phase ships independently to GitHub Pages. Phase C uses lightweight named filter presets (not full first-class graph entities).

---

## Phase B: Cross-Scenario Connections

### B1: Cross-Scenario Edges for Actors

When an actor appears in 3+ scenarios, generate `CROSS_SCENARIO` edges between those scenario nodes. Edge weight = number of shared actors between the pair.

- Add `_add_cross_scenario_edges(G)` after all per-scenario extraction
- Edge attributes: `edge_type="cross_scenario"`, `shared_actors=[list]`, `weight=count`
- Only between scenario pairs sharing 2+ actors (avoid noise from single-actor overlaps)

### B2: FLICC Taxonomy Mapping

Map existing DISARM technique IDs to the 5 FLICC categories:

| FLICC Category | DISARM IDs (from our data) |
|---|---|
| **F**ake experts | T0010 (Cultivate Ignorant Agents), T0022 (Leverage Conspiracy Theory) |
| **L**ogical fallacies | T0004 (Develop Competing Narratives), T0023 (Distort Facts) |
| **I**mpossible expectations | (mapped at runtime based on technique_name) |
| **C**herry picking | T0044 (Seed distortions), T0049 (Flooding) |
| **C**onspiracy theories | T0022 (Leverage Conspiracy Theory) |

Add `flicc_category` attribute to technique nodes. Some techniques map to multiple categories.

### B3: Technique Co-Occurrence Edges

When two techniques appear together in 3+ scenarios, add `CO_OCCURS` edge.

- Computed after all scenarios processed
- Edge attributes: `edge_type="co_occurs"`, `shared_scenarios=[list]`, `weight=count`
- Reveals "playbook patterns": which techniques travel together

### B4: Visualization Updates

- New filter option: "Playbook View" (scenarios + techniques + co-occurrence edges)
- FLICC color bands on technique nodes (5 colors, shown as border ring)
- Cross-scenario edges rendered as dashed lines, thickness proportional to shared actor count
- Tooltip on cross-scenario edges: "These scenarios share N actors: [names]"

### B5: Tests

~8 new tests: cross-scenario edge generation, FLICC mapping correctness, co-occurrence threshold, edge weight calculation.

---

## Phase C: Lightweight Perspectives (v1)

### C1: Perspective Configuration

`graph/perspectives.json` with 4 initial presets:

```json
[
  {
    "id": "scientific_consensus",
    "name": "Scientific Consensus",
    "description": "View weighted by evidence quality and source tier",
    "emphasis": {"node_types": ["technique", "claim"], "min_source_tier": 1},
    "moral_foundations": {"care": 0.3, "fairness": 0.3, "authority": 0.2, "liberty": 0.2}
  },
  {
    "id": "concerned_citizen",
    "name": "Concerned Citizen",
    "description": "View weighted by personal impact and safety",
    "emphasis": {"node_types": ["actor", "scenario"], "highlight_needs": ["safety", "fairness"]},
    "moral_foundations": {"care": 0.4, "fairness": 0.2, "loyalty": 0.2, "authority": 0.2}
  },
  {
    "id": "institutional_skeptic",
    "name": "Institutional Skeptic",
    "description": "View highlighting accountability gaps and commercial motives",
    "emphasis": {"node_types": ["actor"], "highlight_fields": ["commercial_motives", "credibility"]},
    "moral_foundations": {"fairness": 0.3, "liberty": 0.3, "authority": 0.2, "care": 0.2}
  },
  {
    "id": "bridge_builder",
    "name": "Bridge Builder",
    "description": "View highlighting shared reality and common ground",
    "emphasis": {"node_types": ["scenario"], "highlight_fields": ["issue_overlap", "universal_needs"]},
    "moral_foundations": {"care": 0.3, "fairness": 0.3, "loyalty": 0.2, "liberty": 0.2}
  }
]
```

### C2: False Polarization Gap Metric

Computed per scenario at build time:
- Count universal needs that appear in both "side_a" and "side_b" moral foundations
- Ratio: `shared_needs / total_unique_needs`
- Stored as scenario node attribute: `false_polarization_gap`
- Displayed in scenario detail panel and on scenario gallery pages

### C3: Perspective UI

- Dropdown in graph.html nav controls: "Perspective: [All | Scientific | Citizen | Skeptic | Bridge]"
- Switching perspective changes node opacity based on emphasis config
- Does NOT restructure the graph; purely visual filtering
- False Polarization Gap shown as a badge on scenario nodes when Bridge Builder perspective is active

### C4: Tests

~5 tests: perspective loading, gap computation, perspective filtering logic.

---

## Phase D: Advanced Visualization

### D1: Shared Reality Overlay

- Toggle button: "Show Shared Reality"
- Highlights in gold all scenario nodes where `false_polarization_gap > 0.6` (majority shared)
- Highlights in gold all actor nodes connected to 3+ scenarios (cross-cutting figures)
- Visual: gold glow/border effect on qualifying nodes

### D2: Comparison View

- UI: Two perspective dropdowns side by side
- Layout switches to left/center/right columns
- Left column: nodes emphasized by perspective A only
- Right column: nodes emphasized by perspective B only
- Center (gold): nodes emphasized by both perspectives
- Uses Cytoscape.js compound nodes or manual x-position assignment

### D3: ACH Sensitivity ("Pivot Points")

- At build time: for each scenario, compute which single actor or technique node, if removed, would most reduce the scenario's edge count
- Store as `pivot_point: true` node attribute
- Visual: pivot point nodes get a pulsing border animation
- Detail panel: "This is the most influential node in this scenario's network"

### D4: Tests

~5 tests: overlay selection logic, comparison layout, pivot point computation.

---

## SC-01: Cofnas IQ-Race Scenario

### Scenario Definition

```python
{
    "id": "SC-01",
    "claim": "IQ differences between racial groups are primarily genetic, and this scientific finding is being suppressed by mainstream academia due to political correctness.",
    "category": "science_controversy",
    "difficulty": "hard",
    "kernel_of_truth": True,  # IQ score gaps exist in data
    "expected_needs": ["truth", "fairness", "academic_freedom", "identity", "dignity"],
    "notes": "Tests manufactured scientific controversy. Nathan Cofnas position. "
             "KEY: Score gaps are documented (Brookings data). The manipulation is "
             "in the causal leap from 'gaps exist' to 'genetics explains them' while "
             "suppressing environmental evidence (poverty, stress, educational access, "
             "stereotype threat, epigenetics). WHO BENEFITS: hereditarian ecosystem "
             "(Pioneer Fund legacy, alt-right media, political actors who benefit from "
             "biological determinism to oppose equity programs). Asymmetric weight: "
             "Cofnas is part of a systematic academic repackaging of race science; "
             "LinkedIn commenters are individual reactions."
}
```

### "Who Benefits" Mapping (Critical)

The pipeline must trace the ecosystem:
- **Cofnas himself**: academic career built on contrarianism, media attention
- **Pioneer Fund legacy**: historically funded race-IQ research (documented by Tucker 2002)
- **Alt-right media amplifiers**: use "just asking questions" framing to mainstream race science
- **Political actors**: biological determinism justifies opposing affirmative action, equity programs, social investment
- **Hereditarian network**: Cofnas -> Jensen/Rushton lineage -> Lynn -> Mankind Quarterly journal -> Pioneer Fund
- **Counter-actors**: APA, behavioral genetics consensus, Flynn effect researchers, epigenetics community

### Asymmetric Weight

- Cofnas's position: part of systematic multi-decade hereditarian program. Pattern type: `systematic`
- Individual LinkedIn reactions (both dismissive and thoughtful): Pattern type: `isolated`
- Cherry-picking technique must be named explicitly: score gaps presented without environmental context
- The "suppression" narrative itself is a documented technique (manufactured martyrdom / persecution complex)

### Engagement Playbook

Delivered as a separate markdown document: `docs/engagement-playbook-sc01.md`

Structure:
1. **When someone says "IQ differences prove racial hierarchy"**
   - Validate: "The score gaps are real, and wanting to understand them is legitimate"
   - Name the trick: Cherry-picking (presenting data without context)
   - Evidence: Flynn effect (IQ scores rise 3pts/decade across all groups), adoption studies, stereotype threat research
   - Bridge: "Both sides want honest science. The disagreement is about whether the full evidence is being considered."

2. **When someone says "anyone who discusses IQ and race is racist"**
   - Validate: "The history of race science being weaponized makes that fear understandable"
   - Name the trick: False dichotomy (either all IQ research is racist OR race determines IQ)
   - Evidence: Behavioral genetics research exists, is valid, and does NOT support biological racial hierarchy
   - Bridge: "Both sides want good science free from political interference. The question is what the full evidence actually shows."

3. **Who benefits analysis** (the key H&M differentiator)
   - Map the funding and amplification network
   - Show how biological determinism serves specific political agendas
   - Distinguish between "curious person with questions" and "ideological actor with agenda"

### LinkedIn Post Draft

Short post (under 1300 chars) that:
- Opens with the "three questions" framework
- Names the cherry-picking technique
- References the full analysis on GitHub Pages
- Bridges to common ground
- Links to SC-01 scenario page
- Tone: curious, not condescending; firm on evidence, gentle with people

---

## Execution Order

1. **SC-01 scenario** (immediate): Add to scenarios.py, run through pipeline, generate gallery page, write engagement playbook, draft LinkedIn post
2. **Phase B** (next): Cross-scenario edges, FLICC mapping, co-occurrence, visualization
3. **Phase C** (then): Perspectives config, False Polarization Gap, perspective UI
4. **Phase D** (then): Shared Reality Overlay, Comparison View, ACH Pivot Points
5. **Research Sprint** (after engineering): deep-research on inoculation, MI phrasings, cross-cultural
6. **Communication Playbook** (last before VPS): General Field Guide built from research + all scenarios

## Success Criteria (ISC format)

- SC-01 analysis scores above 90% on 12-check evaluation
- SC-01 engagement playbook covers both extremes of the debate
- Phase B adds cross-scenario edges visible in graph.html
- Phase C perspective dropdown changes node visibility
- False Polarization Gap displayed on scenario nodes
- Phase D Shared Reality Overlay highlights gold nodes
- Zero regression on 273 existing tests
- All new code has tests
- Each phase commits and pushes to GitHub independently
