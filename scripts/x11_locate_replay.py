"""X-11: re-run only the Auditor on stored X-10 results, with and without the
LOCATING FINDINGS block, and measure how often its quotes can be found.
Protocol: data/rating/x11/PROTOCOL.md. Existing outputs are skipped.

    python scripts/x11_locate_replay.py run --arm new
    python scripts/x11_locate_replay.py run --arm old
    python scripts/x11_locate_replay.py report
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from huginn_muninn.agents.auditor import AuditorAgent  # noqa: E402
from huginn_muninn.llm import create_client  # noqa: E402
from huginn_muninn.locate import locate_findings, locate_quote  # noqa: E402
from huginn_muninn.orchestrator import _compute_hypothesis_expansion_score  # noqa: E402

IDS = ["HS-02", "HS-07", "HS-09", "HS-11", "MD-02", "TC-02",
       "EV-03", "GP-01", "HS-03", "HS-05", "SC-01", "TC-01"]
SRC = ROOT / "data" / "rating" / "x10" / "claude-opus-5-5-medium"
OUT = ROOT / "data" / "rating" / "x11" / "replay"
SECTIONS = ("decomposition", "origins", "intelligence", "ttps", "bridge")
TEMPLATE_LOCATIONS = ''',
      "locations": [
        {{"section": "CHOOSE ONE: decomposition, origins, intelligence, ttps, bridge", "quote": "Words copied exactly from that section"}}
      ]'''.replace("{{", "{").replace("}}", "}")


class OldAuditor(AuditorAgent):
    """The Auditor prompt as it was before design C."""

    def build_prompt(self, input_data: dict) -> str:
        p = super().build_prompt(input_data)
        start = p.index("LOCATING FINDINGS:")
        p = p[:start] + p[p.index("VETO is a RARE", start):]
        assert p.count(TEMPLATE_LOCATIONS) == 1, "reply template changed; update OldAuditor"
        return p.replace(TEMPLATE_LOCATIONS, "")


def auditor_input(r: dict) -> dict:
    """The Auditor input the orchestrator builds (orchestrator.py, stage 5)."""
    d, o, t = r["decomposition"], r["origins"], r["ttps"]
    return {
        "original_claim": r["claim"], **{k: r[k] for k in SECTIONS},
        "gorgon_signals": {
            "hypothesis_expansion_score": _compute_hypothesis_expansion_score(d),
            "hypothesis_crowding": d.get("hypothesis_crowding", "low"),
            "notable_omissions_count": len(o.get("notable_omissions", []) or []),
            "has_gt_ttps": any((m.get("disarm_id") or "").startswith("GT-")
                               for m in t.get("ttp_matches", []) or []),
        },
    }


def run(arm: str) -> None:
    client = create_client("claude-code", "", "claude-opus-5-5", effort="medium")
    agent = (OldAuditor if arm == "old" else AuditorAgent)(client)
    out_dir = OUT / arm
    out_dir.mkdir(parents=True, exist_ok=True)
    for sid in IDS:
        path = out_dir / f"{sid}.json"
        if path.exists():
            continue
        r = json.loads((SRC / f"{sid}.json").read_text(encoding="utf-8"))["result"]
        start = time.time()
        try:
            audit, error = agent.run(auditor_input(r)), None
        except Exception as e:  # recorded; one failure must not stop the batch
            audit, error = None, f"{type(e).__name__}: {e}"
        elapsed = round(time.time() - start, 1)
        stats = locate_findings(audit, {k: r[k] for k in SECTIONS}) if audit else None
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"scenario_id": sid, "arm": arm, "elapsed_seconds": elapsed,
                                   "error": error, "stats": stats, "audit": audit},
                                  indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
        print(arm, sid, elapsed, error or stats, flush=True)


def report() -> str:
    rows, med_total, med_loc, q_total, q_found, multi, unquoted = [], 0, 0, 0, 0, 0, {}
    s_total, s_found, s_med, lost = 0, 0, 0, []
    for sid in IDS:
        old = json.loads((OUT / "old" / f"{sid}.json").read_text(encoding="utf-8"))
        new = json.loads((OUT / "new" / f"{sid}.json").read_text(encoding="utf-8"))
        if old["error"] or new["error"]:
            rows.append((sid, None, None, old["error"] or new["error"]))
            continue
        fo, fn = old["audit"]["findings"], new["audit"]["findings"]
        # The locate rules were tightened after the protocol was written (review,
        # 2026-11-10: four-word minimum, section normalising). Count both.
        src = json.loads((SRC / f"{sid}.json").read_text(encoding="utf-8"))["result"]
        sections = {k: src[k] for k in SECTIONS}
        for f in fn:
            for loc in f["locations"]:
                strict = locate_quote(sections, loc["section"], loc["quote"])
                if loc["quote"].strip():
                    s_total += 1
                    s_found += bool(strict)
                    if loc["paths"] and not strict:
                        lost.append((sid, loc["quote"]))
            s_med += f["severity"] in ("medium", "high", "critical") and any(
                locate_quote(sections, loc["section"], loc["quote"]) for loc in f["locations"])
        for f in fn:
            if f["severity"] in ("medium", "high", "critical"):
                med_total += 1
                med_loc += f["located"]
            quotes = [loc for loc in f["locations"] if loc["quote"].strip()]
            q_total += len(quotes)
            q_found += sum(bool(loc["paths"]) for loc in quotes)
            multi += sum(len(loc["paths"]) > 1 for loc in quotes)
            if not quotes:
                unquoted[f["category"]] = unquoted.get(f["category"], 0) + 1
        rows.append((sid, new["elapsed_seconds"] - old["elapsed_seconds"],
                     len(fn) / len(fo) if fo else None, None))
    ok = [r for r in rows if r[3] is None]
    added = statistics.median(r[1] for r in ok)
    ratio = statistics.median(r[2] for r in ok if r[2] is not None)
    located = med_loc / med_total if med_total else 0.0
    hit = q_found / q_total if q_total else 0.0
    checks = {"located share >= 0.75": located >= 0.75, "quote hit rate >= 0.80": hit >= 0.80,
              "median added time <= 30 s": added <= 30, "median count ratio in 0.7..1.3": 0.7 <= ratio <= 1.3}
    lines = ["# X-11 result", "",
             f"Claims: {len(ok)} of {len(IDS)} with both arms complete.",
             f"Located share (medium and above): {med_loc}/{med_total} = {located:.2f}",
             f"Quote hit rate: {q_found}/{q_total} = {hit:.2f}",
             f"With the current (stricter) locate rules: quote hit rate {s_found}/{s_total}, "
             f"located share {s_med}/{med_total}; quotes lost: {json.dumps(lost, ensure_ascii=False)}",
             f"Median added Auditor time: {added:+.1f} s",
             f"Median finding count ratio new/old: {ratio:.2f}",
             f"Quotes found in two or more places: {multi}",
             f"Findings with no quote, by category: {json.dumps(unquoted, sort_keys=True)}", "",
             "| Check | Result |", "|---|---|"]
    lines += [f"| {k} | {'pass' if v else 'FAIL'} |" for k, v in checks.items()]
    lines += ["", f"Premise holds: {'yes' if all(checks.values()) else 'no'}", "",
              "| Claim | Added s | Count ratio | Error |", "|---|---|---|---|"]
    lines += [f"| {s} | {a if a is None else f'{a:+.1f}'} | {c if c is None else f'{c:.2f}'} | {e or ''} |"
              for s, a, c, e in rows]
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run").add_argument("--arm", choices=["old", "new"], required=True)
    sub.add_parser("report")
    a = p.parse_args()
    if a.cmd == "run":
        run(a.arm)
    else:
        text = report()
        (ROOT / "data" / "rating" / "x11" / "report.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
