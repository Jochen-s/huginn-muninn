"""Huginn & Muninn CLI -- fact-checking with common humanity."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import httpx

from pydantic import ValidationError

from huginn_muninn.config import get_settings
from huginn_muninn.db import HuginnDB
from huginn_muninn.llm import OllamaClient, extract_json_from_response
from huginn_muninn.models import ClaimInput, VerdictOutput
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt

_VERSION = "0.1.0"


def _db_path() -> Path:
    return get_settings().db_path


@click.group()
@click.version_option(_VERSION, prog_name="Huginn & Muninn")
def main():
    """Huginn & Muninn -- fact-checking that finds common ground."""


@main.command()
@click.argument("claim")
@click.option("--model", default="qwen3.5:9b", help="Ollama model name")
@click.option("--json-output", is_flag=True, help="Output raw JSON instead of formatted text")
@click.option("--no-cache", is_flag=True, help="Skip cache lookup")
@click.option("--auto-escalate", is_flag=True, help="Auto-run Method 2 if escalation recommended")
def check(claim: str, model: str, json_output: bool, no_cache: bool, auto_escalate: bool):
    """Fact-check a claim with Common Humanity analysis."""
    # Validate claim input
    try:
        ClaimInput(text=claim)
    except ValidationError as e:
        click.echo(f"Invalid claim: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)

    with HuginnDB(_db_path()) as db:
        # Check cache
        verdict_dict = None
        if not no_cache:
            cached = db.get_cached_verdict(claim)
            if cached:
                needs_escalation = (
                    auto_escalate
                    and cached.get("escalation", {}).get("should_escalate")
                )
                if not needs_escalation:
                    if json_output:
                        click.echo(json.dumps(cached, indent=2))
                    else:
                        _print_verdict(cached)
                    return
                # Cached verdict needs escalation — reuse it, skip Method 1
                verdict_dict = cached

        # Connect to Ollama for Method 1 and/or Method 2
        m2_result = None
        with OllamaClient(model=model) as client:
            if not client.check_available():
                click.echo(
                    f"Error: Ollama not available or model '{model}' not found.\n"
                    f"Install Ollama and run: ollama pull {model}",
                    err=True,
                )
                sys.exit(1)

            # Run Method 1 if not served from cache
            if verdict_dict is None:
                try:
                    click.echo("Pass 1: Gathering evidence...", err=True)
                    p1_prompt = build_pass1_prompt(claim)
                    p1_raw = client.generate(p1_prompt)
                    p1_data = extract_json_from_response(p1_raw)

                    click.echo("Pass 2: Analyzing verdict and common ground...", err=True)
                    p2_prompt = build_pass2_prompt(claim, json.dumps(p1_data))
                    p2_raw = client.generate(p2_prompt)
                    p2_data = extract_json_from_response(p2_raw)
                except httpx.ReadTimeout:
                    click.echo(
                        "Error: LLM request timed out. The model may still be loading.\n"
                        "Try again in a moment, or use a smaller model with --model.",
                        err=True,
                    )
                    sys.exit(1)
                except httpx.HTTPError as e:
                    click.echo(f"Error communicating with Ollama: {e}", err=True)
                    sys.exit(1)

                try:
                    output = VerdictOutput(claim=claim, **p2_data)
                except ValidationError as e:
                    click.echo(
                        f"Error: LLM response did not match expected schema.\n{e}",
                        err=True,
                    )
                    sys.exit(1)

                verdict_dict = output.model_dump(mode="json")
                db.store_verdict(claim, verdict_dict)

            # Escalate to Method 2 if needed
            if auto_escalate and verdict_dict.get("escalation", {}).get("should_escalate"):
                click.echo(
                    "\nEscalation recommended -- running Method 2 analysis...",
                    err=True,
                )
                try:
                    from huginn_muninn.orchestrator import Orchestrator
                    orch = Orchestrator(client)
                    m2_result = orch.run(claim)
                    db.store_analysis(claim, m2_result)
                    if m2_result.get("degraded"):
                        click.echo(
                            f"Warning: Method 2 degraded -- {m2_result.get('degraded_reason', 'unknown')}",
                            err=True,
                        )
                except httpx.ReadTimeout:
                    click.echo(
                        "Warning: Method 2 timed out. Method 1 result shown below.",
                        err=True,
                    )
                except httpx.HTTPError as e:
                    click.echo(f"Warning: Method 2 failed ({e}). Method 1 result shown below.", err=True)
                except Exception as e:
                    click.echo(f"Warning: Method 2 error ({e}). Method 1 result shown below.", err=True)

        # Output
        if json_output:
            if m2_result:
                click.echo(json.dumps({"method_1": verdict_dict, "method_2": m2_result}, indent=2))
            else:
                click.echo(json.dumps(verdict_dict, indent=2))
        else:
            _print_verdict(verdict_dict)
            if m2_result:
                click.echo("\n  >> Escalated to Method 2:\n")
                _print_analysis(m2_result)


@main.command()
@click.argument("claim")
@click.option("--type", "feedback_type", required=True, type=click.Choice(["agree", "disagree", "partial", "unsure"]))
@click.option("--comment", default=None)
def feedback(claim: str, feedback_type: str, comment: str | None):
    """Submit feedback on a verdict to help improve the system."""
    with HuginnDB(_db_path()) as db:
        cached = db.get_cached_verdict(claim)
        verdict = cached.get("verdict", "unknown") if cached else "unknown"
        db.store_feedback(claim, verdict, feedback_type, comment)
    click.echo("Feedback recorded. Thank you -- this helps Huginn & Muninn improve.")


@main.command()
@click.argument("claim")
@click.option("--model", default="qwen3.5:9b", help="Ollama model name")
@click.option("--json-output", is_flag=True, help="Output raw JSON instead of formatted text")
@click.option("--no-cache", is_flag=True, help="Skip cache lookup")
def analyze(claim: str, model: str, json_output: bool, no_cache: bool):
    """Deep analysis of a claim using Method 2 (6-agent pipeline)."""
    from huginn_muninn.orchestrator import Orchestrator

    try:
        ClaimInput(text=claim)
    except ValidationError as e:
        click.echo(f"Invalid claim: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)

    with HuginnDB(_db_path()) as db:
        # Check cache
        if not no_cache:
            cached = db.get_cached_analysis(claim)
            if cached:
                if json_output:
                    click.echo(json.dumps(cached, indent=2))
                else:
                    _print_analysis(cached)
                return

        with OllamaClient(model=model) as client:
            if not client.check_available():
                click.echo(
                    f"Error: Ollama not available or model '{model}' not found.\n"
                    f"Install Ollama and run: ollama pull {model}",
                    err=True,
                )
                sys.exit(1)

            click.echo("Method 2: Running 6-agent analysis pipeline...", err=True)
            try:
                orch = Orchestrator(client)
                result = orch.run(claim)
            except httpx.ReadTimeout:
                click.echo(
                    "Error: LLM request timed out.\n"
                    "Method 2 requires multiple LLM calls. Try a smaller model or use 'huginn check' for quick analysis.",
                    err=True,
                )
                sys.exit(1)
            except httpx.HTTPError as e:
                click.echo(f"Error communicating with Ollama: {e}", err=True)
                sys.exit(1)

        db.store_analysis(claim, result)

    if result.get("degraded"):
        click.echo(f"Warning: Analysis degraded -- {result.get('degraded_reason', 'unknown')}", err=True)

    if json_output:
        from huginn_muninn.projection import project_analysis
        click.echo(json.dumps(project_analysis(result), indent=2))
    else:
        _print_analysis(result)


def _print_analysis(data: dict):
    """Pretty-print a Method 2 analysis for terminal output."""
    click.echo(f"\n{'='*60}")
    click.echo(f"  METHOD 2 ANALYSIS")
    click.echo(f"  Confidence: {data.get('overall_confidence', 0):.0%}")
    if data.get("degraded"):
        click.echo(f"  [DEGRADED] {data.get('degraded_reason', '')}")
    click.echo(f"{'='*60}")

    decomp = data.get("decomposition", {})
    if decomp.get("sub_claims"):
        click.echo(f"\n  SUB-CLAIMS ({decomp.get('complexity', 'unknown')}):")
        for sc in decomp["sub_claims"]:
            click.echo(f"    [{sc.get('type', '?')}] {sc.get('text', '')}")

    intel = data.get("intelligence", {})
    if intel.get("actors"):
        click.echo("\n  ACTORS:")
        for a in intel["actors"]:
            click.echo(f"    - {a.get('name', '?')} ({a.get('type', '?')}) -- {a.get('motivation', '')}")

    ttps = data.get("ttps", {})
    if ttps.get("ttp_matches"):
        click.echo("\n  DISARM TTPs:")
        for t in ttps["ttp_matches"]:
            click.echo(f"    - [{t.get('disarm_id', '?')}] {t.get('technique_name', '')} (conf: {t.get('confidence', 0):.0%})")

    bridge = data.get("bridge", {})
    if bridge.get("universal_needs"):
        click.echo(f"\n{'- '*30}")
        click.echo("  COMMON GROUND")
        click.echo(f"{'- '*30}")
        click.echo(f"\n  SHARED NEEDS: {', '.join(bridge.get('universal_needs', []))}")
        if bridge.get("issue_overlap"):
            click.echo(f"  OVERLAP: {bridge['issue_overlap']}")
        if bridge.get("perception_gap"):
            click.echo(f"  PERCEPTION GAP: {bridge['perception_gap']}")
        if bridge.get("reframe"):
            click.echo(f"  REFRAME: {bridge['reframe']}")
        if bridge.get("socratic_dialogue"):
            click.echo("\n  SOCRATIC DIALOGUE:")
            for i, round_text in enumerate(bridge["socratic_dialogue"], 1):
                click.echo(f"    Round {i}: {round_text}")

        # Sprint 3 PR 1: Sprint 2 Bridge scoped diagnostics
        posture = bridge.get("communication_posture", "direct_correction")
        if posture != "direct_correction":
            label = posture.replace("_", " ").title()
            click.echo(f"\n  POSTURE: {label}")
        if bridge.get("pattern_density_warning"):
            click.echo("  WARNING: High pattern density detected in claim structure")
        vacuum = bridge.get("vacuum_filled_by", "")
        if vacuum and vacuum != "[scope:redacted-named-entity]":
            click.echo(f"  VACUUM FILLED BY: {vacuum}")
        prebunk = bridge.get("prebunking_note", "")
        if prebunk and prebunk != "[scope:redacted-named-entity]":
            click.echo(f"  PREBUNKING NOTE: {prebunk}")

    audit = data.get("audit", {})
    if audit:
        v = audit.get("verdict", "unknown").upper()
        click.echo(f"\n  AUDIT: {v}")
        if audit.get("findings"):
            for finding in audit["findings"]:
                click.echo(f"    [{finding.get('severity', '?')}] {finding.get('description', '')}")

    click.echo(f"\n{'='*60}\n")


def _print_verdict(data: dict):
    """Pretty-print a verdict for terminal output."""
    v = data.get("verdict", "unknown").upper().replace("_", " ")
    conf = data.get("confidence", 0)
    click.echo(f"\n{'='*60}")
    click.echo(f"  VERDICT: {v}")
    click.echo(f"  CONFIDENCE: {conf:.0%}")
    click.echo(f"{'='*60}")

    if data.get("evidence_for"):
        click.echo("\n  EVIDENCE FOR:")
        for e in data["evidence_for"]:
            click.echo(f"    - {e.get('text', '')}")

    if data.get("evidence_against"):
        click.echo("\n  EVIDENCE AGAINST:")
        for e in data["evidence_against"]:
            click.echo(f"    - {e.get('text', '')}")

    if data.get("unknowns"):
        click.echo("\n  UNKNOWNS:")
        for u in data["unknowns"]:
            click.echo(f"    - {u}")

    if data.get("abstain_reason"):
        click.echo(f"\n  NOTE: {data['abstain_reason']}")

    cg = data.get("common_ground", {})
    if cg:
        click.echo(f"\n{'- '*30}")
        click.echo("  COMMON GROUND")
        click.echo(f"{'- '*30}")
        if cg.get("shared_concern"):
            click.echo(f"\n  SHARED CONCERN: {cg['shared_concern']}")
        if cg.get("framing_technique") and cg["framing_technique"] != "none_detected":
            label = cg["framing_technique"].replace("_", " ").title()
            click.echo(f"\n  FRAMING TECHNIQUE: {label}")
            if cg.get("technique_explanation"):
                click.echo(f"  {cg['technique_explanation']}")
        if cg.get("reflection"):
            click.echo(f"\n  REFLECTION: {cg['reflection']}")

    esc = data.get("escalation", {})
    if esc and esc.get("should_escalate"):
        click.echo(f"\n  >> This claim may benefit from deeper analysis (Method 2)")
        click.echo(f"     Reason: {esc.get('reason', '')}")

    click.echo(f"\n{'='*60}\n")
