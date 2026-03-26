"""Run Method 2 calibration suite against seed claims and produce a report."""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.llm import OllamaClient
from huginn_muninn.orchestrator import Orchestrator

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "calibration" / "seed_claims_m2.json"
REPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "calibration"


def validate_result(result: dict, expected: dict) -> list[str]:
    """Check structural expectations. Returns list of failure descriptions."""
    failures = []

    # Contract validation
    try:
        report = AnalysisReport(**result)
    except Exception as e:
        return [f"AnalysisReport contract violation: {e}"]

    if report.degraded:
        failures.append(f"Pipeline degraded: {report.degraded_reason}")
        return failures  # No point checking structure of degraded output

    # Sub-claims count
    if len(report.decomposition.sub_claims) < expected.get("min_sub_claims", 1):
        failures.append(
            f"Expected >= {expected['min_sub_claims']} sub-claims, got {len(report.decomposition.sub_claims)}"
        )

    # Complexity
    valid_complexities = expected.get("complexity", [])
    if valid_complexities and report.decomposition.complexity not in valid_complexities:
        failures.append(
            f"Expected complexity in {valid_complexities}, got '{report.decomposition.complexity}'"
        )

    # Actors
    if expected.get("has_actors") and len(report.intelligence.actors) == 0:
        failures.append("Expected actors but got none")

    # TTPs
    if expected.get("has_ttps") and len(report.ttps.ttp_matches) == 0:
        failures.append("Expected TTP matches but got none")

    # Bridge
    if expected.get("has_bridge_needs"):
        if report.bridge.universal_needs == ["unknown"]:
            failures.append("Bridge returned fallback ['unknown'] needs")

    # Socratic dialogue rounds
    min_rounds = expected.get("min_socratic_rounds", 1)
    if len(report.bridge.socratic_dialogue) < min_rounds:
        failures.append(
            f"Expected >= {min_rounds} Socratic rounds, got {len(report.bridge.socratic_dialogue)}"
        )

    # Veto check
    if expected.get("should_not_veto") and report.audit.veto:
        failures.append("Auditor vetoed unexpectedly")

    return failures


def run_calibration(model: str = "qwen3.5:9b") -> dict:
    """Run all seed claims through Method 2 and return results."""
    with open(SEED_FILE) as f:
        seed_data = json.load(f)

    claims = seed_data["claims"]
    results = []

    with OllamaClient(model=model) as client:
        if not client.check_available():
            print(f"ERROR: Ollama not available or model '{model}' not found.", file=sys.stderr)
            sys.exit(1)

        orch = Orchestrator(client)

        for i, entry in enumerate(claims):
            claim_text = entry["text"]
            print(f"\n[{i+1}/{len(claims)}] {claim_text}", file=sys.stderr)
            print(f"  Running 6-agent pipeline...", file=sys.stderr)

            t0 = time.time()
            try:
                result = orch.run(claim_text)
                elapsed = time.time() - t0

                failures = validate_result(result, entry["expected"])
                status = "PASS" if not failures else "FAIL"

                results.append({
                    "claim": claim_text,
                    "category": entry["category"],
                    "polarized": entry["polarization"],
                    "degraded": result.get("degraded", False),
                    "overall_confidence": result.get("overall_confidence", 0),
                    "num_sub_claims": len(result.get("decomposition", {}).get("sub_claims", [])),
                    "num_actors": len(result.get("intelligence", {}).get("actors", [])),
                    "num_ttps": len(result.get("ttps", {}).get("ttp_matches", [])),
                    "num_socratic_rounds": len(result.get("bridge", {}).get("socratic_dialogue", [])),
                    "audit_verdict": result.get("audit", {}).get("verdict", "unknown"),
                    "audit_veto": result.get("audit", {}).get("veto", False),
                    "failures": failures,
                    "elapsed_seconds": round(elapsed, 1),
                    "error": None,
                })
                print(f"  {status} conf={result.get('overall_confidence', 0):.0%} "
                      f"sub_claims={len(result.get('decomposition', {}).get('sub_claims', []))} "
                      f"actors={len(result.get('intelligence', {}).get('actors', []))} "
                      f"ttps={len(result.get('ttps', {}).get('ttp_matches', []))} "
                      f"({elapsed:.1f}s)", file=sys.stderr)
                if failures:
                    for f_msg in failures:
                        print(f"    FAIL: {f_msg}", file=sys.stderr)

            except Exception as e:
                elapsed = time.time() - t0
                results.append({
                    "claim": claim_text,
                    "category": entry["category"],
                    "polarized": entry["polarization"],
                    "degraded": True,
                    "overall_confidence": 0,
                    "num_sub_claims": 0,
                    "num_actors": 0,
                    "num_ttps": 0,
                    "num_socratic_rounds": 0,
                    "audit_verdict": "error",
                    "audit_veto": False,
                    "failures": [str(e)],
                    "elapsed_seconds": round(elapsed, 1),
                    "error": str(e),
                })
                print(f"  ERROR: {e} ({elapsed:.1f}s)", file=sys.stderr)

    return {"model": model, "timestamp": datetime.now(timezone.utc).isoformat(), "results": results}


def generate_report(data: dict) -> str:
    """Generate a markdown calibration report."""
    results = data["results"]
    total = len(results)
    passes = sum(1 for r in results if not r["failures"])
    errors = sum(1 for r in results if r["error"])
    degraded = sum(1 for r in results if r["degraded"])
    avg_time = sum(r["elapsed_seconds"] for r in results) / max(total, 1)

    lines = [
        "# Method 2 Calibration Report",
        "",
        f"**Model**: {data['model']}",
        f"**Timestamp**: {data['timestamp']}",
        f"**Claims**: {total}",
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "|--------|--------|",
        f"| Full pass | {passes}/{total} ({passes/max(total, 1):.0%}) |",
        f"| Degraded pipelines | {degraded}/{total} |",
        f"| Errors | {errors}/{total} |",
        f"| Avg time per claim | {avg_time:.0f}s |",
        "",
        "## Results",
        "",
        "| # | Claim | Cat | Conf | Sub | Act | TTP | Dial | Audit | Time | Status |",
        "|---|-------|-----|------|-----|-----|-----|------|-------|------|--------|",
    ]

    for i, r in enumerate(results):
        status = "ERROR" if r["error"] else ("PASS" if not r["failures"] else "FAIL")
        lines.append(
            f"| {i+1} | {r['claim'][:40]} | {r['category']} | "
            f"{r['overall_confidence']:.0%} | {r['num_sub_claims']} | "
            f"{r['num_actors']} | {r['num_ttps']} | {r['num_socratic_rounds']} | "
            f"{r['audit_verdict']} | {r['elapsed_seconds']:.0f}s | {status} |"
        )

    # Detail failures
    failed = [r for r in results if r["failures"]]
    if failed:
        lines.extend(["", "## Failures", ""])
        for r in failed:
            lines.append(f"### {r['claim']}")
            for f_msg in r["failures"]:
                lines.append(f"- {f_msg}")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3.5:9b"
    data = run_calibration(model)

    # Save raw JSON
    json_path = REPORT_DIR / "calibration_results_m2.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw results: {json_path}", file=sys.stderr)

    # Save markdown report
    report = generate_report(data)
    report_path = REPORT_DIR / "calibration_report_m2.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report: {report_path}", file=sys.stderr)

    # Also print to stdout
    print(report)
