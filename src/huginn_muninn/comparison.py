"""Multi-model comparison engine for adversarial analysis."""
from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from huginn_muninn.llm import extract_json_from_response
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt, sanitize_for_prompt

if TYPE_CHECKING:
    from huginn_muninn.db import HuginnDB
    from huginn_muninn.model_registry import ModelRegistry

log = logging.getLogger(__name__)


class ComparisonEngine:
    """Run the same claim through multiple models and compare results."""

    def __init__(
        self,
        registry: ModelRegistry,
        db: HuginnDB,
        max_workers: int = 4,
    ):
        self._registry = registry
        self._db = db
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="compare-worker"
        )

    def compare(
        self,
        claim: str,
        model_names: list[str],
        method: str = "check",
        reconcile: bool = False,
    ) -> dict:
        """Run claim through each model, compare, optionally reconcile."""
        results = {}
        futures = {}
        for name in model_names:
            future = self._executor.submit(self._run_single, claim, name, method)
            futures[future] = name

        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                log.error("Model %s failed: %s", name, e)
                results[name] = {"error": str(e)[:500]}

        comparison = _compute_comparison(results, method)

        reconciliation = None
        if reconcile:
            reconcile_model = self._registry.get_reconcile_model()
            if reconcile_model:
                reconciliation = self._reconcile(claim, results, reconcile_model)

        output = {
            "claim": claim,
            "method": method,
            "models": model_names,
            "results": results,
            "comparison": comparison,
        }
        if reconciliation:
            output["reconciliation"] = reconciliation

        # Store in DB
        comp_id = self._db.store_comparison(
            claim=claim,
            models=model_names,
            method=method,
            results=results,
            comparison={**comparison, **({"reconciliation": reconciliation} if reconciliation else {})},
        )
        output["id"] = comp_id
        return output

    def _run_single(self, claim: str, model_name: str, method: str) -> dict:
        """Run a single model's analysis. Client is created and closed per-call."""
        client = self._registry.create_client(model_name)
        try:
            if method == "check":
                return self._run_check(claim, client)
            elif method == "analyze":
                from huginn_muninn.orchestrator import Orchestrator
                orch = Orchestrator(client)
                return orch.run(claim)
            else:
                raise ValueError(f"Unsupported comparison method: {method}")
        finally:
            client.close()

    def _run_check(self, claim: str, client) -> dict:
        """Run Method 1 (check) with a given client."""
        p1_raw = client.generate(build_pass1_prompt(claim))
        p1_data = extract_json_from_response(p1_raw)
        p2_raw = client.generate(build_pass2_prompt(claim, json.dumps(p1_data)))
        return extract_json_from_response(p2_raw)

    def _reconcile(self, claim: str, results: dict, reconcile_model: str) -> dict:
        """Meta-review: ask a reconciliation model to synthesize all results."""
        client = self._registry.create_client(reconcile_model)
        try:
            prompt = _build_reconcile_prompt(claim, results)
            raw = client.generate(prompt)
            return extract_json_from_response(raw)
        except Exception as e:
            log.error("Reconciliation failed: %s", e)
            return {"error": str(e)[:500]}
        finally:
            client.close()

    def shutdown(self):
        self._executor.shutdown(wait=False, cancel_futures=True)


def _compute_comparison(results: dict, method: str) -> dict:
    """Pure function: compute agreement metrics from model results."""
    verdicts = {}
    confidence_values = {}

    for model, result in results.items():
        if "error" in result:
            verdicts[model] = "error"
            continue

        if method == "check":
            verdicts[model] = result.get("verdict", "unknown")
            conf = result.get("confidence")
            if conf is not None:
                confidence_values[model] = conf
        else:
            verdicts[model] = f"confidence_{result.get('overall_confidence', 0):.2f}"
            conf = result.get("overall_confidence")
            if conf is not None:
                confidence_values[model] = conf

    # Compute agreement
    verdict_set = {v for v in verdicts.values() if v != "error"}
    verdict_agreement = len(verdict_set) <= 1 and len(verdict_set) > 0

    # Compute spread
    confidence_spread = 0.0
    if len(confidence_values) >= 2:
        vals = list(confidence_values.values())
        confidence_spread = round(max(vals) - min(vals), 3)

    # Key differences
    key_differences = []
    models_list = list(verdicts.keys())
    for i in range(len(models_list)):
        for j in range(i + 1, len(models_list)):
            m1, m2 = models_list[i], models_list[j]
            if verdicts[m1] != verdicts[m2]:
                key_differences.append(
                    f"{m1} ({verdicts[m1]}) vs {m2} ({verdicts[m2]})"
                )

    return {
        "verdict_agreement": verdict_agreement,
        "verdicts": verdicts,
        "confidence_spread": confidence_spread,
        "confidence_values": confidence_values,
        "key_differences": key_differences,
    }


def _build_reconcile_prompt(claim: str, results: dict) -> str:
    """Build a meta-review prompt for reconciliation."""
    safe_claim = sanitize_for_prompt(claim)
    analyses = []
    for model, result in results.items():
        if "error" not in result:
            safe_result = sanitize_for_prompt(json.dumps(result, indent=2)[:2000])
            analyses.append(f"<model name=\"{sanitize_for_prompt(model)}\">\n{safe_result}\n</model>")
    analyses_text = "\n\n".join(analyses)

    return f"""You are a meta-reviewer. Given independent analyses of the same claim by different models, produce a reconciled verdict.

<claim>{safe_claim}</claim>

{analyses_text}

Respond in JSON:
{{
  "meta_verdict": "true | mostly_true | mixed | mostly_false | false | insufficient_evidence",
  "meta_confidence": 0.0 to 1.0,
  "reasoning": "Why you chose this verdict given the different analyses",
  "agreements": ["Points where models agree"],
  "disagreements": ["Points where models disagree and why"]
}}"""
