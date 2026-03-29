# Phase B/C/D Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add cross-scenario connections (Phase B), lightweight perspective filtering with False Polarization Gap (Phase C), and advanced visualization modes (Phase D) to the Huginn & Muninn knowledge graph.

**Architecture:** All graph enhancements go in `graph/build_graph.py` as new functions called after the per-scenario extraction loop. Perspective config in `graph/perspectives.json`. All visualization enhancements in the `buildGraphPage()` function of `gallery/build.js`. Tests in `tests/test_graph_builder.py`.

**Tech Stack:** Python 3.12+, NetworkX 3.x, Cytoscape.js 3.30.4

---

## Phase B: Cross-Scenario Connections

### Task 1: FLICC taxonomy mapping for technique nodes

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_flicc_mapping():
    from graph.build_graph import FLICC_MAP, build_graph

    # FLICC_MAP should map DISARM IDs to FLICC categories
    assert "T0023" in FLICC_MAP  # Distort Facts -> Logical fallacies
    assert "T0044" in FLICC_MAP  # Seed distortions -> Cherry picking

    results = [_minimal_result("GP-01")]
    results[0]["ttps"] = {
        "ttp_matches": [
            {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9, "evidence": ""},
        ],
        "primary_tactic": "Execute",
    }

    G = build_graph(results)
    tid = "technique:T0023"
    assert G.nodes[tid].get("flicc_category") is not None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_flicc_mapping -v`

**Step 3: Implement FLICC_MAP and add flicc_category to technique nodes**

Add to `graph/build_graph.py` after `_PATTERN_SEVERITY`:

```python
FLICC_MAP: dict[str, str] = {
    "T0010": "Fake experts",
    "T0022": "Conspiracy theories",
    "T0023": "Logical fallacies",
    "T0004": "Logical fallacies",
    "T0044": "Cherry picking",
    "T0049": "Cherry picking",
    "T0056": "Logical fallacies",
    "T0016": "Cherry picking",
    "T0048": "Impossible expectations",
}
```

Modify `_add_techniques` to include: `"flicc_category": FLICC_MAP.get(disarm_id, ""),`

**Step 4: Run test, verify pass**

**Step 5: Commit**

```bash
git commit -m "feat(graph): FLICC taxonomy mapping for technique nodes"
```

---

### Task 2: Cross-scenario edges between scenarios sharing actors

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_cross_scenario_edges():
    from graph.build_graph import build_graph

    actor1 = {"name": "Shared Actor", "type": "organization", "motivation": "", "credibility": 0.5, "evidence": ""}
    actor2 = {"name": "Another Shared", "type": "media", "motivation": "", "credibility": 0.5, "evidence": ""}
    results = [
        _minimal_result("GP-01", actors=[actor1, actor2]),
        _minimal_result("HS-01", actors=[actor1, actor2]),
        _minimal_result("EN-01", actors=[actor1]),
    ]

    G = build_graph(results)
    # GP-01 and HS-01 share 2 actors -> should have cross_scenario edge
    assert G.has_edge("scenario:GP-01", "scenario:HS-01")
    edge = G.edges["scenario:GP-01", "scenario:HS-01"]
    assert edge["edge_type"] == "cross_scenario"
    assert edge["weight"] == 2
    assert "Shared Actor" in edge["shared_actors"]

    # GP-01 and EN-01 share only 1 actor -> no edge (threshold is 2)
    assert not G.has_edge("scenario:GP-01", "scenario:EN-01")
```

**Step 2: Run test to verify it fails**

**Step 3: Implement `_add_cross_scenario_edges`**

```python
from itertools import combinations

def _add_cross_scenario_edges(G: nx.DiGraph) -> None:
    """Add edges between scenarios that share 2+ actors."""
    scenario_actors: dict[str, set[str]] = {}
    for node_id, data in G.nodes(data=True):
        if data.get("node_type") == "actor":
            for sid in data.get("scenarios", []):
                scenario_actors.setdefault(sid, set()).add(data.get("label", ""))

    for (s1, actors1), (s2, actors2) in combinations(scenario_actors.items(), 2):
        shared = actors1 & actors2
        if len(shared) >= 2:
            G.add_edge(f"scenario:{s1}", f"scenario:{s2}", **{
                "edge_type": "cross_scenario",
                "shared_actors": sorted(shared),
                "weight": len(shared),
                "label": f"{len(shared)} shared actors",
            })
```

Add call in `build_graph()` after the for loop: `_add_cross_scenario_edges(G)`

**Step 4: Run test, verify pass**

**Step 5: Commit**

```bash
git commit -m "feat(graph): cross-scenario edges for shared actors"
```

---

