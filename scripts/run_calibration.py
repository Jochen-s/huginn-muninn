"""Run calibration suite against seed claims and produce a report."""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from huginn_muninn.llm import OllamaClient, extract_json_from_response
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "calibration" / "seed_claims.json"
REPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "calibration"


def run_calibration(model: str = "qwen3.5:9b") -> dict:
    """Run all seed claims and return results."""
    with open(SEED_FILE) as f:
        seed_data = json.load(f)

    claims = seed_data["claims"]
    results = []

    with OllamaClient(model=model) as client:
        if not client.check_available():
            print(f"ERROR: Ollama not available or model '{model}' not found.", file=sys.stderr)
            sys.exit(1)

        for i, claim_entry in enumerate(claims):
            claim_text = claim_entry["text"]
            print(f"[{i+1}/{len(claims)}] {claim_text}...", file=sys.stderr)

            t0 = time.time()
            try:
                p1_raw = client.generate(build_pass1_prompt(claim_text))
                p1_data = extract_json_from_response(p1_raw)

                p2_raw = client.generate(build_pass2_prompt(claim_text, json.dumps(p1_data)))
                p2_data = extract_json_from_response(p2_raw)

                elapsed = time.time() - t0
                actual_verdict = p2_data.get("verdict", "unknown")
                actual_confidence = p2_data.get("confidence", 0)
                expected_verdict = claim_entry["expected_verdict"]
                expected_conf_min = claim_entry["expected_confidence_min"]

                verdict_match = actual_verdict == expected_verdict
                conf_pass = actual_confidence >= expected_conf_min

                results.append({
                    "claim": claim_text,
                    "category": claim_entry["category"],
                    "polarized": claim_entry["polarization"],
                    "expected_verdict": expected_verdict,
                    "actual_verdict": actual_verdict,
                    "verdict_match": verdict_match,
                    "expected_confidence_min": expected_conf_min,
                    "actual_confidence": actual_confidence,
                    "confidence_pass": conf_pass,
                    "common_ground": p2_data.get("common_ground", {}),
                    "escalation": p2_data.get("escalation", {}),
                    "elapsed_seconds": round(elapsed, 1),
                    "error": None,
                })
                status = "PASS" if (verdict_match and conf_pass) else "FAIL"
                print(f"  {status} verdict={actual_verdict} conf={actual_confidence:.0%} ({elapsed:.1f}s)", file=sys.stderr)

            except Exception as e:
                elapsed = time.time() - t0
                results.append({
                    "claim": claim_text,
                    "category": claim_entry["category"],
                    "polarized": claim_entry["polarization"],
                    "expected_verdict": claim_entry["expected_verdict"],
                    "actual_verdict": "ERROR",
                    "verdict_match": False,
                    "expected_confidence_min": claim_entry["expected_confidence_min"],
                    "actual_confidence": 0,
                    "confidence_pass": False,
                    "common_ground": {},
                    "escalation": {},
                    "elapsed_seconds": round(elapsed, 1),
                    "error": str(e),
                })
                print(f"  ERROR: {e} ({elapsed:.1f}s)", file=sys.stderr)

    return {"model": model, "timestamp": datetime.now(timezone.utc).isoformat(), "results": results}


def generate_report(data: dict) -> str:
    """Generate a markdown calibration report."""
    results = data["results"]
    total = len(results)
    verdict_matches = sum(1 for r in results if r["verdict_match"])
    conf_passes = sum(1 for r in results if r["confidence_pass"])
    full_passes = sum(1 for r in results if r["verdict_match"] and r["confidence_pass"])
    errors = sum(1 for r in results if r["error"])
    avg_time = sum(r["elapsed_seconds"] for r in results) / max(total, 1)

    lines = [
        f"# Calibration Report",
        f"",
        f"**Model**: {data['model']}",
        f"**Timestamp**: {data['timestamp']}",
        f"**Claims**: {total}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Result |",
        f"|--------|--------|",
        f"| Verdict accuracy | {verdict_matches}/{total} ({verdict_matches/total:.0%}) |",
        f"| Confidence calibration | {conf_passes}/{total} ({conf_passes/total:.0%}) |",
        f"| Full pass (verdict + confidence) | {full_passes}/{total} ({full_passes/total:.0%}) |",
        f"| Errors | {errors}/{total} |",
        f"| Avg time per claim | {avg_time:.1f}s |",
        f"",
        f"## Results",
        f"",
        f"| # | Claim | Category | Expected | Actual | Conf | Time | Status |",
        f"|---|-------|----------|----------|--------|------|------|--------|",
    ]

    for i, r in enumerate(results):
        status = "ERROR" if r["error"] else ("PASS" if (r["verdict_match"] and r["confidence_pass"]) else "FAIL")
        conf_str = f"{r['actual_confidence']:.0%}" if not r["error"] else "N/A"
        lines.append(
            f"| {i+1} | {r['claim'][:50]} | {r['category']} | {r['expected_verdict']} | "
            f"{r['actual_verdict']} | {conf_str} | {r['elapsed_seconds']:.0f}s | {status} |"
        )

    # Failures detail
    failures = [r for r in results if not (r["verdict_match"] and r["confidence_pass"]) and not r["error"]]
    if failures:
        lines.extend(["", "## Mismatches", ""])
        for r in failures:
            lines.append(f"### {r['claim']}")
            lines.append(f"- Expected: {r['expected_verdict']} (conf >= {r['expected_confidence_min']:.0%})")
            lines.append(f"- Actual: {r['actual_verdict']} (conf = {r['actual_confidence']:.0%})")
            if not r["verdict_match"]:
                lines.append(f"- Verdict mismatch")
            if not r["confidence_pass"]:
                lines.append(f"- Confidence below threshold")
            lines.append("")

    # Common Ground analysis
    lines.extend(["", "## Common Ground Analysis", ""])
    for i, r in enumerate(results):
        if r["error"]:
            continue
        cg = r.get("common_ground", {})
        if cg:
            lines.append(f"**{i+1}. {r['claim'][:50]}**")
            lines.append(f"- Technique: {cg.get('framing_technique', 'N/A')}")
            lines.append(f"- Shared concern: {cg.get('shared_concern', 'N/A')[:100]}")
            lines.append(f"- Reflection: {cg.get('reflection', 'N/A')[:100]}")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3.5:9b"
    data = run_calibration(model)

    # Save raw JSON
    json_path = REPORT_DIR / "calibration_results.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw results: {json_path}", file=sys.stderr)

    # Save markdown report
    report = generate_report(data)
    report_path = REPORT_DIR / "calibration_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report: {report_path}", file=sys.stderr)

    # Also print report to stdout
    print(report)
