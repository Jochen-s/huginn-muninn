"""Generate full-pipeline analyses for the blinded model rating (X-08).

One JSON file per scenario per model under data/rating/<run>/<model-label>/.
Existing files are skipped, so an interrupted run resumes.

    python scripts/rating_generate.py qwen3.5:9b --ids HS-01,EN-01
    python scripts/rating_generate.py claude-opus-5-5 --provider claude-code --effort medium --ids HS-01
"""
from __future__ import annotations

import argparse
import logging
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))  # sibling import; see run_bridge_scenarios.py

from huginn_muninn.llm import create_client  # noqa: E402
from huginn_muninn.orchestrator import Orchestrator  # noqa: E402
from scenarios import get_scenario  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--provider", default="ollama", choices=["ollama", "openai", "anthropic", "claude-code"])
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--base-url", default="http://localhost:11434")
    p.add_argument("--ids", required=True, help="comma-separated scenario ids")
    p.add_argument("--run", default="2026-10-25")
    a = p.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    label = re.sub(r"[^A-Za-z0-9.-]", "-", a.model) + (f"-{a.effort}" if a.effort else "")
    out_dir = ROOT / "data" / "rating" / a.run / label
    out_dir.mkdir(parents=True, exist_ok=True)
    kwargs = {"effort": a.effort} if a.effort and a.provider in ("anthropic", "claude-code") else {}
    client = create_client(a.provider, a.base_url, a.model, **kwargs)
    orch = Orchestrator(client)

    for sid in a.ids.split(","):
        path = out_dir / f"{sid}.json"
        if path.exists():
            print(f"{label} {sid}: exists, skipped", flush=True)
            continue
        scenario = get_scenario(sid)
        cost_before = getattr(client, "total_cost_usd", None)
        start = time.time()
        try:
            result, error = orch.run(scenario["claim"]), None
        except Exception as e:  # recorded, not fatal: one failure must not stop the batch
            result, error = None, f"{type(e).__name__}: {e}"
        elapsed = round(time.time() - start, 1)
        cost = None
        if cost_before is not None:
            cost = round(client.total_cost_usd - cost_before, 4)
        record = {"scenario_id": sid, "claim": scenario["claim"], "model": a.model,
                  "provider": a.provider, "effort": a.effort, "elapsed_seconds": elapsed,
                  "cost_usd": cost, "error": error, "result": result}
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        status = "ERROR " + error[:120] if error else f"degraded={result.get('degraded', False)}"
        print(f"{label} {sid}: {elapsed}s {status}", flush=True)


if __name__ == "__main__":
    main()
