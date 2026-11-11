"""X-12: can a reader tell which passage an Auditor finding is about?

    python scripts/x12_attribution.py prepare
    python scripts/x12_attribution.py judge --judge codex
    python scripts/x12_attribution.py judge --judge fable
    python scripts/x12_attribution.py report

Protocol: data/rating/x12/PROTOCOL.md (sha256 in PROTOCOL.sha256).
"""
from __future__ import annotations

import argparse
import html
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from huginn_muninn.contracts import AnalysisReport  # noqa: E402
from huginn_muninn.llm import ClaudeCodeClient, extract_json_from_response  # noqa: E402
from huginn_muninn.locate import _norm  # noqa: E402

CLAIMS = ["HS-02", "HS-07", "HS-09", "HS-11", "MD-02", "TC-02",
          "EV-03", "GP-01", "HS-03", "HS-05", "SC-01", "TC-01"]
BASE = ROOT / "data" / "rating" / "x12"
BUILD_JS = ROOT / "gallery" / "build.js"
SEED = 20261111
JUDGES = ("codex", "fable")

TASK = """You are reading a page from a fact-checking site. The page ends with a list of findings
written by an automated reviewer about the analysis above them.

For each numbered finding, copy from the page, word for word, the one sentence of the analysis
that the finding is mainly about. If the passage the finding is about is not on this page,
write NONE.

Reply with JSON only:
{"answers": [{"finding": 1, "sentence": "..."}, {"finding": 2, "sentence": "NONE"}]}

The page:

"""

NODE = """
const m = require(process.argv[1]);
const fs = require('fs');
const d = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const strip = JSON.parse(JSON.stringify(d));
for (const f of (strip.audit && strip.audit.findings) || []) { delete f.locations; delete f.located; }
const page = data => m.buildScenarioPage({id: 'X', version: 1, data}, [{id: 'X', version: 1, data}]);
const truth = ((d.audit && d.audit.findings) || []).map(f => m.verifiedPassages(d, f));
process.stdout.write(JSON.stringify({L: page(d), N: page(strip), truth}));
"""


class _Text(HTMLParser):
    """Page HTML to plain text. Each findings-list item gets a 'Finding k:' label
    in both conditions; the design C number badge is dropped so it cannot differ."""

    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "blockquote", "tr", "br", "section", "ul", "ol"}

    def __init__(self):
        super().__init__()
        self.out: list[str] = []
        self.skip = 0
        self.in_findings = False
        self.k = 0

    VOID = {"meta", "link", "br", "img", "input", "hr", "source", "wbr", "area", "base", "col", "embed", "track"}

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            if tag == "br" and not self.skip:
                self.out.append("\n")
            return
        cls = dict(attrs).get("class") or ""
        if self.skip or tag in ("script", "style", "nav", "head") or "finding-number" in cls.split():
            self.skip += 1
            return
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "ul" and "findings-list" in cls.split():
            self.in_findings = True
        if tag == "li" and self.in_findings:
            self.k += 1
            self.out.append(f"Finding {self.k}: ")

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.skip:
            self.skip -= 1
            return
        if tag == "ul":
            self.in_findings = False
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)

    def text(self) -> str:
        t = html.unescape("".join(self.out))
        t = re.sub(r"[ \t]+", " ", t)
        return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def page_text(page_html: str) -> str:
    p = _Text()
    p.feed(page_html)
    return p.text()


def record(sid: str) -> dict:
    x10 = json.loads((ROOT / "data/rating/x10/claude-opus-5-5-medium" / f"{sid}.json").read_text(encoding="utf-8"))
    x11 = json.loads((ROOT / "data/rating/x11/replay/new" / f"{sid}.json").read_text(encoding="utf-8"))
    result = {**x10["result"], "audit": x11["audit"]}
    return AnalysisReport(**result).model_dump(mode="json")


