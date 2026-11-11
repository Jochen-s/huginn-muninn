"""Blinded ECF agreement (X-08): a human rater against the Auditor.

    python scripts/ecf_agreement.py sheet                 # writes data/rating/x08/sheet.csv
    python scripts/ecf_agreement.py score --run x10 --model claude-opus-5-5-medium

The rater scores each claim on the five ECF dimensions from their own
knowledge, without seeing any analysis or Auditor score (independent first).
Each score is one of 0, 0.25, 0.5, 0.75, 1. `score` compares the filled sheet
with the Auditor's confidence_profile in data/rating/<run>/<model>/ and reports,
per dimension, Spearman's rho and quadratic-weighted kappa on the five steps
(chance-corrected agreement).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))  # sibling import; see run_bridge_scenarios.py

from scenarios import get_scenario  # noqa: E402

DIMENSIONS = ["evidence_quality", "source_reliability", "claim_testability",
              "expert_consensus", "internal_coherence"]
STEPS = [0.0, 0.25, 0.5, 0.75, 1.0]
# Spread across categories; 20 of the 28 scenarios.
IDS = ["HS-01", "HS-02", "HS-03", "HS-05", "HS-08", "HS-10", "GP-01", "GP-02", "GP-04", "GP-06",
       "EN-01", "EN-02", "EV-01", "EV-02", "EV-04", "TC-01", "TC-02", "MD-01", "MD-02", "SC-01"]
OUT = ROOT / "data" / "rating" / "x08"


def to_step(x: float) -> int:
    """Index of the nearest of the five steps."""
    return min(range(len(STEPS)), key=lambda i: abs(STEPS[i] - x))


def weighted_kappa(a: list[int], b: list[int], k: int = len(STEPS)) -> float | None:
    """Quadratic-weighted Cohen's kappa for two raters on k ordered steps."""
    n = len(a)
    if n == 0:
        return None
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[x][y] += 1
    ra = [sum(row) for row in obs]
    rb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    w = [[(i - j) ** 2 / (k - 1) ** 2 for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * ra[i] * rb[j] / n for i in range(k) for j in range(k))
    return None if den == 0 else 1 - num / den


def spearman(a: list[float], b: list[float]) -> float | None:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for t in range(i, j + 1):
                r[order[t]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return None if va == 0 or vb == 0 else cov / (va * vb)


def sheet(a) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "sheet.csv"
    if path.exists():
        sys.exit(f"{path} exists; delete it first to start a fresh sheet")
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "claim"] + DIMENSIONS + ["note"])
        for sid in IDS:
            w.writerow([sid, get_scenario(sid)["claim"]] + [""] * (len(DIMENSIONS) + 1))
    print(f"wrote {path} ({len(IDS)} claims)")


def score(a) -> None:
    rows = list(csv.DictReader((OUT / "sheet.csv").open(encoding="utf-8")))
    lines = [f"# ECF agreement: human rater vs Auditor ({a.run}/{a.model})", "",
             "| Dimension | n | Spearman rho | Weighted kappa | Exact step match |", "|---|---|---|---|---|"]
    for d in DIMENSIONS:
        human, auditor = [], []
        for r in rows:
            f = ROOT / "data" / "rating" / a.run / a.model / f"{r['id']}.json"
            if not r.get(d, "").strip() or not f.exists():
                continue
            prof = (json.loads(f.read_text(encoding="utf-8")).get("result") or {}).get("confidence_profile") or {}
            if d not in prof:
                continue
            human.append(float(r[d]))
            auditor.append(float(prof[d]))
        hs, au = [to_step(x) for x in human], [to_step(x) for x in auditor]
        rho, kap = spearman(human, auditor), weighted_kappa(hs, au)
        exact = sum(x == y for x, y in zip(hs, au))
        fmt = lambda v: "n/a" if v is None else f"{v:.2f}"  # noqa: E731
        lines.append(f"| {d} | {len(human)} | {fmt(rho)} | {fmt(kap)} | {exact} of {len(human)} |")
    text = "\n".join(lines) + "\n"
    (OUT / f"report-{a.run}-{a.model}.md").write_text(text, encoding="utf-8")
    print(text)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["sheet", "score"])
    p.add_argument("--run", default="x10")
    p.add_argument("--model", default="claude-opus-5-5-medium")
    a = p.parse_args()
    {"sheet": sheet, "score": score}[a.step](a)


if __name__ == "__main__":
    main()
