"""Data models for Huginn & Muninn Method 1 I/O contracts."""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

FramingTechnique = Literal[
    "false_dichotomy",
    "emotional_amplification",
    "scapegoating",
    "false_equivalence",
    "cherry_picking",
    "appeal_to_fear",
    "manufactured_consensus",
    "whataboutism",
    "none_detected",
]


class Verdict(str, Enum):
    TRUE = "true"
    MOSTLY_TRUE = "mostly_true"
    MIXED = "mixed"
    MOSTLY_FALSE = "mostly_false"
    FALSE = "false"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class JobRequest(BaseModel):
    """Async job submission request."""

    claim: str = Field(..., min_length=1, max_length=2000)
    method: Literal["check", "analyze", "check-and-escalate"] = "check"
    callback_url: str | None = Field(
        default=None,
        max_length=2000,
        description="URL to POST results to on completion",
    )
    session_id: int | None = None
    no_cache: bool = False
    deep_sources: bool = False


class JobResponse(BaseModel):
    """Response after job submission."""

    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Full job status response."""

    id: str
    claim: str
    method: str
    status: str
    result: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str


class ClaimInput(BaseModel):
    """User-submitted claim for fact-checking."""

    text: str = Field(..., min_length=1, max_length=2000)
    context: str | None = Field(
        default=None,
        description="Where/when the claim was encountered",
    )
    language: str = Field(default="en", max_length=5)


class Evidence(BaseModel):
    """A piece of evidence for or against a claim."""

    text: str
    source_url: str
    source_tier: int = Field(..., ge=1, le=4)
    supports_claim: bool
    publication_date: str | None = None


class CommonGround(BaseModel):
    """Common Humanity layer output -- always present in every verdict."""

    shared_concern: str = Field(
        ..., description="Universal human need at stake, framed empathetically"
    )
    framing_technique: FramingTechnique = Field(
        ..., description="Named manipulation technique (maps to DISARM TTP)"
    )
    technique_explanation: str = Field(
        ..., description="How the technique works, as shared observation"
    )
    reflection: str = Field(
        ..., description="Socratic question that plants a seed of insight"
    )

    @field_validator("reflection")
    @classmethod
    def reflection_must_be_question(cls, v: str) -> str:
        if not v.rstrip().endswith("?"):
            msg = "Reflection must be a question (end with '?')"
            raise ValueError(msg)
        return v


class EscalationScore(BaseModel):
    """SNARC-like scoring for Method 2 escalation."""

    score: float = Field(..., ge=0.0, le=1.0)
    should_escalate: bool
    reason: str


class VerdictOutput(BaseModel):
    """Complete Method 1 output including Common Ground."""

    claim: str
    verdict: Verdict
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_for: list[Evidence]
    evidence_against: list[Evidence]
    unknowns: list[str]
    common_ground: CommonGround
    escalation: EscalationScore
    abstain_reason: str | None = None
