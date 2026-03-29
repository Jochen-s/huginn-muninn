# Knowledge Graph Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract entities from 29 JSON result files into a NetworkX graph using the POLE-Extended schema, export as Cytoscape.js JSON, and render an interactive cross-scenario knowledge graph in the gallery.

**Architecture:** Python build script reads JSON results, constructs a NetworkX graph with typed nodes (Scenario, Actor, Technique, Claim, Mutation, TemporalEra) and typed edges (contains, features, uses, reveals, relates_to), deduplicates cross-scenario entities (same actor/technique across scenarios), exports via `nx.cytoscape_data()`, and a new `graph.html` gallery page renders it with Cytoscape.js.

**Tech Stack:** Python 3.12+, NetworkX 3.x, Node.js (gallery build.js extension), Cytoscape.js 3.x (CDN)

---

## Phase A: Entity Extraction + Graph Construction

### Task 1: Create graph builder module with schema constants

**Files:**
- Create: `graph/build_graph.py`
- Create: `graph/__init__.py`
- Test: `tests/test_graph_builder.py`

**Step 1: Write the failing test for node type constants**

```python
# tests/test_graph_builder.py
"""Tests for the knowledge graph builder."""
import json
from pathlib import Path

import pytest

from graph.build_graph import NODE_TYPES, EDGE_TYPES


def test_node_types_defined():
    expected = {"scenario", "actor", "technique", "technique_reveal", "claim", "mutation", "temporal_era"}
    assert set(NODE_TYPES) == expected


def test_edge_types_defined():
    expected = {
        "contains", "features", "uses", "reveals",
        "relates_to", "mutates_to", "spans_era",
    }
    assert set(EDGE_TYPES) == expected
```

**Step 2: Run test to verify it fails**

Run: `cd C:/LocalAgent/Products/huginn_muninn && python -m pytest tests/test_graph_builder.py::test_node_types_defined -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write minimal implementation**

```python
# graph/__init__.py
# (empty)

