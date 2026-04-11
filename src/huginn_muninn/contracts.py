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
    # Sprint 2 P2-7: triage priority for the verification stage. Defaults to
    # "low" so that failing to triage never inflates verification debt. The
    # anti-inflation clause ("marking everything critical defeats the triage
    # purpose") lives in the Decomposer prompt, not in the schema. Older LLM
    # outputs without this key still parse; the literal discipline is enforced
    # strictly to catch LLM drift toward synonyms like "urgent" / "immediate".
    verification_priority: Annotated[
        Literal["critical", "high", "low"],
        BeforeValidator(_first_pipe_value),
    ] = "low"

    @model_validator(mode="after")
    def _triage_coherence(self) -> "SubClaim":
        """Sprint 2 PR 2 / Holodeck I-roles mitigation:
        verifiable=False + verification_priority="critical" is an incoherent
        combination. A sub-claim the Decomposer has marked as structurally
        non-verifiable cannot simultaneously be a critical verification
        target, since there is nothing for the downstream pipeline to
        verify. Prompt-level discipline is insufficient enforcement; a
        future model swap or a prompt rewrite could silently break the
        invariant. The schema-level guard downgrades the incoherent
        combination to "high" rather than raising, so that a single
        Decomposer hallucination does not take down the whole pipeline.
        This mirrors the "degrade, do not crash" discipline of the Sprint 1
        orchestrator fallback path.
        """
        if self.verifiable is False and self.verification_priority == "critical":
            # Downgrade rather than raise: a single incoherent sub-claim
            # must not degrade the entire analysis.
            object.__setattr__(self, "verification_priority", "high")
        return self


class DecomposerOutput(BaseModel):
    sub_claims: list[SubClaim] = Field(..., min_length=1)
    original_claim: str
    complexity: Annotated[Literal["simple", "moderate", "complex", "multi_actor"], BeforeValidator(_first_pipe_value)]
    # Qualitative hypothesis-space saturation signal (Briggs, Danyk, Weiss 2026
    # cognitive-warfare taxonomy). Deliberately qualitative: literal density-matrix
    # formalism rejected as false precision without a concrete Hilbert space.
    # All three fields default so older LLM outputs still parse.
    hypothesis_crowding: Annotated[
        Literal["low", "medium", "high"],
        BeforeValidator(_first_pipe_value),
    ] = "low"
    manipulation_vector_density: float = Field(default=0.0, ge=0.0, le=1.0)
    complexity_explosion_flag: bool = False


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
    mutation_type: Annotated[Literal["distortion", "amplification", "recontextualization", "fabrication", "ideological_migration", "inversion"], BeforeValidator(_first_pipe_value)]
    source: str
    # Relay classification for narrative mutation tracking. Default "ambiguous"
    # prevents speculation about intent when explicit signals are absent.
    relay_type: Annotated[
        Literal["knowing", "unknowing", "ambiguous"],
        BeforeValidator(_first_pipe_value),
    ] = "ambiguous"


class TemporalContext(BaseModel):
    era: str
    date_range: str
    dominant_framing: str
    key_actors: list[str] = Field(default_factory=list)
    power_context: str = ""
    irony_or_inversion: str = ""


class TracerOutput(BaseModel):
    origins: list[OriginEntry]
    mutations: list[NarrativeMutation] = Field(default_factory=list)
    temporal_context: list[TemporalContext] = Field(default_factory=list)
    # --- Gorgon Trap assimilation (P1 #4) ---
    # Source TYPES missing from the claim/context. Capped at 3 to prevent
    # hallucination sprawl. Empty default; the "missing from context" framing
    # (vs. speculative "suppressed") lives in the Tracer prompt, not the schema.
    notable_omissions: list[str] = Field(default_factory=list, max_length=3)


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


class TechniqueReveal(BaseModel):
    technique: str
    how_it_works: str
    used_by: str
    where_used_here: str
    historical_precedent: str = ""
    pattern_type: Annotated[
        Literal["isolated", "repeated", "systematic"],
        BeforeValidator(_first_pipe_value),
    ] = "isolated"


class BridgeOutput(BaseModel):
    universal_needs: list[str] = Field(..., min_length=1)
    issue_overlap: Annotated[str, BeforeValidator(_null_to_empty_str)]
    narrative_deconstruction: Annotated[str, BeforeValidator(_null_to_empty_str)]
    consensus_explanation: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    inferential_gap: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    feasibility_check: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    commercial_motives: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    techniques_revealed: list[TechniqueReveal] = Field(default_factory=list)
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
    # --- Gorgon Trap assimilation (P1 #3) ---
    # Frame capture risk. The term is deliberately chosen over "verification
    # trap" to avoid priming the Auditor against legitimate fact-checking:
    # frame capture is when upstream agents adopt the claim's framing without
    # independent restatement, which is orthogonal to whether the claim was
    # fact-checked. Cognitive-warfare findings are routed through the existing
    # AuditFinding.category values ("manipulation" / "quality") with description
    # prefixes [cognitive_warfare] / [frame_capture] -- the category enum is
    # intentionally not expanded here to avoid breaking downstream renderers.
    frame_capture_risk: Annotated[
        Literal["none", "possible", "high"],
        BeforeValidator(_first_pipe_value),
    ] = "none"
    frame_capture_evidence: str = ""

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
