"""Re-score the five ECF dimensions on stored gallery results (2026-11-10).

The Auditor prompt now rates the claim as stated instead of the analysis.
Only the profile changes, so this re-runs the gallery runner's Auditor prompt
on the stored upstream outputs and replaces `confidence_profile`, leaving the
findings, verdict and every other field as published. Each file records what
was done in `confidence_profile_provenance`.

    python scripts/regen_ecf_profiles.py --effort medium            # all results with a profile
    python scripts/regen_ecf_profiles.py --effort medium --ids GP-07
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from huginn_muninn.contracts import ConfidenceProfile  # noqa: E402
from huginn_muninn.llm import create_client, extract_json_from_response  # noqa: E402
from run_scenario_claude import _auditor_template  # noqa: E402

RESULTS = ROOT / "tests" / "results"
NAME = re.compile(r"^([A-Z]{2}-\d{2})-opus-v(\d+)\.json$")


def latest_with_profile(results: Path = RESULTS) -> dict[str, Path]:
    """Highest version per scenario, kept only if it carries a profile."""
    best: dict[str, tuple[int, Path]] = {}
    for f in results.glob("*.json"):
        m = NAME.match(f.name)
        if m and (m[1] not in best or int(m[2]) > best[m[1]][0]):
            best[m[1]] = (int(m[2]), f)
    out = {}
    for sid, (_v, f) in sorted(best.items()):
        if json.loads(f.read_text(encoding="utf-8")).get("confidence_profile"):
            out[sid] = f
    return out


DIMENSIONS = ("evidence_quality", "source_reliability", "claim_testability",
              "expert_consensus", "internal_coherence")
UPSTREAM = ("decomposition", "origins", "intelligence", "ttps", "bridge")


def five_scores(reply: dict) -> dict:
    """The five scores from a reply, or ValueError. ConfidenceProfile fills a
    missing dimension with 0.5, which would publish an invented score."""
    prof = reply.get("confidence_profile")
    if not isinstance(prof, dict):
        raise ValueError("reply has no confidence_profile")
    out = {}
    for d in DIMENSIONS:
        v = prof.get(d)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1:
            raise ValueError(f"confidence_profile.{d} missing or out of range: {v!r}")
        out[d] = float(v)
    ConfidenceProfile(**out)  # same validation the package applies
    return out


def rescore(client, path: Path, model: str, effort: str | None) -> dict:
    r = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in UPSTREAM if not r.get(k)]
    if missing:
        raise ValueError(f"{path.name}: missing upstream output {missing}")
    t = _auditor_template(r["claim"], *(r[k] for k in UPSTREAM))
    profile = five_scores(extract_json_from_response(client.generate(t["system"] + "\n\n" + t["user"])))
    old = r.get("confidence_profile_provenance", {}).get("replaced", r.get("confidence_profile"))
    r["confidence_profile"] = profile
    r["confidence_profile_provenance"] = {
        "rescored": dt.date.today().isoformat(), "model": model, "effort": effort,
        "note": "ECF re-scored with the claim-level prompt; all other fields as published",
        "replaced": old,
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return profile


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="claude-opus-5-5")
    p.add_argument("--provider", default="claude-code")
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--ids", nargs="*")
    a = p.parse_args()
    kwargs = {"effort": a.effort} if a.effort else {}
    client = create_client(a.provider, "", a.model, **kwargs)
    for sid, f in latest_with_profile().items():
        if a.ids and sid not in a.ids:
            continue
        prof = rescore(client, f, a.model, a.effort)
        print(sid, f.name, {k: prof[k] for k in ("evidence_quality", "expert_consensus")}, flush=True)


if __name__ == "__main__":
    main()