def prepare(a) -> None:
    for d in ("inputs", "pages"):
        (BASE / d).mkdir(parents=True, exist_ok=True)
    truth_all = {}
    for sid in CLAIMS:
        rec = record(sid)
        src = BASE / "inputs" / f"{sid}.json"
        src.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        out = subprocess.run(["node", "-e", NODE, str(BUILD_JS), str(src)], capture_output=True,
                             text=True, encoding="utf-8", check=True, timeout=120)
        built = json.loads(out.stdout)
        for cond in ("L", "N"):
            (BASE / "pages" / f"{sid}-{cond}.txt").write_text(page_text(built[cond]), encoding="utf-8")
        findings = rec["audit"]["findings"]
        truth_all[sid] = []
        for i, tr in enumerate(built["truth"]):
            quotes = sorted({p["quote"] for p in tr["shown"]})
            desc = findings[i].get("description") or ""
            truth_all[sid].append({
                "finding": i + 1,
                "kind": "shown" if tr["shown"] else ("hidden" if tr["hidden"] else "unscored"),
                "category": findings[i].get("category"),
                "quotes": quotes,
                "path_texts": sorted({value_at(rec, p["path"]) for p in tr["shown"]}),
                "desc_quotes": any(longest_run(desc, q) >= 4 for q in quotes),
            })
        check_pages(sid, truth_all[sid])
    (BASE / "truth.json").write_text(json.dumps(truth_all, indent=2, ensure_ascii=False), encoding="utf-8")
    kinds = [f["kind"] for v in truth_all.values() for f in v]
    print({k: kinds.count(k) for k in ("shown", "hidden", "unscored")})


TREATMENT = ("questions this passage", "concern is about", "which this page does not show", "automated review step")


def value_at(rec: dict, path: str) -> str:
    cur = rec
    for key, idx in re.findall(r"([A-Za-z_0-9]+)|\[(\d+)\]", path):
        cur = cur[int(idx)] if idx else cur[key]
    return cur


def check_pages(sid: str, truth: list[dict]) -> None:
    """Pre-run assert (review S2-6): every shown passage survives into both page
    texts, and the N page carries none of the design C text."""
    pages = {c: words((BASE / "pages" / f"{sid}-{c}.txt").read_text(encoding="utf-8")) for c in ("L", "N")}
    for f in truth:
        for q in f["quotes"]:
            for c, page in pages.items():
                assert words(q) in page, (sid, c, f["finding"], q)
    n_text = (BASE / "pages" / f"{sid}-N.txt").read_text(encoding="utf-8")
    assert not any(s in n_text for s in TREATMENT), sid


def call_codex(prompt: str, workdir: Path) -> str:
    out = workdir / f"out-{random.getrandbits(48):x}.txt"
    cmd = [shutil.which("codex") or "codex", "exec", "-m", "gpt-6-astra", "-c", "model_reasoning_effort=high",
           "--skip-git-repo-check", "--ephemeral", "--sandbox", "read-only", "--ignore-rules",
           "-C", str(workdir), "-o", str(out), "-"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=900)
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"codex exited {proc.returncode}: {proc.stderr[-400:]}")
    text = out.read_text(encoding="utf-8")
    out.unlink()
    return text