### Task 3: Technique co-occurrence edges

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_technique_cooccurrence_edges():
    from graph.build_graph import build_graph

    ttp1 = {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9, "evidence": ""}
    ttp2 = {"disarm_id": "T0056", "technique_name": "Amplify", "confidence": 0.9, "evidence": ""}
    results = [_minimal_result(f"GP-0{i}") for i in range(1, 4)]
    for r in results:
        r["ttps"] = {"ttp_matches": [ttp1, ttp2], "primary_tactic": "Execute"}

    G = build_graph(results)
    # T0023 and T0056 co-occur in 3 scenarios -> co_occurs edge
    assert G.has_edge("technique:T0023", "technique:T0056")
    edge = G.edges["technique:T0023", "technique:T0056"]
    assert edge["edge_type"] == "co_occurs"
    assert edge["weight"] == 3
```

**Step 2: Run test to verify it fails**

**Step 3: Implement `_add_cooccurrence_edges`**

```python
def _add_cooccurrence_edges(G: nx.DiGraph) -> None:
    """Add edges between techniques that co-occur in 3+ scenarios."""
    tech_scenarios: dict[str, set[str]] = {}
    for node_id, data in G.nodes(data=True):
        if data.get("node_type") == "technique":
            tech_scenarios[node_id] = set(data.get("scenarios", []))

    for (t1, s1), (t2, s2) in combinations(tech_scenarios.items(), 2):
        shared = s1 & s2
        if len(shared) >= 3:
            G.add_edge(t1, t2, **{
                "edge_type": "co_occurs",
                "shared_scenarios": sorted(shared),
                "weight": len(shared),
                "label": f"co-occurs ({len(shared)}x)",
            })