# graph/build_graph.py
"""
Huginn & Muninn Knowledge Graph Builder

Extracts entities from pipeline JSON results into a NetworkX graph.
Exports Cytoscape.js-compatible JSON for the gallery.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

NODE_TYPES = [
    "scenario",
    "actor",
    "technique",
    "technique_reveal",
    "claim",
    "mutation",
    "temporal_era",
]

EDGE_TYPES = [
    "contains",
    "features",
    "uses",
    "reveals",
    "relates_to",
    "mutates_to",
    "spans_era",
]

RESULTS_DIR = Path(__file__).resolve().parent.parent / "tests" / "results"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "gallery" / "dist"
```

**Step 4: Run test to verify it passes**

Run: `cd C:/LocalAgent/Products/huginn_muninn && python -m pytest tests/test_graph_builder.py -v`
Expected: 2 PASS

**Step 5: Commit**

```bash
git add graph/__init__.py graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): scaffold graph builder with schema constants"
```

---

### Task 2: Implement JSON loader with version selection

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_load_results_returns_highest_version_per_scenario(tmp_path):
    """Loader picks highest version when multiple exist for same scenario."""
    from graph.build_graph import load_results

    r1 = {"scenario_id": "HS-01", "version": "v2", "claim": "test claim"}
    r2 = {"scenario_id": "HS-01", "version": "v4", "claim": "test claim v4"}
    (tmp_path / "HS-01-opus-v2.json").write_text(json.dumps(r1))
    (tmp_path / "HS-01-opus-v4.json").write_text(json.dumps(r2))

    results = load_results(tmp_path)
    assert len(results) == 1
    assert results[0]["version"] == "v4"


def test_load_results_skips_non_json(tmp_path):
    from graph.build_graph import load_results

    (tmp_path / "SUMMARY.md").write_text("# Summary")
    r1 = {"scenario_id": "TC-01", "version": "v2", "claim": "test"}
    (tmp_path / "TC-01-opus-v2.json").write_text(json.dumps(r1))

    results = load_results(tmp_path)
    assert len(results) == 1
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_load_results_returns_highest_version_per_scenario -v`
Expected: FAIL with ImportError

**Step 3: Write minimal implementation**

```python
def _parse_version(filename: str) -> int:
    """Extract version number from filename like 'HS-01-opus-v4.json'."""
    name = Path(filename).stem
    for part in reversed(name.split("-")):
        if part.startswith("v") and part[1:].isdigit():
            return int(part[1:])
    return 0


def load_results(results_dir: Path | None = None) -> list[dict]:
    """Load JSON results, keeping only highest version per scenario_id."""
    results_dir = results_dir or RESULTS_DIR
    best: dict[str, tuple[int, dict]] = {}

    for fp in sorted(results_dir.glob("*.json")):
        with open(fp) as f:
            data = json.load(f)
        sid = data.get("scenario_id", "")
        ver = _parse_version(fp.name)
        if sid not in best or ver > best[sid][0]:
            best[sid] = (ver, data)

    return [entry for _, entry in sorted(best.values(), key=lambda x: x[1].get("scenario_id", ""))]
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): JSON loader with version selection"
```

---

### Task 3: Extract Scenario nodes

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_scenario_nodes():
    from graph.build_graph import build_graph

    results = [{
        "scenario_id": "HS-01",
        "version": "v5",
        "claim": "Chemtrails are real",
        "model": "claude-opus-4-6",
        "decomposition": {"sub_claims": [], "original_claim": "Chemtrails", "complexity": "simple"},
        "origins": {"origins": [], "mutations": [], "temporal_context": []},
        "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
        "ttps": {"ttp_matches": [], "primary_tactic": "Execute"},
        "bridge": {
            "universal_needs": ["safety"],
            "issue_overlap": "",
            "narrative_deconstruction": "",
            "perception_gap": "",
            "moral_foundations": {},
            "reframe": "",
            "socratic_dialogue": ["Q1"],
            "techniques_revealed": [],
        },
        "audit": {"verdict": "pass", "findings": [], "confidence_adjustment": 0, "summary": ""},
        "overall_confidence": 0.85,
    }]

    G = build_graph(results)
    assert G.has_node("scenario:HS-01")
    node = G.nodes["scenario:HS-01"]
    assert node["node_type"] == "scenario"
    assert node["label"] == "HS-01"
    assert node["claim"] == "Chemtrails are real"
    assert node["version"] == "v5"
    assert node["confidence"] == 0.85
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_scenario_nodes -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
CATEGORY_BY_PREFIX = {
    "HS": "Health & Science",
    "GP": "Geopolitics",
    "EN": "Environment",
    "EV": "Events",
    "TC": "Technology",
    "MD": "Media",
}


def _category(scenario_id: str) -> str:
    prefix = scenario_id.split("-")[0]
    return CATEGORY_BY_PREFIX.get(prefix, "Unknown")


def build_graph(results: list[dict]) -> nx.DiGraph:
    """Build a NetworkX directed graph from pipeline results."""
    G = nx.DiGraph()

    for r in results:
        sid = r["scenario_id"]
        _add_scenario(G, r, sid)

    return G


def _add_scenario(G: nx.DiGraph, r: dict, sid: str) -> None:
    G.add_node(f"scenario:{sid}", **{
        "node_type": "scenario",
        "label": sid,
        "claim": r.get("claim", ""),
        "version": r.get("version", ""),
        "model": r.get("model", ""),
        "category": _category(sid),
        "confidence": r.get("overall_confidence", 0),
        "complexity": r.get("decomposition", {}).get("complexity", ""),
    })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 5 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Scenario nodes"
```

---

### Task 4: Extract Actor nodes with cross-scenario deduplication

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def _minimal_result(sid, actors=None, relations=None, **overrides):
    """Helper to build a minimal valid result dict."""
    r = {
        "scenario_id": sid,
        "version": "v5",
        "claim": f"Claim for {sid}",
        "model": "claude-opus-4-6",
        "decomposition": {"sub_claims": [], "original_claim": "", "complexity": "simple"},
        "origins": {"origins": [], "mutations": [], "temporal_context": []},
        "intelligence": {
            "actors": actors or [],
            "relations": relations or [],
            "narrative_summary": "",
        },
        "ttps": {"ttp_matches": [], "primary_tactic": "Execute"},
        "bridge": {
            "universal_needs": ["safety"],
            "issue_overlap": "",
            "narrative_deconstruction": "",
            "perception_gap": "",
            "moral_foundations": {},
            "reframe": "",
            "socratic_dialogue": ["Q1"],
            "techniques_revealed": [],
        },
        "audit": {"verdict": "pass", "findings": [], "confidence_adjustment": 0, "summary": ""},
        "overall_confidence": 0.85,
    }
    r.update(overrides)
    return r


def test_extract_actor_nodes():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01", actors=[
        {"name": "Fossil Fuel Industry", "type": "organization", "motivation": "Profit", "credibility": 0.2, "evidence": "Documented"},
    ])]

    G = build_graph(results)
    actor_id = "actor:fossil-fuel-industry"
    assert G.has_node(actor_id)
    node = G.nodes[actor_id]
    assert node["node_type"] == "actor"
    assert node["actor_type"] == "organization"
    assert G.has_edge("scenario:GP-01", actor_id)
    edge = G.edges["scenario:GP-01", actor_id]
    assert edge["edge_type"] == "features"


def test_actor_deduplication_across_scenarios():
    from graph.build_graph import build_graph

    actor = {"name": "Fossil Fuel Industry", "type": "organization", "motivation": "Profit", "credibility": 0.3, "evidence": ""}
    results = [
        _minimal_result("GP-01", actors=[actor]),
        _minimal_result("EN-01", actors=[actor]),
    ]

    G = build_graph(results)
    actor_id = "actor:fossil-fuel-industry"
    assert G.has_node(actor_id)
    assert G.has_edge("scenario:GP-01", actor_id)
    assert G.has_edge("scenario:EN-01", actor_id)
    assert set(G.nodes[actor_id]["scenarios"]) == {"GP-01", "EN-01"}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_actor_nodes -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
import re


def _slugify(name: str) -> str:
    """Convert a name to a URL-safe slug for node IDs."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _add_actors(G: nx.DiGraph, r: dict, sid: str) -> None:
    actors = r.get("intelligence", {}).get("actors", [])
    for actor in actors:
        name = actor.get("name", "")
        if not name:
            continue
        aid = f"actor:{_slugify(name)}"

        if G.has_node(aid):
            G.nodes[aid]["scenarios"].append(sid)
            G.nodes[aid]["credibility"] = max(
                G.nodes[aid]["credibility"],
                actor.get("credibility", 0),
            )
        else:
            G.add_node(aid, **{
                "node_type": "actor",
                "label": name,
                "actor_type": actor.get("type", "unknown"),
                "motivation": actor.get("motivation", ""),
                "credibility": actor.get("credibility", 0),
                "scenarios": [sid],
            })

        G.add_edge(f"scenario:{sid}", aid, edge_type="features", label="features")
