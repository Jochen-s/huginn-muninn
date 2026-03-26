"""Inter-agent Pydantic contracts for Method 2 pipeline."""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field, model_validator


def _first_pipe_value(v: object) -> object:
    """Take first value when LLM returns pipe-separated enum like 'a|b'."""
    if isinstance(v, str) and "|" in v:
        return v.split("|")[0].strip()
    return v


# --- Analysis Input ---

class AnalysisInput(BaseModel):
    """Input to the Method 2 pipeline."""
    claim: str = Field(..., min_length=1, max_length=5000)
    context: str | None = None
    language: str = Field(default="en", max_length=5)


# --- Claim Decomposer ---

class SubClaimType(str, Enum):
    FACTUAL = "factual"
    OPINION = "opinion"
    PREDICTION = "prediction"
    VALUE = "value"
    CAUSAL = "causal"


class SubClaim(BaseModel):
    text: str = Field(..., min_length=1)
    type: Annotated[SubClaimType, BeforeValidator(_first_pipe_value)]
    verifiable: bool = True


class DecomposerOutput(BaseModel):
    sub_claims: list[SubClaim] = Field(..., min_length=1)
    original_claim: str
    complexity: Annotated[Literal["simple", "moderate", "complex", "multi_actor"], BeforeValidator(_first_pipe_value)]


# --- Origin Tracer ---

class OriginEntry(BaseModel):
    sub_claim: str
    earliest_source: str
    earliest_date: str | None = None
    source_tier: int = Field(..., ge=1, le=4)
    propagation_path: list[str] = Field(default_factory=list)


class NarrativeMutation(BaseModel):
    original: str
    mutated: str
    mutation_type: Annotated[Literal["distortion", "amplification", "recontextualization", "fabrication"], BeforeValidator(_first_pipe_value)]
    source: str


class TracerOutput(BaseModel):
    origins: list[OriginEntry]
    mutations: list[NarrativeMutation] = Field(default_factory=list)


# --- Intelligence Mapper ---

class Actor(BaseModel):
    name: str
    type: Annotated[Literal["state", "media", "influencer", "organization", "bot_network", "unknown"], BeforeValidator(_first_pipe_value)]
    motivation: str
    credibility: float = Field(..., ge=0.0, le=1.0)
    evidence: str = ""


class ActorRelation(BaseModel):
    source_actor: str
    target_actor: str
    relation_type: Annotated[Literal["amplifies", "funds", "coordinates", "opposes", "cites"], BeforeValidator(_first_pipe_value)]
    confidence: float = Field(..., ge=0.0, le=1.0)


class MapperOutput(BaseModel):
    actors: list[Actor]
    relations: list[ActorRelation] = Field(default_factory=list)
    narrative_summary: str


# --- TTP Classifier ---

class TTPMatch(BaseModel):
    disarm_id: str
    technique_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: str


class ClassifierOutput(BaseModel):
    ttp_matches: list[TTPMatch]
    primary_tactic: Annotated[Literal["Plan", "Prepare", "Execute", "Assess"], BeforeValidator(_first_pipe_value)]


# --- Bridge Builder ---

def _null_to_empty_str(v: object) -> object:
    """Convert None to empty string for optional text fields."""
    return "" if v is None else v


class BridgeOutput(BaseModel):
    universal_needs: list[str] = Field(..., min_length=1)
    issue_overlap: Annotated[str, BeforeValidator(_null_to_empty_str)]
    narrative_deconstruction: Annotated[str, BeforeValidator(_null_to_empty_str)]
    inferential_gap: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    feasibility_check: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    commercial_motives: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    perception_gap: Annotated[str, BeforeValidator(_null_to_empty_str)]
    moral_foundations: dict[str, list[str]] = Field(default_factory=dict)
    reframe: Annotated[str, BeforeValidator(_null_to_empty_str)]
    socratic_dialogue: list[str] = Field(..., min_length=1, max_length=3)


# --- Adversarial Auditor ---

class AuditVerdict(str, Enum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"


class AuditFinding(BaseModel):
    category: Annotated[Literal["bias", "accuracy", "completeness", "manipulation", "quality"], BeforeValidator(_first_pipe_value)]
    severity: Annotated[Literal["low", "medium", "high", "critical"], BeforeValidator(_first_pipe_value)]
    description: str
    recommendation: str


class AuditorOutput(BaseModel):
    verdict: Annotated[AuditVerdict, BeforeValidator(_first_pipe_value)]
    findings: list[AuditFinding] = Field(default_factory=list)
    confidence_adjustment: float = Field(..., ge=-1.0, le=1.0)
    veto: bool = False
    summary: str

    @model_validator(mode="after")
    def veto_requires_fail(self) -> "AuditorOutput":
        if self.veto and self.verdict == AuditVerdict.PASS:
            msg = "veto=True is inconsistent with verdict='pass'"
            raise ValueError(msg)
        return self


# --- Final Output ---

class AnalysisReport(BaseModel):
    """Complete Method 2 output."""
    claim: str
    decomposition: DecomposerOutput
    origins: TracerOutput
    intelligence: MapperOutput
    ttps: ClassifierOutput
    bridge: BridgeOutput
    audit: AuditorOutput
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    method: Literal["method_2"] = "method_2"
    degraded: bool = False
    degraded_reason: str | None = None
