"""Blinded pairwise rating of full-pipeline analyses (X-08).

    python scripts/rating_judge.py prepare           # blind items + key
    python scripts/rating_judge.py judge --judge codex --workers 4
    python scripts/rating_judge.py judge --judge sonnet --workers 3
    python scripts/rating_judge.py report

Every analysis is rendered through one fixed template, so formatting is the
same for all models and only the content differs. Each model pair is judged
in both A/B orders; a pair counts as a win only when both orders agree,
otherwise as a tie. The key (item -> models) sits apart from the items.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from huginn_muninn.llm import ClaudeCodeClient, extract_json_from_response  # noqa: E402

CRITERIA = ["accuracy", "evidence", "fairness", "bridge", "insight"]
DROP_KEYS = {"method", "confidence_profile", "cnqs", "claim", "original_claim"}

RUBRIC = """You are rating two analyses of the same claim, produced by an automated
fact-checking and bridge-building pipeline. The pipeline's goal: decompose the
claim, trace its origins, map the actors, name the manipulation techniques, and
help people on both sides find common ground without condescension.

Judge each criterion and pick A, B or tie:
- accuracy: factual correctness. Fabricated sources, dates, people or quotes
  count heavily against an analysis. Wrong verdicts count against it.
- evidence: are sources specific, real and fairly weighted; is the origin
  trace plausible and checkable?
- fairness: respectful, non-condescending tone; takes the believer's concerns
  seriously; no controlling language ("the truth is", "you were misled").
- bridge: would the common-ground section, dialogue and reframe actually help
  a believer and a skeptic talk to each other?
- insight: does it find the kernel of truth, the real motives and the actual
  techniques, beyond generic statements?

Do NOT prefer an analysis because it is longer or lists more items. Extra
material counts only when it is accurate and relevant; padding and repetition
count against it. A "degraded" status means a pipeline stage failed; judge the
content that is present.

Reply with only this JSON object:
{"accuracy": "A|B|tie", "evidence": "A|B|tie", "fairness": "A|B|tie",
 "bridge": "A|B|tie", "insight": "A|B|tie", "overall": "A|B|tie",
 "confidence": "low|medium|high", "reason": "<two or three sentences>"}