```

Add call in `build_graph()` after `_add_cross_scenario_edges(G)`: `_add_cooccurrence_edges(G)`

**Step 4: Run test, verify pass**

**Step 5: Commit**

```bash
git commit -m "feat(graph): technique co-occurrence edges"
```

---

### Task 4: Phase B visualization updates in gallery

**Files:**
- Modify: `gallery/build.js` (buildGraphPage function)

**Step 1: Add "Playbook View" filter option**

In the filter-type select, add:
```html
<option value="scenario+technique">Playbook View (Scenarios + Techniques)</option>
```

**Step 2: Add FLICC color coding**

Add FLICC colors to the JavaScript:
```javascript
var FLICC_COLORS = {
  'Fake experts': '#E74C3C',
  'Logical fallacies': '#3498DB',
  'Impossible expectations': '#E67E22',
  'Cherry picking': '#2ECC71',
  'Conspiracy theories': '#9B59B6'
};
```

Update node style to use FLICC border color for technique nodes:
```javascript
// In initGraph, after creating elements:
// If node has flicc_category, set border color
```

**Step 3: Style cross-scenario edges as dashed**

Add style rule:
```javascript
{
  selector: 'edge[edge_type="cross_scenario"]',
  style: {
    'line-style': 'dashed',
    'line-dash-pattern': [6, 3],
    'width': 'mapData(weight, 2, 10, 2, 6)',
    'line-color': '#E74C3C',
    'target-arrow-color': '#E74C3C'
  }
}
```

**Step 4: Rebuild gallery, verify graph.html**

Run: `node gallery/build.js`

**Step 5: Commit**

```bash
git commit -m "feat(graph): Phase B visualization (playbook view, FLICC colors, cross-scenario edges)"
```

---

### Task 5: Phase B regression test + sync to GitHub

**Step 1: Run all tests**

Run: `python -m pytest tests/test_graph_builder.py tests/test_contracts.py tests/test_orchestrator.py tests/test_agents.py -q`

**Step 2: Rebuild graph + gallery + copy to docs/**

```bash
python graph/build_graph.py
node gallery/build.js
cp gallery/dist/* docs/gallery/
```

**Step 3: Commit and sync to GitHub**

```bash
git add graph/ tests/test_graph_builder.py gallery/build.js docs/gallery/
git commit -m "feat(graph): Phase B complete - cross-scenario connections, FLICC, co-occurrence"
```

Then sync to C:/LocalAgent/github/huginn-muninn and push.

---

## Phase C: Lightweight Perspectives

### Task 6: Create perspectives.json config

**Files:**
- Create: `graph/perspectives.json`
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_load_perspectives():
    from graph.build_graph import load_perspectives

    perspectives = load_perspectives()
    assert len(perspectives) == 4
    assert perspectives[0]["id"] == "scientific_consensus"
    assert "moral_foundations" in perspectives[0]
```

**Step 2: Create perspectives.json and implement load_perspectives()**

Create `graph/perspectives.json`:
```json
[
  {
    "id": "scientific_consensus",
    "name": "Scientific Consensus",
    "description": "View weighted by evidence quality and source tier",
    "emphasis_node_types": ["technique", "claim"],
    "emphasis_fields": ["consensus_explanation"],
    "moral_foundations": {"care": 0.3, "fairness": 0.3, "authority": 0.2, "liberty": 0.2}
  },
  {
    "id": "concerned_citizen",
    "name": "Concerned Citizen",
    "description": "View weighted by personal impact and safety needs",
    "emphasis_node_types": ["actor", "scenario"],
    "emphasis_fields": ["universal_needs", "perception_gap"],
    "moral_foundations": {"care": 0.4, "fairness": 0.2, "loyalty": 0.2, "authority": 0.2}
  },
  {
    "id": "institutional_skeptic",
    "name": "Institutional Skeptic",
    "description": "View highlighting accountability gaps and commercial motives",
    "emphasis_node_types": ["actor"],
    "emphasis_fields": ["commercial_motives", "credibility"],
    "moral_foundations": {"fairness": 0.3, "liberty": 0.3, "authority": 0.2, "care": 0.2}
  },
  {
    "id": "bridge_builder",
    "name": "Bridge Builder",
    "description": "View highlighting shared reality and common ground",
    "emphasis_node_types": ["scenario"],
    "emphasis_fields": ["issue_overlap", "universal_needs", "reframe"],
    "moral_foundations": {"care": 0.3, "fairness": 0.3, "loyalty": 0.2, "liberty": 0.2}
  }
]
```

Add to `graph/build_graph.py`:
```python
def load_perspectives(config_path: Path | None = None) -> list[dict]:
    config_path = config_path or Path(__file__).parent / "perspectives.json"
    with open(config_path) as f:
        return json.load(f)
```

**Step 3: Run test, verify pass**

**Step 4: Commit**

```bash
git commit -m "feat(graph): perspectives.json config with 4 presets"
```

---

### Task 7: False Polarization Gap metric

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_false_polarization_gap():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["bridge"]["moral_foundations"] = {
        "side_a": ["fairness", "loyalty", "authority"],
        "side_b": ["fairness", "care", "liberty"],
        "shared_across_both": ["fairness"],
    }

    G = build_graph(results)
    node = G.nodes["scenario:GP-01"]
    gap = node.get("false_polarization_gap")
    assert gap is not None
    # shared = fairness (1), total unique = fairness, loyalty, authority, care, liberty (5)
    # gap = 1/5 = 0.2
    assert 0.1 <= gap <= 0.3


def test_false_polarization_gap_with_shared_list():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["bridge"]["moral_foundations"] = {
        "side_a": ["fairness", "care"],
        "side_b": ["fairness", "care", "authority"],
        "shared_across_both": ["fairness", "care"],
    }

    G = build_graph(results)
    gap = G.nodes["scenario:GP-01"]["false_polarization_gap"]
    # shared = 2, total = 3, gap = 2/3 = 0.67
    assert 0.5 <= gap <= 0.8
```

**Step 2: Implement `_compute_false_polarization_gap`**

```python
def _compute_false_polarization_gap(bridge: dict) -> float:
    """Compute False Polarization Gap from moral foundations data."""
    mf = bridge.get("moral_foundations", {})
    if not mf:
        return 0.0

    side_a = set()
    side_b = set()
    for item in mf.get("side_a", []):
        foundations = item.split("/")[0].split(":")[0].strip().lower() if isinstance(item, str) else ""
        if foundations:
            side_a.add(foundations)
    for item in mf.get("side_b", []):
        foundations = item.split("/")[0].split(":")[0].strip().lower() if isinstance(item, str) else ""
        if foundations:
            side_b.add(foundations)

    if not side_a and not side_b:
        return 0.0

    shared = side_a & side_b
    total = side_a | side_b
    return len(shared) / len(total) if total else 0.0
```

Call from `_add_scenario` to add as node attribute:
```python
bridge = r.get("bridge", {})
gap = _compute_false_polarization_gap(bridge)
# Add to node: "false_polarization_gap": gap
```

**Step 3: Run test, verify pass**

**Step 4: Commit**

```bash
git commit -m "feat(graph): False Polarization Gap metric on scenario nodes"
```

---

### Task 8: Perspective dropdown in graph.html

**Files:**
- Modify: `gallery/build.js`

**Step 1: Add perspective dropdown to controls**

After the search control:
```html
<div>
  <label for="filter-perspective">Perspective:</label>
  <select id="filter-perspective">
    <option value="all">All perspectives</option>
    <option value="scientific_consensus">Scientific Consensus</option>
    <option value="concerned_citizen">Concerned Citizen</option>
    <option value="institutional_skeptic">Institutional Skeptic</option>
    <option value="bridge_builder">Bridge Builder</option>
  </select>
</div>
```

**Step 2: Implement perspective filtering in JS**

Perspectives change node opacity based on emphasis_node_types.

**Step 3: Add False Polarization Gap badge on scenario nodes**

When Bridge Builder perspective is active, show the gap percentage on scenario detail panel.

**Step 4: Rebuild and verify**

**Step 5: Commit**

```bash
git commit -m "feat(graph): perspective dropdown and False Polarization Gap display"
```

---

### Task 9: Phase C regression + sync

Same pattern as Task 5: run tests, rebuild, copy, commit, sync to GitHub, push.

```bash
git commit -m "feat(graph): Phase C complete - perspectives, False Polarization Gap"
```

---

## Phase D: Advanced Visualization

### Task 10: Shared Reality Overlay

**Files:**
- Modify: `gallery/build.js`

**Step 1: Add "Show Shared Reality" toggle**

```html
<button id="btn-shared-reality" style="...">Show Shared Reality</button>
```

**Step 2: Implement overlay logic**

On click: highlight in gold all scenario nodes where `false_polarization_gap > 0.5`, and all actor nodes with `scenarios.length >= 3`.

```javascript
document.getElementById('btn-shared-reality').addEventListener('click', function() {
  var active = this.classList.toggle('active');
  cy.batch(function() {
    cy.nodes().removeClass('shared-reality');
    if (active) {
      cy.nodes().forEach(function(node) {
        var d = node.data();
        if (d.node_type === 'scenario' && d.false_polarization_gap > 0.5) {
          node.addClass('shared-reality');
        }
        if (d.node_type === 'actor' && (d.scenarios || []).length >= 3) {
          node.addClass('shared-reality');
        }
      });
    }
  });
});
```

Add style:
```javascript
{
  selector: '.shared-reality',
  style: {
    'border-width': 4,
    'border-color': '#F1C40F',
    'background-opacity': 1
  }
}
```

**Step 3: Rebuild and verify**

**Step 4: Commit**

---

### Task 11: ACH Pivot Points

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_pivot_points():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01", actors=[
        {"name": "Central Actor", "type": "organization", "motivation": "", "credibility": 0.3, "evidence": ""},
        {"name": "Minor Actor", "type": "influencer", "motivation": "", "credibility": 0.5, "evidence": ""},
    ], relations=[
        {"source_actor": "Central Actor", "target_actor": "Minor Actor", "relation_type": "funds", "confidence": 0.9},
    ])]
    results[0]["ttps"] = {
        "ttp_matches": [
            {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9, "evidence": ""},
        ],
        "primary_tactic": "Execute",
    }

    G = build_graph(results)
    # Central Actor has more connections -> should be pivot point
    pivot_nodes = [n for n, d in G.nodes(data=True)
                   if d.get("pivot_point") and "GP-01" in d.get("scenarios", [d.get("scenario", "")])]
    assert len(pivot_nodes) >= 1
```

**Step 2: Implement `_compute_pivot_points`**

```python
def _compute_pivot_points(G: nx.DiGraph) -> None:
    """Mark the most influential non-scenario node per scenario as pivot_point."""
    for node_id, data in list(G.nodes(data=True)):
        if data.get("node_type") != "scenario":
            continue
        sid = data.get("label", "")
        neighbors = list(G.neighbors(node_id)) + list(G.predecessors(node_id))
        if not neighbors:
            continue
        # Score each neighbor by its total degree
        best_node = max(neighbors, key=lambda n: G.degree(n))
        G.nodes[best_node]["pivot_point"] = True
        G.nodes[best_node].setdefault("pivot_for", []).append(sid)
```

Call after cross-scenario and co-occurrence edges.

**Step 3: Run test, verify pass**

**Step 4: Add pivot point visual in graph.html**

Pulsing border animation for nodes with `pivot_point: true`:
```css
@keyframes pulse { 0%,100% { border-width: 2px; } 50% { border-width: 5px; } }
```

**Step 5: Commit**

```bash
git commit -m "feat(graph): ACH pivot points with pulsing border"
```

---

### Task 12: Phase D regression + final sync

Run tests, rebuild all, copy to docs/, commit, sync to GitHub, push.

```bash
git commit -m "feat(graph): Phase D complete - Shared Reality, Pivot Points"
```

Note: Comparison View is deferred to Phase C v2 (requires full Perspective graph entities, not just filter presets). The lightweight perspectives in this iteration support the dropdown filter and Shared Reality Overlay, which deliver 80% of the value.

---

## Dependency Map

```
Task 1 (FLICC) ── Task 2 (cross-scenario) ── Task 3 (co-occurrence)
                                                      |
                                              Task 4 (Phase B viz)
                                                      |
                                              Task 5 (Phase B ship)
                                                      |
                              Task 6 (perspectives) ── Task 7 (FPG metric)
                                                      |
                                              Task 8 (Phase C viz)
                                                      |
                                              Task 9 (Phase C ship)
                                                      |
                              Task 10 (Shared Reality) ── Task 11 (Pivot Points)
                                                      |
                                              Task 12 (Phase D ship)
```
