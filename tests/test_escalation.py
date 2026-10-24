"""Tests for SNARC-like escalation scoring."""
import pytest

from huginn_muninn.escalation import compute_escalation
from huginn_muninn.models import EscalationScore


class TestEscalation:
    def test_simple_factual_no_escalation(self):
        result = compute_escalation(
            complexity="simple",
            polarization=False,
            confidence=0.9,
            groups_involved=[],
        )
        assert not result.should_escalate
        assert result.score < 0.5

    def test_multi_actor_escalates(self):
        result = compute_escalation(
            complexity="multi_actor",
            polarization=True,
            confidence=0.5,
            groups_involved=["group_a", "group_b"],
        )
        assert result.should_escalate
        assert result.score > 0.6

    def test_low_confidence_escalates(self):
        result = compute_escalation(
            complexity="moderate",
            polarization=False,
            confidence=0.3,
            groups_involved=[],
        )
        assert result.should_escalate

    def test_polarized_simple_claim(self):
        result = compute_escalation(
            complexity="simple",
            polarization=True,
            confidence=0.7,
            groups_involved=["left", "right"],
        )
        # Polarization alone may warrant escalation
        assert result.score > 0.4


class TestShouldEscalateVerdict:
    """The deterministic gate is wired in as a floor under the LLM self-report."""

    def test_llm_flag_alone_escalates(self):
        from huginn_muninn.escalation import should_escalate_verdict
        verdict = {"confidence": 0.9, "escalation": {"should_escalate": True, "score": 0.8, "reason": "x"}}
        escalate, reason = should_escalate_verdict(verdict)
        assert escalate is True
        assert "self-report" in reason

    def test_low_confidence_escalates_even_when_llm_says_no(self):
        from huginn_muninn.escalation import should_escalate_verdict
        verdict = {"confidence": 0.3, "escalation": {"should_escalate": False, "score": 0.1, "reason": "fine"}}
        escalate, reason = should_escalate_verdict(verdict)
        assert escalate is True
        assert "low confidence" in reason

    def test_confident_and_llm_no_does_not_escalate(self):
        from huginn_muninn.escalation import should_escalate_verdict
        verdict = {"confidence": 0.8, "escalation": {"should_escalate": False, "score": 0.1, "reason": "fine"}}
        escalate, _ = should_escalate_verdict(verdict)
        assert escalate is False

    def test_missing_fields_do_not_crash(self):
        from huginn_muninn.escalation import should_escalate_verdict
        escalate, _ = should_escalate_verdict({})
        assert escalate is False
