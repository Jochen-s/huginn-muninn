"""Tests for Huginn & Muninn data models."""
import pytest
from pydantic import ValidationError

from huginn_muninn.models import (
    ClaimInput,
    CommonGround,
    EscalationScore,
    Evidence,
    Verdict,
    VerdictOutput,
)


class TestClaimInput:
    def test_valid_claim(self):
        claim = ClaimInput(text="Vaccines cause autism")
        assert claim.text == "Vaccines cause autism"
        assert claim.context is None
        assert claim.language == "en"

    def test_empty_claim_rejected(self):
        with pytest.raises(ValidationError):
            ClaimInput(text="")

    def test_claim_with_context(self):
        claim = ClaimInput(
            text="GDP grew 5%",
            context="Shared on Facebook, 2024-01-15",
            language="en",
        )
        assert claim.context == "Shared on Facebook, 2024-01-15"


class TestEvidence:
    def test_evidence_with_source_tier(self):
        ev = Evidence(
            text="WHO states no link between vaccines and autism",
            source_url="https://who.int/factsheet",
            source_tier=1,
            supports_claim=False,
        )
        assert ev.source_tier == 1
        assert ev.supports_claim is False

    def test_tier_must_be_1_to_4(self):
        with pytest.raises(ValidationError):
            Evidence(
                text="test",
                source_url="https://example.com",
                source_tier=5,
                supports_claim=True,
            )


class TestCommonGround:
    def test_common_ground_fields(self):
        cg = CommonGround(
            shared_concern="Both sides want children to be healthy and safe",
            framing_technique="false_dichotomy",
            technique_explanation=(
                "This narrative presents vaccine safety as an all-or-nothing "
                "choice, hiding the shared goal of child health."
            ),
            reflection=(
                "What if both pro- and anti-vaccine parents are driven by "
                "the same love for their children?"
            ),
        )
        assert "children" in cg.shared_concern
        assert cg.framing_technique == "false_dichotomy"

    def test_reflection_must_be_question(self):
        with pytest.raises(ValidationError):
            CommonGround(
                shared_concern="test",
                framing_technique="test",
                technique_explanation="test",
                reflection="This is a statement not a question",
            )


class TestVerdictOutput:
    def test_full_verdict(self):
        output = VerdictOutput(
            claim="Vaccines cause autism",
            verdict=Verdict.MOSTLY_FALSE,
            confidence=0.85,
            evidence_for=[],
            evidence_against=[],
            unknowns=["Long-term studies beyond 20 years"],
            common_ground=CommonGround(
                shared_concern="Both sides want children healthy",
                framing_technique="emotional_amplification",
                technique_explanation="Uses fear to override nuance",
                reflection="What do parents on both sides actually want?",
            ),
            escalation=EscalationScore(
                score=0.3,
                should_escalate=False,
                reason="Low complexity, single-claim",
            ),
            abstain_reason=None,
        )
        assert output.verdict == Verdict.MOSTLY_FALSE
        assert output.confidence == 0.85
        assert output.common_ground.framing_technique == "emotional_amplification"

    def test_abstain_verdict(self):
        output = VerdictOutput(
            claim="Something unknowable",
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            confidence=0.2,
            evidence_for=[],
            evidence_against=[],
            unknowns=["Everything"],
            common_ground=CommonGround(
                shared_concern="Shared desire for clarity",
                framing_technique="none_detected",
                technique_explanation="No clear manipulation detected",
                reflection="What would help us find better evidence?",
            ),
            escalation=EscalationScore(
                score=0.8, should_escalate=True, reason="High uncertainty"
            ),
            abstain_reason="Insufficient verifiable sources available",
        )
        assert output.verdict == Verdict.INSUFFICIENT_EVIDENCE
        assert output.abstain_reason is not None
