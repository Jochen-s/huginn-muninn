"""Pages edited after their audit say so (2026-11-17).

Hand edits to stored analyses were not visible on the pages, and four audits
carried text the Auditor never wrote. These tests keep the notice list equal
to the pages CORRECTIONS.md names and keep development notes out of audits.
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUILD_JS = ROOT / "gallery" / "build.js"
RESULTS = ROOT / "tests" / "results"
ID = re.compile(r"\b[A-Z]{2}-\d{2}\b")


def _node(script):
    out = subprocess.run(["node", "-e", f"const m = require({json.dumps(str(BUILD_JS))}); {script}"],
                         capture_output=True, text=True, encoding="utf-8", check=True, timeout=60)
    return out.stdout


def _marked():
    return set(json.loads(_node("process.stdout.write(JSON.stringify([...m.EDITED_AFTER_AUDIT]));")))


def _named_in_corrections():
    text = (ROOT / "CORRECTIONS.md").read_text(encoding="utf-8")
    return {i for line in text.splitlines() if line.startswith("| ") for i in ID.findall(line)}


def _page(sid):
    d = {"claim": "c", "audit": {"verdict": "pass", "summary": "s", "findings": []}}
    script = (f"const d = {json.dumps(d)}; const s = {{id: {json.dumps(sid)}, version: 1, data: d}};"
              "process.stdout.write(m.buildScenarioPage(s, [s]));")
    return _node(script)


def test_marked_pages_equal_the_pages_corrections_names():
    assert _marked() == _named_in_corrections()


NOTICE = "CORRECTIONS.md describes the changes."


@pytest.mark.parametrize("sid, words", [
    ("SC-01", "corrected by hand on 29 March 2026"),
    ("GP-07", "written for the first version of this analysis"),
    ("GP-09", "changed by hand after the pipeline ran"),
    ("HS-07", "corrected by hand after the audit below was written"),
])
def test_marked_page_shows_its_notice_above_the_audit(sid, words):
    html = _page(sid)
    audit = html.index("<h2>Audit</h2>")
    assert audit < html.index(words) < html.index(NOTICE) < html.index("Verdict:", audit)


def test_unmarked_page_has_no_notice():
    assert NOTICE not in _page("HS-02")


def test_gp07_audit_text_is_the_first_versions():
    v1, v3 = RESULTS / "GP-07-opus-v1.json", RESULTS / "GP-07-opus-v3.json"
    if not (v1.exists() and v3.exists()):
        pytest.skip("GP-07 results not in this checkout")
    a1 = json.loads(v1.read_text(encoding="utf-8"))["audit"]
    a3 = json.loads(v3.read_text(encoding="utf-8"))["audit"]
    assert (a3["summary"], a3["findings"]) == (a1["summary"], a1["findings"])


def test_evidence_note_no_longer_claims_the_rest_is_original():
    assert "the rest of this analysis is from the original run" not in BUILD_JS.read_text(encoding="utf-8")


def test_no_stored_audit_carries_development_notes():
    files = sorted(RESULTS.glob("*-opus*.json"))
    if len(files) < 2:
        pytest.skip("the full corpus is private; the public repo ships only SC-01")
    pat = re.compile(r"pipeline redesign|redesign compliance|compliance verified|\bC[136] compliance\b|Charter C\d", re.I)
    hits = []
    for f in files:
        audit = json.loads(f.read_text(encoding="utf-8")).get("audit") or {}
        if pat.search(json.dumps(audit, ensure_ascii=False)):
            hits.append(f.name)
    assert hits == []
