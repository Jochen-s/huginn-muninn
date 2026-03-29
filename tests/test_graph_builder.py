"""Tests for the Huginn & Muninn knowledge graph builder."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from graph.build_graph import EDGE_TYPES, FLICC_MAP, NODE_TYPES


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _minimal_result(sid, actors=None, relations=None, **overrides):
    """Build a minimal valid result dict for use in unit tests."""
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


# ---------------------------------------------------------------------------
# Task 1: Schema constants
# ---------------------------------------------------------------------------

def test_node_types_defined():
    expected = {"scenario", "actor", "technique", "technique_reveal", "claim", "mutation", "temporal_era"}
    assert set(NODE_TYPES) == expected


def test_edge_types_defined():
    expected = {
        "contains", "features", "uses", "reveals",
        "relates_to", "mutates_to", "spans_era",
    }
    assert set(EDGE_TYPES) == expected


# ---------------------------------------------------------------------------
# Task 2: JSON loader
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 3: Scenario nodes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 4: Actor nodes with cross-scenario deduplication
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 5: Actor-to-Actor relation edges
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 6: Technique nodes (DISARM TTPs)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 7: TechniqueReveal nodes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 8: Mutation nodes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 9: Claim nodes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 10: TemporalEra nodes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 11: Graph statistics and Cytoscape.js export
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 12: Full pipeline integration test against real result files
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Phase B: Feature 1 — FLICC taxonomy mapping
# ---------------------------------------------------------------------------

def test_flicc_mapping():
    """FLICC_MAP exists and technique nodes receive flicc_category attribute."""
    from graph.build_graph import build_graph

    assert isinstance(FLICC_MAP, dict)
    assert len(FLICC_MAP) > 0

    results = [_minimal_result("GP-01")]
    results[0]["ttps"] = {
        "ttp_matches": [
            {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9},
            {"disarm_id": "T0099", "technique_name": "Unknown Technique", "confidence": 0.5},
        ],
        "primary_tactic": "Execute",
    }

    G = build_graph(results)
    mapped_node = G.nodes["technique:T0023"]
    unmapped_node = G.nodes["technique:T0099"]

    assert mapped_node["flicc_category"] == FLICC_MAP["T0023"]
    assert unmapped_node["flicc_category"] == ""


# ---------------------------------------------------------------------------
# Phase B: Feature 2 — Cross-scenario edges
# ---------------------------------------------------------------------------

def test_cross_scenario_edges():
    """Two scenarios sharing 2+ actors receive a cross_scenario edge."""
    from graph.build_graph import build_graph

    actor_a = {"name": "Alice", "type": "influencer", "motivation": "", "credibility": 0.5, "evidence": ""}
    actor_b = {"name": "Bob", "type": "media", "motivation": "", "credibility": 0.4, "evidence": ""}
    actor_c = {"name": "Carol", "type": "organization", "motivation": "", "credibility": 0.3, "evidence": ""}

    results = [
        _minimal_result("GP-01", actors=[actor_a, actor_b, actor_c]),
        _minimal_result("GP-02", actors=[actor_a, actor_b]),
        _minimal_result("GP-03", actors=[actor_c]),
    ]

    G = build_graph(results)

    assert G.has_edge("scenario:GP-01", "scenario:GP-02")
    edge = G.edges["scenario:GP-01", "scenario:GP-02"]
    assert edge["edge_type"] == "cross_scenario"

    assert not G.has_edge("scenario:GP-01", "scenario:GP-03")
    assert not G.has_edge("scenario:GP-02", "scenario:GP-03")


def test_cross_scenario_edge_weight():
    """Cross-scenario edge weight equals the number of shared actors."""
    from graph.build_graph import build_graph

    actor_a = {"name": "Alice", "type": "influencer", "motivation": "", "credibility": 0.5, "evidence": ""}
    actor_b = {"name": "Bob", "type": "media", "motivation": "", "credibility": 0.4, "evidence": ""}
    actor_c = {"name": "Carol", "type": "organization", "motivation": "", "credibility": 0.3, "evidence": ""}

    results = [
        _minimal_result("EN-01", actors=[actor_a, actor_b, actor_c]),
        _minimal_result("EN-02", actors=[actor_a, actor_b, actor_c]),
    ]

    G = build_graph(results)

    assert G.has_edge("scenario:EN-01", "scenario:EN-02")
    edge = G.edges["scenario:EN-01", "scenario:EN-02"]
    assert edge["weight"] == 3
    assert sorted(edge["shared_actors"]) == ["Alice", "Bob", "Carol"]


# ---------------------------------------------------------------------------
# Phase B: Feature 3 — Technique co-occurrence edges
# ---------------------------------------------------------------------------

def test_technique_cooccurrence_edges():
    """Two techniques appearing together in 3+ scenarios receive a co_occurs edge."""
    from graph.build_graph import build_graph

    ttp_a = {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9}
    ttp_b = {"disarm_id": "T0044", "technique_name": "Cherry Pick", "confidence": 0.8}

    results = [
        _minimal_result(f"SC-0{i}", **{
            "ttps": {"ttp_matches": [ttp_a, ttp_b], "primary_tactic": "Execute"}
        })
        for i in range(1, 4)
    ]

    G = build_graph(results)

    assert G.has_edge("technique:T0023", "technique:T0044")
    edge = G.edges["technique:T0023", "technique:T0044"]
    assert edge["edge_type"] == "co_occurs"
    assert edge["weight"] == 3
    assert sorted(edge["shared_scenarios"]) == ["SC-01", "SC-02", "SC-03"]


def test_cooccurrence_threshold():
    """Co-occurrence below 3 scenarios produces no co_occurs edge."""
    from graph.build_graph import build_graph

    ttp_a = {"disarm_id": "T0023", "technique_name": "Distort Facts", "confidence": 0.9}
    ttp_b = {"disarm_id": "T0044", "technique_name": "Cherry Pick", "confidence": 0.8}

    results = [
        _minimal_result(f"TC-0{i}", **{
            "ttps": {"ttp_matches": [ttp_a, ttp_b], "primary_tactic": "Execute"}
        })
        for i in range(1, 3)
    ]

    G = build_graph(results)

    assert not G.has_edge("technique:T0023", "technique:T0044")


# ---------------------------------------------------------------------------
# Phase C: Perspectives and False Polarization Gap
# ---------------------------------------------------------------------------


def test_load_perspectives():
    from graph.build_graph import load_perspectives

    perspectives = load_perspectives()
    assert len(perspectives) == 4
    assert perspectives[0]["id"] == "scientific_consensus"
    assert "moral_foundations" in perspectives[0]
    assert "emphasis_node_types" in perspectives[0]


def test_false_polarization_gap():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["bridge"]["moral_foundations"] = {
        "side_a": ["fairness", "loyalty", "authority"],
        "side_b": ["fairness", "care", "liberty"],
    }

    G = build_graph(results)
    gap = G.nodes["scenario:GP-01"].get("false_polarization_gap")
    assert gap is not None
    # shared = {fairness}, total = {fairness, loyalty, authority, care, liberty} = 5
    # gap = 1/5 = 0.2
    assert 0.15 <= gap <= 0.25


def test_false_polarization_gap_high_overlap():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["bridge"]["moral_foundations"] = {
        "side_a": ["fairness", "care"],
        "side_b": ["fairness", "care", "authority"],
    }

    G = build_graph(results)
    gap = G.nodes["scenario:GP-01"]["false_polarization_gap"]
    # shared = {fairness, care} = 2, total = {fairness, care, authority} = 3
    # gap = 2/3 = 0.67
    assert 0.6 <= gap <= 0.7


def test_false_polarization_gap_empty():
    from graph.build_graph import build_graph

    results = [_minimal_result("GP-01")]
    results[0]["bridge"]["moral_foundations"] = {}

    G = build_graph(results)
    gap = G.nodes["scenario:GP-01"]["false_polarization_gap"]
    assert gap == 0.0


# ---------------------------------------------------------------------------
# Phase D: Pivot Points
# ---------------------------------------------------------------------------


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
    pivot_nodes = [n for n, d in G.nodes(data=True) if d.get("pivot_point")]
    assert len(pivot_nodes) >= 1
