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
