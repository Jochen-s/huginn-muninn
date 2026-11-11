"""Gallery rendering of located Auditor findings (design C, 2026-11-10).

The renderers run in node; each test passes a scenario as JSON and reads the
HTML back. The build re-checks every quote against the text at its path, so
these tests also cover stale and forged paths and the veto.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

BUILD_JS = Path(__file__).resolve().parent.parent / "gallery" / "build.js"
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

QUOTE = "Both sides want the record to be honest"


def _data(locations, **extra):
    return {
        "claim": "X",
        "bridge": {"issue_overlap": f"{QUOTE} and complete.", "reframe": "A different frame entirely here.",
                   "socratic_dialogue": ["R1 text", "R2 text", "R3 text?"]},
        "audit": {"verdict": "pass_with_warnings", "summary": "s", "findings": [
            {"category": "manipulation", "severity": "medium", "description": "Overlap is overstated.",
             "recommendation": "Qualify it.", "locations": locations}]},
        **extra,
    }


def _render(data, fn="findings"):
    call = {
        "findings": "m.renderFindings(d.audit.findings, d)",
        "notes": "m.renderNotes(m.noteIndex(d), 'bridge.issue_overlap')",
    }[fn]
    script = f"const m = require({json.dumps(str(BUILD_JS))}); const d = JSON.parse(process.argv[1]); process.stdout.write({call});"
    out = subprocess.run(["node", "-e", script, json.dumps(data)], capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=60)
    return out.stdout


def test_located_finding_shows_its_passage_and_anchor():
    html = _render(_data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}]))
    assert 'id="finding-1"' in html
    assert QUOTE in html


def test_note_appears_beside_the_passage():
    html = _render(_data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}]), "notes")
    assert 'href="#finding-1"' in html and "questions this passage (finding 1, medium)" in html


def test_forged_path_shows_nothing():
    html = _render(_data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.reframe"]}]))
    assert QUOTE not in html and 'id="finding-1"' not in html


def test_veto_drops_bridge_passages():
    data = _data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}], bridge_withheld=True)
    assert QUOTE not in _render(data)


def test_page_without_locations_is_unchanged():
    html = _render(_data([]))
    assert "finding-number" not in html and "id=" not in html


def _page(data):
    script = (f"const m = require({json.dumps(str(BUILD_JS))}); const d = JSON.parse(process.argv[1]);"
              "const s = {id: 'XX-01', version: 1, data: d}; process.stdout.write(m.buildScenarioPage(s, [s]));")
    return subprocess.run(["node", "-e", script, json.dumps(data)], capture_output=True, text=True,
                          encoding="utf-8", check=True, timeout=60).stdout


def test_page_puts_the_note_inside_the_common_ground_section():
    html = _page(_data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}]))
    section = html[html.index("<h2>Common Ground</h2>"):html.index("<h2>Narrative Deconstruction</h2>")]
    assert 'href="#finding-1"' in section


def test_page_says_what_the_auditor_is():
    html = _page(_data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}]))
    assert "automated review step" in html and "no person has checked them" in html


def test_audit_veto_alone_drops_bridge_passages():
    data = _data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap"]}])
    data["audit"]["veto"] = True
    assert QUOTE not in _render(data)


def test_quote_from_a_section_the_page_hides_is_named_not_printed():
    data = _data([{"section": "intelligence", "quote": "places him inside the system it critiques",
                   "paths": ["intelligence.actors[0].motivation"]}])
    data["intelligence"] = {"actors": [{"motivation": "This places him inside the system it critiques."}]}
    html = _render(data)
    assert "places him inside" not in html
    assert "the actor analysis, which this page does not show" in html


def test_quote_from_a_printed_technique_card_is_quoted():
    q = "the claim leans on a single anecdote"
    data = _data([{"section": "bridge", "quote": q, "paths": ["bridge.techniques_revealed[0].where_used_here"]}])
    data["bridge"]["techniques_revealed"] = [{"technique": "Anecdote", "where_used_here": "Here " + q + "."}]
    html = _render(data)
    assert q in html and "does not show" not in html


def test_quote_from_the_source_diversity_warning_is_quoted():
    q = "100% of classified sources are western_academic"
    data = _data([{"section": "origins", "quote": q, "paths": ["origins.epistemic_diversity_gap"]}])
    data["origins"] = {"epistemic_diversity_gap": q + "."}
    html = _render(data)
    assert q in html and "does not show" not in html


def test_quote_text_is_escaped():
    q = "<b>seven</b> & \"eight\" nine ten"
    data = _data([{"section": "bridge", "quote": q, "paths": ["bridge.issue_overlap"]}])
    data["bridge"]["issue_overlap"] = q + " more."
    html = _render(data)
    assert "<b>seven" not in html and "&lt;b&gt;seven" in html


def test_same_quote_at_two_paths_prints_once():
    data = _data([{"section": "bridge", "quote": QUOTE, "paths": ["bridge.issue_overlap", "bridge.reframe"]}])
    data["bridge"]["reframe"] = QUOTE + "."
    assert _render(data).count('class="finding-quote"') == 1


def test_malformed_locations_do_not_break_the_page():
    for locs in ([None], {"a": 1}, [{"quote": QUOTE, "paths": [["bridge.issue_overlap"]]}],
                 [{"quote": QUOTE, "paths": {"a": "x"}}], ["text"],
                 [{"quote": QUOTE, "paths": ["bridge[issue_overlap]", "bridge..issue_overlap"]}]):
        html = _render(_data(locs))
        assert QUOTE not in html, locs


def test_build_runs_main_only_when_executed():
    js = BUILD_JS.read_text(encoding="utf-8")
    assert "if (require.main === module) {\n  main();" in js.replace("\r\n", "\n")