```

Then update `build_graph` to call `_add_actors(G, r, sid)` after `_add_scenario`.

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 7 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Actor nodes with cross-scenario dedup"
```

---

### Task 5: Extract Actor-to-Actor relationship edges

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_actor_relations():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-06", actors=[
        {"name": "Farage", "type": "influencer", "motivation": "Power", "credibility": 0.15, "evidence": ""},
        {"name": "GB News", "type": "media", "motivation": "Commercial", "credibility": 0.2, "evidence": ""},
    ], relations=[
        {"source_actor": "Farage", "target_actor": "GB News", "relation_type": "amplifies", "confidence": 0.95},
        {"source_actor": "GB News", "target_actor": "Farage", "relation_type": "amplifies", "confidence": 0.95},
    ])]

    G = build_graph(results)
    farage_id = "actor:farage"
    gb_id = "actor:gb-news"
    assert G.has_edge(farage_id, gb_id)
    assert G.edges[farage_id, gb_id]["edge_type"] == "relates_to"
    assert G.edges[farage_id, gb_id]["relation"] == "amplifies"
    assert G.edges[farage_id, gb_id]["confidence"] == 0.95
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_actor_relations -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def _add_actor_relations(G: nx.DiGraph, r: dict, sid: str) -> None:
    relations = r.get("intelligence", {}).get("relations", [])
    for rel in relations:
        src = f"actor:{_slugify(rel.get('source_actor', ''))}"
        tgt = f"actor:{_slugify(rel.get('target_actor', ''))}"
        if not G.has_node(src) or not G.has_node(tgt):
            continue
        rel_type = rel.get("relation_type", "unknown")
        conf = rel.get("confidence", 0)

        if G.has_edge(src, tgt):
            existing = G.edges[src, tgt]
            if conf > existing.get("confidence", 0):
                existing["confidence"] = conf
            if sid not in existing.get("scenarios", []):
                existing["scenarios"].append(sid)
        else:
            G.add_edge(src, tgt, **{
                "edge_type": "relates_to",
                "relation": rel_type,
                "confidence": conf,
                "scenarios": [sid],
                "label": rel_type,
            })
