"""Bridge Builder scenario runner: test the full pipeline against 20 real-world claims.

Usage:
    # Run all scenarios (requires Ollama running with model available)
    python -m tests.run_bridge_scenarios

    # Run specific scenario by ID
    python -m tests.run_bridge_scenarios --id HS-01

    # Run by category
    python -m tests.run_bridge_scenarios --category health_science

    # Run by difficulty
    python -m tests.run_bridge_scenarios --difficulty easy

    # Use a different model
    python -m tests.run_bridge_scenarios --model llama3.1:8b

    # Use OpenAI-compatible endpoint (LiteLLM, OpenRouter, etc.)
    python -m tests.run_bridge_scenarios --provider openai --base-url http://localhost:4000 --model gpt-4o

    # Output JSON results
    python -m tests.run_bridge_scenarios --json-output

    # Dry run (show scenarios without executing)
    python -m tests.run_bridge_scenarios --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from huginn_muninn.llm import OllamaClient, OpenAIClient, create_client
from huginn_muninn.orchestrator import Orchestrator
from tests.scenarios import SCENARIOS, get_scenario, get_scenarios_by_category, get_scenarios_by_difficulty


def evaluate_bridge_output(scenario: dict, bridge: dict) -> dict:
    """Evaluate the Bridge Builder output against scenario expectations.

    Returns a quality score dict with individual checks and overall score.
    """
    checks = {}

    # Check 1: Universal needs identified (are expected needs present?)
    identified_needs = [n.lower().replace(" ", "_") for n in bridge.get("universal_needs", [])]
    expected = scenario.get("expected_needs", [])
    matched = sum(1 for n in expected if any(n in idn for idn in identified_needs))
    checks["needs_coverage"] = {
        "score": matched / max(len(expected), 1),
        "matched": matched,
        "expected": len(expected),
        "identified": identified_needs,
    }

    # Check 2: Issue overlap is substantive (not empty or generic)
    overlap = bridge.get("issue_overlap", "")
    checks["issue_overlap_quality"] = {
        "score": 1.0 if len(overlap) > 50 else 0.5 if len(overlap) > 10 else 0.0,
        "length": len(overlap),
    }

    # Check 3: Narrative deconstruction present and substantive
    narr = bridge.get("narrative_deconstruction", "")
    checks["narrative_deconstruction"] = {
        "score": 1.0 if len(narr) > 100 else 0.5 if len(narr) > 20 else 0.0,
        "length": len(narr),
    }

    # Check 4: Perception gap analysis present
    gap = bridge.get("perception_gap", "")
    checks["perception_gap"] = {
        "score": 1.0 if len(gap) > 30 else 0.5 if len(gap) > 5 else 0.0,
        "length": len(gap),
    }

    # Check 5: Socratic dialogue quality
    dialogue = bridge.get("socratic_dialogue", [])
    dialogue_score = 0.0
    if len(dialogue) == 3:
        dialogue_score = 0.5  # Correct number of rounds
        # Check if dialogue follows the protocol
        r1 = dialogue[0].lower() if dialogue else ""
        r3 = dialogue[2].lower() if len(dialogue) > 2 else ""
        if "?" in r3:  # Round 3 should end with a question
            dialogue_score += 0.25
        if any(w in r1 for w in ["understand", "see", "hear", "concern", "worry", "feel"]):
            dialogue_score += 0.25  # Round 1 should show perspective-getting
    checks["socratic_dialogue"] = {
        "score": dialogue_score,
        "rounds": len(dialogue),
        "ends_with_question": dialogue[-1].rstrip().endswith("?") if dialogue else False,
    }

    # Check 6: Reframe present and uses shared values language
    reframe = bridge.get("reframe", "")
    reframe_score = 0.0
    if len(reframe) > 20:
        reframe_score = 0.5
        shared_language = ["we", "together", "shared", "common", "both", "all of us", "everyone"]
        if any(w in reframe.lower() for w in shared_language):
            reframe_score = 1.0
    checks["reframe_quality"] = {
        "score": reframe_score,
        "length": len(reframe),
    }

    # Check 6b: Inferential gap analysis (new)
    inf_gap = bridge.get("inferential_gap", "")
    checks["inferential_gap"] = {
        "score": 1.0 if len(inf_gap) > 50 else 0.5 if len(inf_gap) > 10 else 0.0,
        "length": len(inf_gap),
    }

    # Check 6c: Feasibility check (new)
    feasibility = bridge.get("feasibility_check", "")
    checks["feasibility_check"] = {
        "score": 1.0 if len(feasibility) > 50 else 0.5 if len(feasibility) > 10 else 0.0,
        "length": len(feasibility),
    }

    # Check 6d: Commercial motives (new)
    commercial = bridge.get("commercial_motives", "")
    checks["commercial_motives"] = {
        "score": 1.0 if len(commercial) > 30 else 0.5 if len(commercial) > 10 else 0.0,
        "length": len(commercial),
    }

    # Check 7: No controlling language
    controlling_phrases = [
        "the truth is", "experts agree", "you were misled",
        "you fell for", "you should know", "the fact is",
        "everyone knows", "it's obvious", "you need to understand",
    ]
    all_text = json.dumps(bridge).lower()
    violations = [p for p in controlling_phrases if p in all_text]
    checks["no_controlling_language"] = {
        "score": 1.0 if not violations else 0.0,
        "violations": violations,
    }

    # Compute overall score (weighted average)
    weights = {
        "needs_coverage": 0.10,
        "issue_overlap_quality": 0.08,
        "narrative_deconstruction": 0.10,
        "inferential_gap": 0.10,
        "feasibility_check": 0.08,
        "commercial_motives": 0.07,
        "perception_gap": 0.07,
        "socratic_dialogue": 0.20,
        "reframe_quality": 0.08,
        "no_controlling_language": 0.12,
    }
    overall = sum(checks[k]["score"] * weights[k] for k in weights)

    return {
        "overall_score": round(overall, 3),
        "checks": checks,
        "grade": "A" if overall >= 0.8 else "B" if overall >= 0.6 else "C" if overall >= 0.4 else "D",
    }


def run_scenario(orchestrator: Orchestrator, scenario: dict, verbose: bool = True) -> dict:
    """Run a single scenario through the full pipeline and evaluate."""
    scenario_id = scenario["id"]
    claim = scenario["claim"]

    if verbose:
        print(f"\n{'='*70}")
        print(f"  Scenario {scenario_id}: {scenario['category']}")
        print(f"  Difficulty: {scenario['difficulty']}")
        print(f"  Claim: {claim[:80]}...")
        print(f"{'='*70}")

    start = time.time()
    try:
        result = orchestrator.run(claim)
        elapsed = time.time() - start

        bridge = result.get("bridge", {})
        evaluation = evaluate_bridge_output(scenario, bridge)

        if verbose:
            print(f"\n  Time: {elapsed:.1f}s")
            print(f"  Pipeline confidence: {result.get('overall_confidence', 0):.0%}")
            print(f"  Degraded: {result.get('degraded', False)}")
            print(f"\n  Bridge Builder Evaluation:")
            print(f"    Overall Score: {evaluation['overall_score']:.1%} (Grade: {evaluation['grade']})")
            for check_name, check_data in evaluation["checks"].items():
                status = "PASS" if check_data["score"] >= 0.5 else "FAIL"
                print(f"    [{status}] {check_name}: {check_data['score']:.0%}")

            # Show Socratic dialogue
            if bridge.get("socratic_dialogue"):
                print(f"\n  Socratic Dialogue:")
                for i, rd in enumerate(bridge["socratic_dialogue"], 1):
                    print(f"    Round {i}: {rd[:100]}...")

            # Show key Bridge Builder outputs
            if bridge.get("universal_needs"):
                print(f"\n  Universal Needs: {', '.join(bridge['universal_needs'])}")
            if bridge.get("reframe"):
                print(f"  Reframe: {bridge['reframe'][:150]}...")

        return {
            "scenario_id": scenario_id,
            "claim": claim,
            "category": scenario["category"],
            "difficulty": scenario["difficulty"],
            "elapsed_seconds": round(elapsed, 1),
            "pipeline_confidence": result.get("overall_confidence", 0),
            "degraded": result.get("degraded", False),
            "evaluation": evaluation,
            "bridge_output": bridge,
            "full_result": result,
        }

    except Exception as e:
        elapsed = time.time() - start
        if verbose:
            print(f"\n  ERROR after {elapsed:.1f}s: {e}")
        return {
            "scenario_id": scenario_id,
            "claim": claim,
            "category": scenario["category"],
            "difficulty": scenario["difficulty"],
            "elapsed_seconds": round(elapsed, 1),
            "error": str(e),
            "evaluation": {"overall_score": 0.0, "grade": "F", "checks": {}},
        }


def print_summary(results: list[dict]):
    """Print summary statistics across all scenario results."""
    print(f"\n{'='*70}")
    print(f"  BRIDGE BUILDER TEST SUITE -- SUMMARY")
    print(f"{'='*70}")

    total = len(results)
    errors = sum(1 for r in results if "error" in r)
    degraded = sum(1 for r in results if r.get("degraded", False))
    scores = [r["evaluation"]["overall_score"] for r in results if "error" not in r]

    print(f"\n  Total scenarios: {total}")
    print(f"  Completed: {total - errors}")
    print(f"  Errors: {errors}")
    print(f"  Degraded: {degraded}")

    if scores:
        avg = sum(scores) / len(scores)
        print(f"\n  Average Bridge Score: {avg:.1%}")
        print(f"  Best: {max(scores):.1%}")
        print(f"  Worst: {min(scores):.1%}")

        # Grade distribution
        grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for r in results:
            g = r["evaluation"].get("grade", "F")
            grades[g] = grades.get(g, 0) + 1
        print(f"\n  Grade Distribution: A={grades['A']} B={grades['B']} C={grades['C']} D={grades['D']} F={grades['F']}")

    # By category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        if "error" not in r:
            categories[cat].append(r["evaluation"]["overall_score"])

    print(f"\n  By Category:")
    for cat, cat_scores in sorted(categories.items()):
        if cat_scores:
            avg = sum(cat_scores) / len(cat_scores)
            print(f"    {cat}: {avg:.1%} avg ({len(cat_scores)} scenarios)")

    # By difficulty
    difficulties = {}
    for r in results:
        diff = r["difficulty"]
        if diff not in difficulties:
            difficulties[diff] = []
        if "error" not in r:
            difficulties[diff].append(r["evaluation"]["overall_score"])

    print(f"\n  By Difficulty:")
    for diff in ["easy", "medium", "hard"]:
        if diff in difficulties and difficulties[diff]:
            avg = sum(difficulties[diff]) / len(difficulties[diff])
            print(f"    {diff}: {avg:.1%} avg ({len(difficulties[diff])} scenarios)")

    # Controlling language violations
    violations = []
    for r in results:
        checks = r["evaluation"].get("checks", {})
        ctrl = checks.get("no_controlling_language", {})
        if ctrl.get("violations"):
            violations.append((r["scenario_id"], ctrl["violations"]))

    if violations:
        print(f"\n  Controlling Language Violations:")
        for sid, v in violations:
            print(f"    {sid}: {', '.join(v)}")
    else:
        print(f"\n  Controlling Language: CLEAN (no violations)")

    # Total time
    total_time = sum(r.get("elapsed_seconds", 0) for r in results)
    print(f"\n  Total execution time: {total_time:.0f}s ({total_time/60:.1f}m)")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Run Bridge Builder test scenarios")
    parser.add_argument("--id", help="Run specific scenario by ID (e.g., HS-01)")
    parser.add_argument("--category", help="Run scenarios by category")
    parser.add_argument("--difficulty", help="Run scenarios by difficulty (easy/medium/hard)")
    parser.add_argument("--model", default="qwen3.5:9b", help="LLM model name")
    parser.add_argument("--provider", default="ollama", choices=["ollama", "openai", "anthropic"], help="LLM provider")
    parser.add_argument("--base-url", default="http://localhost:11434", help="LLM base URL")
    parser.add_argument("--api-key", default="", help="API key for OpenAI-compatible providers")
    parser.add_argument("--json-output", action="store_true", help="Output JSON results")
    parser.add_argument("--dry-run", action="store_true", help="Show scenarios without executing")
    parser.add_argument("--output-file", help="Save results to JSON file")
    parser.add_argument("--limit", type=int, help="Limit number of scenarios to run")
    args = parser.parse_args()

    # Select scenarios
    if args.id:
        scenario = get_scenario(args.id)
        if not scenario:
            print(f"Unknown scenario ID: {args.id}", file=sys.stderr)
            sys.exit(1)
        scenarios = [scenario]
    elif args.category:
        scenarios = get_scenarios_by_category(args.category)
        if not scenarios:
            print(f"No scenarios for category: {args.category}", file=sys.stderr)
            sys.exit(1)
    elif args.difficulty:
        scenarios = get_scenarios_by_difficulty(args.difficulty)
        if not scenarios:
            print(f"No scenarios for difficulty: {args.difficulty}", file=sys.stderr)
            sys.exit(1)
    else:
        scenarios = SCENARIOS

    if args.limit:
        scenarios = scenarios[:args.limit]

    # Dry run
    if args.dry_run:
        print(f"\nBridge Builder Test Suite -- {len(scenarios)} scenarios\n")
        for s in scenarios:
            kot = "Y" if s["kernel_of_truth"] else "N"
            print(f"  [{s['id']}] ({s['difficulty']:6s}) (KoT:{kot}) {s['claim'][:70]}...")
        print(f"\nRun without --dry-run to execute against {args.provider}/{args.model}")
        return

    # Create LLM client
    client = create_client(
        provider=args.provider,
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key or None,
    )

    if not client.check_available():
        print(
            f"Error: {args.provider} not available or model '{args.model}' not found.\n"
            f"Ensure the LLM service is running at {args.base_url}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nBridge Builder Test Suite")
    print(f"Provider: {args.provider} | Model: {args.model} | Base URL: {args.base_url}")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Starting...\n")

    orchestrator = Orchestrator(client)
    results = []

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] Running scenario {scenario['id']}...")
        result = run_scenario(orchestrator, scenario, verbose=not args.json_output)
        results.append(result)

    # Summary
    if not args.json_output:
        print_summary(results)

    # JSON output
    if args.json_output:
        # Strip full_result for cleaner JSON output
        clean_results = []
        for r in results:
            clean = {k: v for k, v in r.items() if k != "full_result"}
            clean_results.append(clean)
        print(json.dumps(clean_results, indent=2))

    # Save to file
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")

    # Exit with non-zero if average score is below threshold
    scores = [r["evaluation"]["overall_score"] for r in results if "error" not in r]
    if scores and (sum(scores) / len(scores)) < 0.4:
        sys.exit(1)


if __name__ == "__main__":
    main()
