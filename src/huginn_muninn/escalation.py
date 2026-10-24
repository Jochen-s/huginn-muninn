"""SNARC-like escalation scoring for Method 2 promotion."""
from __future__ import annotations

from huginn_muninn.models import EscalationScore

# SNARC dimensions: Surprise, Novelty, Arousal, Reward, Conflict
_COMPLEXITY_SCORES = {
    "simple": 0.1,
    "moderate": 0.3,
    "complex": 0.6,
    "multi_actor": 0.8,
}


def compute_escalation(
    complexity: str,
    polarization: bool,
    confidence: float,
    groups_involved: list[str],
) -> EscalationScore:
    """Compute escalation score based on SNARC-like dimensions."""
    complexity_score = _COMPLEXITY_SCORES.get(complexity, 0.3)
    polarization_score = 0.4 if polarization else 0.0
    uncertainty_score = max(0, 1.0 - confidence) * 0.6
    actor_score = min(len(groups_involved) * 0.2, 0.6)

    raw = (complexity_score + polarization_score + uncertainty_score + actor_score) / 2
    score = min(max(raw, 0.0), 1.0)
    should_escalate = score > 0.5 or confidence < 0.4

    reasons = []
    if complexity in ("complex", "multi_actor"):
        reasons.append(f"{complexity} claim structure")
    if polarization:
        reasons.append("polarization detected")
    if confidence < 0.4:
        reasons.append(f"low confidence ({confidence:.2f})")
    if len(groups_involved) > 1:
        reasons.append(f"{len(groups_involved)} groups involved")

    reason = "; ".join(reasons) if reasons else "Low complexity, single-claim"

    return EscalationScore(score=round(score, 3), should_escalate=should_escalate, reason=reason)


def should_escalate_verdict(verdict: dict) -> tuple[bool, str]:
    """Decide Method 2 escalation for a Method 1 verdict dict.

    Combines the LLM's own `escalation.should_escalate` with the deterministic
    gate above as a floor: the LLM may ask for escalation on its own judgement,
    and low reported confidence escalates regardless of that judgement. Method 1
    output carries no complexity, polarization or group fields, so of the four
    SNARC terms only the confidence term can bind here; the gate is therefore a
    floor, not a replacement. Until 2026-09-03 `compute_escalation` had no
    caller and every escalation decision was the model's self-report."""
    llm_flag = bool((verdict.get("escalation") or {}).get("should_escalate", False))
    try:
        confidence = float(verdict.get("confidence", 1.0))
    except (TypeError, ValueError):
        confidence = 1.0
    deterministic = compute_escalation(
        complexity="moderate",
        polarization=False,
        confidence=confidence,
        groups_involved=[],
    )
    if llm_flag and deterministic.should_escalate:
        return True, f"model self-report; deterministic gate ({deterministic.reason})"
    if llm_flag:
        return True, "model self-report"
    if deterministic.should_escalate:
        return True, f"deterministic gate ({deterministic.reason})"
    return False, "neither model self-report nor deterministic gate"