```

Then update `build_graph` to call `_add_actor_relations(G, r, sid)` after `_add_actors`.

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 8 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Actor-to-Actor relation edges"
```

---

### Task 6: Extract Technique nodes (DISARM TTPs)

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_technique_nodes():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["ttps"] = {
        "ttp_matches": [
            {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9, "evidence": "Documented"},
        ],
        "primary_tactic": "Execute",
    }

    G = build_graph(results)
    tid = "technique:T0023"
    assert G.has_node(tid)
    assert G.nodes[tid]["label"] == "Distort Facts"
    assert G.nodes[tid]["disarm_id"] == "T0023"
    assert G.has_edge("scenario:GP-01", tid)
    assert G.edges["scenario:GP-01", tid]["edge_type"] == "uses"


def test_technique_dedup_across_scenarios():
    from graph.build_graph import build_graph

    ttp = {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9, "evidence": ""}
    results = [
        _minimal_result("GP-01"),
        _minimal_result("HS-02"),
    ]
    results[0]["ttps"] = {"ttp_matches": [ttp], "primary_tactic": "Execute"}
    results[1]["ttps"] = {"ttp_matches": [ttp], "primary_tactic": "Execute"}

    G = build_graph(results)
    tid = "technique:T0023"
    assert set(G.nodes[tid]["scenarios"]) == {"GP-01", "HS-02"}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_technique_nodes -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def _add_techniques(G: nx.DiGraph, r: dict, sid: str) -> None:
    ttps = r.get("ttps", {}).get("ttp_matches", [])
    for ttp in ttps:
        disarm_id = ttp.get("disarm_id", "")
        if not disarm_id:
            continue
        tid = f"technique:{disarm_id}"

        if G.has_node(tid):
            G.nodes[tid]["scenarios"].append(sid)
            G.nodes[tid]["max_confidence"] = max(
                G.nodes[tid]["max_confidence"],
                ttp.get("confidence", 0),
            )
        else:
            G.add_node(tid, **{
                "node_type": "technique",
                "label": ttp.get("technique_name", disarm_id),
                "disarm_id": disarm_id,
                "max_confidence": ttp.get("confidence", 0),
                "scenarios": [sid],
            })

        G.add_edge(f"scenario:{sid}", tid, **{
            "edge_type": "uses",
            "confidence": ttp.get("confidence", 0),
            "label": "uses",
        })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 10 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Technique nodes (DISARM TTPs) with cross-scenario dedup"