def judge(a) -> None:
    items = [(sid, cond) for sid in CLAIMS for cond in ("L", "N")]
    random.Random(SEED).shuffle(items)
    out_dir = BASE / "judgments" / a.judge
    out_dir.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.gettempdir()) / "huginn-x12"
    workdir.mkdir(exist_ok=True)
    fable = ClaudeCodeClient(model="claude-fable-5-2", timeout=900) if a.judge == "fable" else None

    def one(item) -> None:
        sid, cond = item
        dest = out_dir / f"{sid}-{cond}.json"
        if dest.exists():
            return
        prompt = TASK + (BASE / "pages" / f"{sid}-{cond}.txt").read_text(encoding="utf-8")
        try:
            raw = call_codex(prompt, workdir) if a.judge == "codex" else fable.generate(prompt)
            reply = extract_json_from_response(raw, expected_keys={"answers"})
        except Exception as e:  # logged and left for a rerun
            print(f"{sid}-{cond}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
            return
        dest.write_text(json.dumps({"raw": raw, "reply": reply}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{sid}-{cond}: {len(reply.get('answers') or [])} answers", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(one, items))


def words(s: str) -> str:
    return " ".join(re.findall(r"\w+", _norm(s or "").casefold()))


def longest_run(a: str, b: str) -> int:
    x, y = words(a).split(), words(b).split()
    best = 0
    prev = [0] * (len(y) + 1)
    for i in range(1, len(x) + 1):
        cur = [0] * (len(y) + 1)
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


MAX_ANSWER_WORDS = 60


def is_none(sentence: str) -> bool:
    return words(sentence) == "none"


def is_hit(sentence: str, f: dict) -> bool:
    n = len(words(sentence).split())
    if n == 0 or is_none(sentence) or n > MAX_ANSWER_WORDS:
        return False
    from_passage = any(longest_run(sentence, pt) >= 0.8 * n for pt in f["path_texts"])
    on_quote = any(longest_run(sentence, q) >= min(6, len(words(q).split())) for q in f["quotes"])
    return from_passage and on_quote


def score(judge_name: str, truth: dict) -> dict:
    res = {}
    for cond in ("L", "N"):
        hits = shown = none_ok = hidden = 0
        split = {"no_completeness": [0, 0], "desc_quotes": [0, 0], "desc_silent": [0, 0]}
        per = {}
        for sid in CLAIMS:
            path = BASE / "judgments" / judge_name / f"{sid}-{cond}.json"
            answers = {}
            if path.exists():
                for x in json.loads(path.read_text(encoding="utf-8"))["reply"].get("answers") or []:
                    if isinstance(x, dict):
                        try:
                            answers[int(x.get("finding"))] = str(x.get("sentence") or "")
                        except (TypeError, ValueError):
                            pass
            h = n = 0
            for f in truth[sid]:
                ans = answers.get(f["finding"])
                if f["kind"] == "shown":
                    hit = ans is not None and is_hit(ans, f)
                    shown += 1
                    n += 1
                    hits += hit
                    h += hit
                    groups = ["desc_quotes" if f["desc_quotes"] else "desc_silent"]
                    if f["category"] != "completeness":
                        groups.append("no_completeness")
                    for g in groups:
                        split[g][0] += hit
                        split[g][1] += 1
                elif f["kind"] == "hidden":
                    hidden += 1
                    if ans is not None and is_none(ans):
                        none_ok += 1
            per[sid] = f"{h}/{n}" if path.exists() else "missing"
        res[cond] = {"A": hits / shown if shown else 0.0, "hits": hits, "shown": shown,
                     "F": (hidden - none_ok) / hidden if hidden else 0.0, "hidden": hidden, "per_claim": per,
                     "split": {g: (v[0] / v[1] if v[1] else 0.0, v[0], v[1]) for g, v in split.items()}}
    return res


def report(a) -> None:
    truth = json.loads((BASE / "truth.json").read_text(encoding="utf-8"))
    scores = {j: score(j, truth) for j in JUDGES if (BASE / "judgments" / j).exists()}
    lines = ["# X-12 result", ""]
    for j, s in scores.items():
        lines.append(f"## Judge: {j}")
        lines.append("")
        lines.append("| Condition | A (hits / shown) | F (false attributions / hidden) |")
        lines.append("|---|---|---|")
        for cond in ("L", "N"):
            c = s[cond]
            lines.append(f"| {cond} | {c['A']:.2f} ({c['hits']}/{c['shown']}) | {c['F']:.2f} of {c['hidden']} |")
        lines.append("")
        lines.append("Per claim, N: " + ", ".join(f"{k} {v}" for k, v in s["N"]["per_claim"].items()))
        lines.append("")
        for cond in ("L", "N"):
            lines.append(f"{cond} split: " + "; ".join(f"{g} {a:.2f} ({h}/{n})" for g, (a, h, n) in s[cond]["split"].items()))
        lines.append("")
    if set(scores) == set(JUDGES):
        a_l = [scores[j]["L"]["A"] for j in JUDGES]
        # co-primary (review S1-3): A_N over all shown findings and without completeness findings
        a_n = [scores[j]["N"]["A"] for j in JUDGES] + [scores[j]["N"]["split"]["no_completeness"][0] for j in JUDGES]
        if min(a_l) < 0.95:
            verdict = "check failed: A_L below 0.95; fix the page text or prompt and repeat once"
        elif min(a_n) >= 0.90:
            verdict = ("A_N >= 0.90 on both measures for both judges: a strong reader finds the passage "
                       "without help; locating adds little for this task; hand check of ten N items next")
        elif max(a_n) <= 0.75:
            verdict = ("A_N <= 0.75 on both measures for both judges: readers cannot find the Auditor's "
                       "passage unaided; locating helps; quote and inline notes are not separated")
        else:
            verdict = "inconclusive: display stays, no benefit claimed"
        lines += ["## Decision", "", verdict, ""]
    (BASE / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["prepare", "judge", "report"])
    p.add_argument("--judge", choices=JUDGES)
    p.add_argument("--workers", type=int, default=3)
    a = p.parse_args()
    {"prepare": prepare, "judge": judge, "report": report}[a.step](a)


if __name__ == "__main__":
    main()
