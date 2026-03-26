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