```

---

### Task 7: Extract TechniqueReveal nodes (v5 Name the Trick)

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_technique_reveals():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-06")]
    results[0]["bridge"]["techniques_revealed"] = [
        {
            "technique": "Scapegoating",
            "how_it_works": "Takes a real problem...",
            "used_by": "Farage",
            "where_used_here": "Across three parties",
            "historical_precedent": "Dreyfus Affair",
            "pattern_type": "systematic",
        },
    ]

    G = build_graph(results)
    trid = "reveal:scapegoating"
    assert G.has_node(trid)
    node = G.nodes[trid]
    assert node["node_type"] == "technique_reveal"
    assert node["pattern_type"] == "systematic"
    assert node["label"] == "Scapegoating"
    assert G.has_edge("scenario:GP-06", trid)
    assert G.edges["scenario:GP-06", trid]["edge_type"] == "reveals"


def test_technique_reveal_dedup():
    from graph.build_graph import build_graph

    reveal = {
        "technique": "Emotional Amplification",
        "how_it_works": "Escalates emotional register",
        "used_by": "Various",
        "where_used_here": "In framing",
        "pattern_type": "repeated",
    }
    results = [
        _minimal_result("GP-06"),
        _minimal_result("HS-01"),
    ]
    results[0]["bridge"]["techniques_revealed"] = [reveal]
    results[1]["bridge"]["techniques_revealed"] = [reveal]

    G = build_graph(results)
    trid = "reveal:emotional-amplification"
    assert set(G.nodes[trid]["scenarios"]) == {"GP-06", "HS-01"}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_technique_reveals -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
_PATTERN_SEVERITY = {"isolated": 0, "repeated": 1, "systematic": 2}


def _add_technique_reveals(G: nx.DiGraph, r: dict, sid: str) -> None:
    reveals = r.get("bridge", {}).get("techniques_revealed", [])
    for rev in reveals:
        name = rev.get("technique", "")
        if not name:
            continue
        trid = f"reveal:{_slugify(name)}"
        pt = rev.get("pattern_type", "isolated")

        if G.has_node(trid):
            G.nodes[trid]["scenarios"].append(sid)
            existing_sev = _PATTERN_SEVERITY.get(G.nodes[trid]["pattern_type"], 0)
            new_sev = _PATTERN_SEVERITY.get(pt, 0)
            if new_sev > existing_sev:
                G.nodes[trid]["pattern_type"] = pt
        else:
            G.add_node(trid, **{
                "node_type": "technique_reveal",
                "label": name,
                "how_it_works": rev.get("how_it_works", ""),
                "pattern_type": pt,
                "historical_precedent": rev.get("historical_precedent", ""),
                "scenarios": [sid],
            })

        G.add_edge(f"scenario:{sid}", trid, **{
            "edge_type": "reveals",
            "used_by": rev.get("used_by", ""),
            "pattern_type": pt,
            "label": "reveals",
        })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 12 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract TechniqueReveal nodes (Name the Trick)"
```

---

### Task 8: Extract Mutation nodes (narrative evolution)

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_mutations():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-06")]
    results[0]["origins"]["mutations"] = [
        {
            "original": "Anti-EU immigration messaging (2013-2016)",
            "mutated": "Anti-Channel-crossing messaging (2020-2024)",
            "mutation_type": "ideological_migration",
            "source": "Core rhetorical structure preserved",
        },
    ]

    G = build_graph(results)
    mutation_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "mutation"]
    assert len(mutation_nodes) == 1
    node = G.nodes[mutation_nodes[0]]
    assert node["mutation_type"] == "ideological_migration"
    assert G.has_edge("scenario:GP-06", mutation_nodes[0])
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_mutations -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
import hashlib


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:8]


def _add_mutations(G: nx.DiGraph, r: dict, sid: str) -> None:
    mutations = r.get("origins", {}).get("mutations", [])
    for mut in mutations:
        original = mut.get("original", "")
        mutated = mut.get("mutated", "")
        if not original or not mutated:
            continue
        mid = f"mutation:{_short_hash(original + mutated)}"

        if not G.has_node(mid):
            G.add_node(mid, **{
                "node_type": "mutation",
                "label": mut.get("mutation_type", "unknown"),
                "original": original[:120],
                "mutated": mutated[:120],
                "mutation_type": mut.get("mutation_type", "unknown"),
                "scenarios": [sid],
            })
        else:
            if sid not in G.nodes[mid]["scenarios"]:
                G.nodes[mid]["scenarios"].append(sid)

        G.add_edge(f"scenario:{sid}", mid, **{
            "edge_type": "mutates_to",
            "mutation_type": mut.get("mutation_type", "unknown"),
            "label": mut.get("mutation_type", "mutation"),
        })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 13 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Mutation nodes (narrative evolution)"
