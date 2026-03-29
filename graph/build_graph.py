"""
Huginn & Muninn Knowledge Graph Builder

Extracts entities from pipeline JSON results into a NetworkX graph.
Exports Cytoscape.js-compatible JSON for the gallery.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
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

CATEGORY_BY_PREFIX = {
    "HS": "Health & Science",
    "GP": "Geopolitics",
    "EN": "Environment",
    "EV": "Events",
    "TC": "Technology",
    "MD": "Media",
}

_PATTERN_SEVERITY: dict[str, int] = {"isolated": 0, "repeated": 1, "systematic": 2}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _parse_version(filename: str) -> int:
    """Extract version number from filename like 'HS-01-opus-v4.json'."""
    name = Path(filename).stem
    for part in reversed(name.split("-")):
        if part.startswith("v") and part[1:].isdigit():
            return int(part[1:])
    return 0


def _slugify(name: str) -> str:
    """Convert a name to a URL-safe slug for node IDs."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _short_hash(text: str) -> str:
    """Return first 8 hex chars of SHA-256 digest of text."""
    return hashlib.sha256(text.encode()).hexdigest()[:8]


def _category(scenario_id: str) -> str:
    """Return full category name for the given scenario ID prefix."""
    prefix = scenario_id.split("-")[0]
    return CATEGORY_BY_PREFIX.get(prefix, "Unknown")


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_results(results_dir: Path | None = None) -> list[dict]:
    """Load JSON results, keeping only the highest version per scenario_id.

    Results are returned sorted by scenario_id.
    """
    results_dir = results_dir or RESULTS_DIR
    best: dict[str, tuple[int, dict]] = {}

    for fp in sorted(results_dir.glob("*.json")):
        try:
            with open(fp) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        sid = data.get("scenario_id", "")
        if not sid:
            continue

        ver = _parse_version(fp.name)
        if sid not in best or ver > best[sid][0]:
            best[sid] = (ver, data)

    return [entry for _, entry in sorted(best.values(), key=lambda x: x[1].get("scenario_id", ""))]


# ---------------------------------------------------------------------------
# Node builders
# ---------------------------------------------------------------------------

def _add_scenario(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Add a scenario node to the graph."""
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


def _add_actors(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract actors from intelligence.actors, dedup by slugified name.

    Tracks all scenarios each actor appears in and keeps the maximum
    credibility seen across those appearances.
    """
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


def _add_actor_relations(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract actor-to-actor relations from intelligence.relations.

    Creates relates_to edges between actor nodes that must already exist.
    When the same directed relation appears in multiple scenarios the
    highest-confidence version is preserved.
    """
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


def _add_techniques(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract DISARM TTP nodes from ttps.ttp_matches.

    Deduplicates by DISARM ID and tracks all scenarios in which each
    technique appears, keeping the maximum observed confidence.
    """
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


def _add_technique_reveals(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract Name-the-Trick reveal nodes from bridge.techniques_revealed.

    Deduplicates by slugified technique name.  Pattern severity is
    monotonically upgraded: isolated < repeated < systematic.
    """
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


def _add_mutations(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract narrative-evolution mutation nodes from origins.mutations.

    Node IDs are based on a short hash of original+mutated text so that
    identical mutations appearing across scenarios are deduplicated.
    """
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


def _add_claims(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract sub-claim nodes from decomposition.sub_claims.

    IDs are scenario-specific (claim:SID-index) because sub-claims are
    not deduplicated across scenarios.
    """
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


def _add_temporal_eras(G: nx.DiGraph, r: dict, sid: str) -> None:
    """Extract temporal era nodes from origins.temporal_context.

    Deduplicates by slugified era name; all scenarios sharing an era are
    collected in the node's scenarios list.
    """
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


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph(results: list[dict]) -> nx.DiGraph:
    """Build a NetworkX directed graph from pipeline results.

    Processes each result through all entity extractors in order:
    scenario -> actors -> actor_relations -> techniques ->
    technique_reveals -> mutations -> claims -> temporal_eras
    """
    G = nx.DiGraph()

    for r in results:
        sid = r["scenario_id"]
        _add_scenario(G, r, sid)
        _add_actors(G, r, sid)
        _add_actor_relations(G, r, sid)
        _add_techniques(G, r, sid)
        _add_technique_reveals(G, r, sid)
        _add_mutations(G, r, sid)
        _add_claims(G, r, sid)
        _add_temporal_eras(G, r, sid)

    return G


# ---------------------------------------------------------------------------
# Statistics and export
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Build the knowledge graph and export to Cytoscape.js JSON."""
    print("Huginn & Muninn Knowledge Graph Builder")
    print("=" * 40)

    results = load_results()
    print(f"Loaded {len(results)} scenarios (highest version per ID)")

    G = build_graph(results)
    stats = graph_stats(G)
    print("\nGraph Statistics:")
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