"""


def render(value, depth: int = 0) -> list[str]:
    """Fixed-template markdown rendering of an analysis value."""
    pad = "  " * depth
    lines: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k in DROP_KEYS or v in (None, "", [], {}):
                continue
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}- {k}:")
                lines += render(v, depth + 1)
            else:
                lines.append(f"{pad}- {k}: {v}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines += render(item, depth + 1)
            else:
                lines.append(f"{pad}- {item}")
    else:
        lines.append(f"{pad}{value}")
    return lines


def render_analysis(record: dict) -> str:
    if record.get("error") or not record.get("result"):
        return "The pipeline produced no analysis (run failed)."
    r = record["result"]
    out = []
    status = "degraded: " + (r.get("degraded_reason") or "") if r.get("degraded") else "complete"
    out.append(f"Status: {status}")
    out.append(f"Overall confidence: {r.get('overall_confidence', 0):.2f}")
    for section in ["decomposition", "origins", "intelligence", "ttps", "bridge", "audit"]:
        if r.get(section):
            out.append(f"\n### {section}")
            out += render(r[section])
    return "\n".join(out)


def run_dir(run: str) -> Path:
    return ROOT / "data" / "rating" / run


def prepare(a) -> None:
    base = run_dir(a.run)
    models = a.models.split(",")
    blind = base / "blind"
    (blind / "items").mkdir(parents=True, exist_ok=True)
    ids = sorted(p.stem for p in (base / models[0]).glob("*.json"))
    rng = random.Random(a.seed)
    entries = []
    for sid in ids:
        recs = {m: json.loads((base / m / f"{sid}.json").read_text(encoding="utf-8")) for m in models}
        for m1, m2 in itertools.combinations(models, 2):
            first, second = (m1, m2) if rng.random() < 0.5 else (m2, m1)
            for left, right in [(first, second), (second, first)]:
                entries.append({"scenario": sid, "claim": recs[left]["claim"], "A": left, "B": right,
                                "text_a": render_analysis(recs[left]), "text_b": render_analysis(recs[right])})
    rng.shuffle(entries)
    key = {}
    for i, e in enumerate(entries, 1):
        item = f"p{i:03d}"
        key[item] = {"scenario": e["scenario"], "A": e["A"], "B": e["B"]}
        body = (f"{RUBRIC}\nClaim: {e['claim']}\n\n## Analysis A\n\n{e['text_a']}\n\n"
                f"## Analysis B\n\n{e['text_b']}\n")
        (blind / "items" / f"{item}.md").write_text(body, encoding="utf-8")
    (base / "key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"{len(entries)} items for {len(ids)} scenarios x {len(models)} models")


def judge_codex(prompt: str, workdir: Path) -> str:
    out = workdir / f"out-{random.getrandbits(48):x}.txt"
    cmd = [shutil.which("codex") or "codex", "exec", "--skip-git-repo-check", "--ephemeral",
           "--sandbox", "read-only", "--ignore-rules", "-C", str(workdir), "-o", str(out), "-"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=900)
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"codex exited {proc.returncode}: {proc.stderr[-400:]}")
    text = out.read_text(encoding="utf-8")
    out.unlink()
    return text


def judge(a) -> None:
    base = run_dir(a.run)
    items = sorted((base / "blind" / "items").glob("*.md"))[: a.limit or None]
    out_dir = base / "judgments" / a.judge
    out_dir.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.gettempdir()) / "huginn-judge"
    workdir.mkdir(exist_ok=True)
    sonnet = ClaudeCodeClient(model="claude-sonnet-5-5", timeout=900) if a.judge == "sonnet" else None

    def one(path: Path) -> None:
        dest = out_dir / f"{path.stem}.json"
        if dest.exists():
            return
        prompt = path.read_text(encoding="utf-8")
        try:
            raw = judge_codex(prompt, workdir) if a.judge == "codex" else sonnet.generate(prompt)
            verdict = extract_json_from_response(raw, expected_keys=set(CRITERIA) | {"overall"})
        except Exception as e:  # logged and left for a rerun; one failure must not stop the batch
            print(f"{path.stem}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
            return
        dest.write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{path.stem}: {verdict.get('overall')}", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(one, items))


def report(a) -> None:
    base = run_dir(a.run)
    key = json.loads((base / "key.json").read_text(encoding="utf-8"))
    judges = sorted(p.name for p in (base / "judgments").iterdir() if p.is_dir())
    lines = [f"# Blinded pairwise rating, run {a.run}", ""]
    per_judge_outcomes: dict[str, dict] = {}
    for j in judges:
        # verdict per (scenario, pair, criterion) -> winning model per order
        votes: dict[tuple, list] = defaultdict(list)
        for item, meta in key.items():
            f = base / "judgments" / j / f"{item}.json"
            if not f.exists():
                continue
            v = json.loads(f.read_text(encoding="utf-8"))
            pair = tuple(sorted((meta["A"], meta["B"])))
            for c in CRITERIA + ["overall"]:
                pick = str(v.get(c, "tie")).strip()
                winner = meta["A"] if pick == "A" else meta["B"] if pick == "B" else "tie"
                votes[(meta["scenario"], pair, c)].append(winner)
        outcomes = {}
        position_flips = 0
        for k, ws in votes.items():
            if len(ws) == 2 and ws[0] == ws[1]:
                outcomes[k] = ws[0]
            else:
                outcomes[k] = "tie"
                if len(ws) == 2 and k[2] == "overall":
                    position_flips += 1
        per_judge_outcomes[j] = outcomes
        lines += [f"## Judge: {j}", "",
                  f"Overall verdicts that changed with A/B order (counted as ties): {position_flips}", "",
                  "| Pair | Criterion | Wins first | Wins second | Ties |", "|---|---|---|---|---|"]
        tally: dict[tuple, dict] = defaultdict(lambda: defaultdict(int))
        for (sid, pair, c), w in outcomes.items():
            tally[(pair, c)][w] += 1
        for (pair, c) in sorted(tally, key=lambda t: (t[0], (CRITERIA + ["overall"]).index(t[1]))):
            t = tally[(pair, c)]
            lines.append(f"| {pair[0]} vs {pair[1]} | {c} | {t[pair[0]]} | {t[pair[1]]} | {t['tie']} |")
        lines.append("")
    if len(judges) >= 2:
        j1, j2 = judges[:2]
        shared = [k for k in per_judge_outcomes[j1] if k in per_judge_outcomes[j2] and k[2] == "overall"]
        agree = sum(per_judge_outcomes[j1][k] == per_judge_outcomes[j2][k] for k in shared)
        lines += [f"## Agreement {j1} vs {j2}", "",
                  f"Overall pair outcomes identical: {agree} of {len(shared)}", ""]
    text = "\n".join(lines)
    (base / "report.md").write_text(text, encoding="utf-8")
    print(text)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["prepare", "judge", "report"])
    p.add_argument("--run", default="2026-10-25")
    p.add_argument("--models", default="qwen3.5-9b,qwen3.8-27b,claude-opus-5-5-medium")
    p.add_argument("--judge", choices=["codex", "sonnet"])
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--limit", type=int, help="judge only the first N items")
    p.add_argument("--seed", type=int, default=20261025)
    a = p.parse_args()
    {"prepare": prepare, "judge": judge, "report": report}[a.step](a)


if __name__ == "__main__":
    main()