```

---

### Task 9: Extract Claim nodes (sub-claims)

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_claims():
    from graph.build_graph import build_graph

    results = [_minimal_result("HS-01")]
    results[0]["decomposition"]["sub_claims"] = [
        {"text": "Chemtrails contain barium", "type": "factual", "verifiable": True},
        {"text": "Government is hiding the truth", "type": "opinion", "verifiable": False},
    ]

    G = build_graph(results)
    claim_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "claim"]
    assert len(claim_nodes) == 2
    for cn in claim_nodes:
        assert G.has_edge("scenario:HS-01", cn)
        assert G.edges["scenario:HS-01", cn]["edge_type"] == "contains"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_claims -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def _add_claims(G: nx.DiGraph, r: dict, sid: str) -> None:
    sub_claims = r.get("decomposition", {}).get("sub_claims", [])
    for i, sc in enumerate(sub_claims):
        text = sc.get("text", "")
        if not text:
            continue
        cid = f"claim:{sid}-{i}"

        G.add_node(cid, **{
            "node_type": "claim",
            "label": text[:80],
            "full_text": text,
            "claim_type": sc.get("type", "unknown"),
            "verifiable": sc.get("verifiable", False),
            "scenario": sid,
        })

        G.add_edge(f"scenario:{sid}", cid, **{
            "edge_type": "contains",
            "label": "contains",
        })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 14 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract Claim nodes (sub-claims)"
```

---

### Task 10: Extract TemporalEra nodes

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_extract_temporal_eras():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-06")]
    results[0]["origins"]["temporal_context"] = [
        {
            "era": "UKIP Rise (2006-2016)",
            "date_range": "2006 to 2016",
            "dominant_framing": "Anti-EU",
            "key_actors": ["Farage", "UKIP"],
            "power_context": "Financial crisis",
            "irony_or_inversion": "Most Leave areas had lowest immigration",
        },
    ]

    G = build_graph(results)
    era_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "temporal_era"]
    assert len(era_nodes) == 1
    node = G.nodes[era_nodes[0]]
    assert node["date_range"] == "2006 to 2016"
    assert G.has_edge("scenario:GP-06", era_nodes[0])
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_extract_temporal_eras -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def _add_temporal_eras(G: nx.DiGraph, r: dict, sid: str) -> None:
    eras = r.get("origins", {}).get("temporal_context", [])
    for era in eras:
        era_name = era.get("era", "")
        if not era_name:
            continue
        eid = f"era:{_slugify(era_name)}"

        if not G.has_node(eid):
            G.add_node(eid, **{
                "node_type": "temporal_era",
                "label": era_name,
                "date_range": era.get("date_range", ""),
                "dominant_framing": era.get("dominant_framing", "")[:200],
                "scenarios": [sid],
            })
        else:
            if sid not in G.nodes[eid]["scenarios"]:
                G.nodes[eid]["scenarios"].append(sid)

        G.add_edge(f"scenario:{sid}", eid, **{
            "edge_type": "spans_era",
            "label": "spans",
        })
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 15 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): extract TemporalEra nodes"
```

---

### Task 11: Graph statistics and Cytoscape.js JSON export

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_graph_stats():
    from graph.build_graph import build_graph, graph_stats

    results = [_minimal_result("GP-01", actors=[
        {"name": "Actor A", "type": "influencer", "motivation": "", "credibility": 0.5, "evidence": ""},
    ])]

    G = build_graph(results)
    stats = graph_stats(G)
    assert stats["total_nodes"] >= 2
    assert stats["total_edges"] >= 1
    assert stats["node_types"]["scenario"] == 1
    assert stats["node_types"]["actor"] == 1


def test_export_cytoscape_json():
    from graph.build_graph import build_graph, export_cytoscape

    results = [_minimal_result("GP-01", actors=[
        {"name": "Actor A", "type": "influencer", "motivation": "", "credibility": 0.5, "evidence": ""},
    ])]

    G = build_graph(results)
    cy_data = export_cytoscape(G)
    assert "elements" in cy_data
    assert "nodes" in cy_data["elements"]
    assert "edges" in cy_data["elements"]
    assert len(cy_data["elements"]["nodes"]) >= 2
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_graph_stats -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
from collections import Counter


def graph_stats(G: nx.DiGraph) -> dict:
    """Return summary statistics for the graph."""
    node_types = Counter(d.get("node_type", "unknown") for _, d in G.nodes(data=True))
    edge_types = Counter(d.get("edge_type", "unknown") for _, _, d in G.edges(data=True))
    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "node_types": dict(node_types),
        "edge_types": dict(edge_types),
    }


def export_cytoscape(G: nx.DiGraph) -> dict:
    """Export graph to Cytoscape.js-compatible JSON."""
    return nx.cytoscape_data(G)
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 17 PASS

**Step 5: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): graph statistics and Cytoscape.js JSON export"
```

---

### Task 12: CLI entry point and full pipeline integration test

**Files:**
- Modify: `graph/build_graph.py`
- Modify: `tests/test_graph_builder.py`

**Step 1: Write the failing test**

```python
def test_full_pipeline_with_real_results():
    """Integration test: build graph from actual result files."""
    from graph.build_graph import build_graph, export_cytoscape, graph_stats, load_results

    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        pytest.skip("No results directory")

    results = load_results(results_dir)
    assert len(results) >= 20

    G = build_graph(results)
    stats = graph_stats(G)

    assert stats["node_types"]["scenario"] >= 20
    assert stats["node_types"]["actor"] >= 10
    assert stats["node_types"]["technique"] >= 5
    assert stats["total_edges"] >= 50

    multi_scenario_actors = [
        n for n, d in G.nodes(data=True)
        if d.get("node_type") == "actor" and len(d.get("scenarios", [])) > 1
    ]
    assert len(multi_scenario_actors) >= 1, "Expected cross-scenario actor dedup"

    cy = export_cytoscape(G)
    assert len(cy["elements"]["nodes"]) == stats["total_nodes"]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_builder.py::test_full_pipeline_with_real_results -v`
Expected: FAIL (no CLI entry point yet, but test should pass if build_graph works)

**Step 3: Write CLI entry point**

Add to `graph/build_graph.py`:

```python
def main() -> None:
    """Build the knowledge graph and export to Cytoscape.js JSON."""
    print("Huginn & Muninn Knowledge Graph Builder")
    print("=" * 40)

    results = load_results()
    print(f"Loaded {len(results)} scenarios (highest version per ID)")

    G = build_graph(results)
    stats = graph_stats(G)
    print(f"\nGraph Statistics:")
    for nt, count in sorted(stats["node_types"].items()):
        print(f"  {nt}: {count} nodes")
    print(f"  Total: {stats['total_nodes']} nodes, {stats['total_edges']} edges")

    cy_data = export_cytoscape(G)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "graph-data.json"
    with open(out_path, "w") as f:
        json.dump(cy_data, f, indent=2)
    size_kb = out_path.stat().st_size / 1024
    print(f"\nExported: {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_graph_builder.py -v`
Expected: 18 PASS

**Step 5: Run the builder against real data**

Run: `cd C:/LocalAgent/Products/huginn_muninn && python graph/build_graph.py`
Expected: Prints graph stats, exports graph-data.json to gallery/dist/

**Step 6: Commit**

```bash
git add graph/build_graph.py tests/test_graph_builder.py
git commit -m "feat(graph): CLI entry point and full pipeline integration test"
```

---

### Task 13: Verify zero regression on existing tests

**Step 1: Run all existing tests**

Run: `cd C:/LocalAgent/Products/huginn_muninn && python -m pytest tests/ -v --timeout=30 -x`
Expected: All existing tests pass (56+ existing + 18 new graph tests)

**Step 2: If any failures, fix without modifying existing test files**

The graph module is entirely additive (new files only). No existing code should be affected.

---

## Phase D: Cytoscape.js Visualization

### Task 14: Generate graph.html page in gallery build

**Files:**
- Modify: `gallery/build.js`

**Step 1: Add graph page generation to build.js main()**

After the scenario page loop in `main()`, add graph page generation call.

**Step 2: Implement buildGraphPage() function**

The function generates a complete HTML page with:
- Header matching existing gallery style (site-header, site-nav)
- Graph stats cards (scenarios, actors, cross-scenario actors, techniques, connections)
- Filter controls (node type dropdown, category dropdown, search input)
- Color legend (navy=Scenario, red=Actor, teal=Technique, purple=Named Trick, orange=Mutation, blue=Era)
- Cytoscape.js container (600px height)
- Node detail panel (shown on click)
- Cytoscape.js loaded from CDN (unpkg, v3.30.4)
- COSE layout (force-directed) with: idealEdgeLength 120, nodeRepulsion 8000, gravity 0.3
- Node sizing: scenarios 40px, actors 25+8*scenarioCount, techniques 20+6*scenarioCount
- Click handler: highlight neighbors, dim everything else, show detail panel
- Filter logic: type filter (compound options like "scenario+actor"), category filter, text search
- Detail panel: scenario links to scenario page, actor shows all scenarios, technique shows DISARM ID
- All user-supplied text escaped via textContent-based esc() function (XSS-safe)

**Step 3: Run gallery build**

Run: `cd C:/LocalAgent/Products/huginn_muninn && node gallery/build.js`
Expected: graph.html generated alongside existing pages

**Step 4: Commit**

```bash
git add gallery/build.js
git commit -m "feat(graph): Cytoscape.js graph page in gallery"
```

---

### Task 15: Add graph nav link to index and scenario pages

**Files:**
- Modify: `gallery/build.js`

**Step 1: Find the nav section in buildIndex() and buildScenarioPage()**

Search for `site-nav` in build.js. Add a "Knowledge Graph" link next to existing nav links.

**Step 2: Rebuild and verify**

Run: `node gallery/build.js`
Expected: All pages now have "Knowledge Graph" in nav bar

**Step 3: Commit**

```bash
git add gallery/build.js
git commit -m "feat(graph): add Knowledge Graph nav link to all gallery pages"
```

---

### Task 16: Copy gallery to docs/ for GitHub Pages

**Step 1: Copy dist to docs/gallery**

```bash
cd C:/LocalAgent/Products/huginn_muninn
rm -rf docs/gallery
cp -r gallery/dist docs/gallery
```

**Step 2: Verify graph-data.json and graph.html are in docs/gallery/**

Run: `ls docs/gallery/graph*`
Expected: graph.html, graph-data.json

**Step 3: Commit**

```bash
git add docs/gallery/
git commit -m "feat(graph): update GitHub Pages with knowledge graph"
```

---

### Task 17: Final regression test

**Step 1: Run all Python tests**

Run: `cd C:/LocalAgent/Products/huginn_muninn && python -m pytest tests/ -v --timeout=30`
Expected: All tests pass (existing 56 + new ~18 graph tests)

**Step 2: Run gallery build**

Run: `node gallery/build.js`
Expected: 23+ files generated (21 scenarios + index + graph) without errors

**Step 3: Verify graph rendering**

Open graph.html and check:
- Nodes render with correct colors per type
- Click a scenario node: detail panel shows claim, link to scenario page
- Click an actor appearing in multiple scenarios: detail panel lists all scenarios
- Filter by category works (dims unrelated nodes)
- Search filter works
- "Scenarios + Actors" default view shows clean, readable graph

---

## Dependency Map

```
Task 1 (constants) -- Task 2 (loader)
                         |
Task 3 (scenarios) -- Task 4 (actors) -- Task 5 (relations)
                                       |-- Task 6 (techniques)
                                       |-- Task 7 (reveals)
                                       |-- Task 8 (mutations)
                                       |-- Task 9 (claims)
                                       |-- Task 10 (eras)
                                       |
                              Task 11 (stats + export)
                                       |
                              Task 12 (CLI + integration)
                                       |
                              Task 13 (regression check)
                                       |
                              Task 14 (graph.html) -- Task 15 (nav links)
                                                   |-- Task 16 (GitHub Pages)
                                                   |-- Task 17 (final check)
```

## Key Design Decisions

1. **Node IDs use type prefix** (`scenario:HS-01`, `actor:fossil-fuel-industry`). Prevents collisions, enables filtering.
2. **Actor dedup by slugified name**. "Fossil Fuel Industry" in GP-01 and EN-01 becomes one node with `scenarios: ["GP-01", "EN-01"]`.
3. **Technique dedup by DISARM ID** (`T0023`). Technique reveals dedup by slugified technique name.
4. **Claims are NOT deduplicated** across scenarios (each claim is scenario-specific: `claim:HS-01-0`).
5. **Default view is "Scenarios + Actors"** to keep the initial graph readable. Full graph with all node types available via dropdown.
6. **Cytoscape.js loaded from CDN** (unpkg). No build step needed.
7. **Graph data is a separate JSON file** (`graph-data.json`), not embedded in HTML. Keeps graph page lightweight and data cacheable.
8. **No claims in default view** to prevent node explosion. 21 scenarios x ~5 claims each = 100+ claim nodes that add noise. Available via "All node types" filter.
9. **All text sanitized via textContent-based esc()** for XSS safety. No raw data injected into DOM.
