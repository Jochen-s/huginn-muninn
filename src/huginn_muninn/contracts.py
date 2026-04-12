"""Inter-agent Pydantic contracts for Method 2 pipeline."""
from __future__ import annotations

import re
from enum import Enum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, BeforeValidator, Field, model_validator


def _first_pipe_value(v: object) -> object:
    """Take first value when LLM returns pipe-separated enum like 'a|b'."""
    if isinstance(v, str) and "|" in v:
        return v.split("|")[0].strip()
    return v


# Sprint 2 PR 3 Codex mitigation (High severity -- must-fix #1):
# `vacuum_filled_by` and `prebunking_note` on BridgeOutput are prompt-
# constrained to narrative patterns only -- never named publishers, never
# named individuals, never named organisations. The prompt says so and the
# Anti-Weaponization Charter Commitment 3 says so, but prompt discipline is
# insufficient enforcement: a future model swap could emit "The New York
# Times filled the expertise vacuum" and the schema would accept the toxic
# string. Codex Blind Spot PR 3: a policy guarantee masquerading as an
# implementation guarantee.
#
# The fix is a schema-level post-parse scrub that mirrors SubClaim's
# "degrade, do not crash" discipline: detect out-of-scope named-entity
# content and replace the offending field with a sanitized marker, rather
# than raising (a single Bridge emission must never crash the pipeline).
#
# Detection heuristic (deliberately conservative -- false positives scrub
# to a marker which is far safer than false negatives leaking a named
# publisher into downstream renderers):
#
#   1. Explicit publisher / outlet blocklist (common English-language
#      news and wire services that the charter must never name).
#   2. Known disinfo-ecosystem brands (outlets repeatedly named in
#      academic literature as venues for state-aligned narrative
#      laundering -- including these by name is precisely the charter
#      violation we are preventing).
#   3. Multi-word Capitalised Proper Noun sequences of length >= 2 that
#      are not common English sentence-start phrases. This is a fuzzy
#      signal so we combine it with a second guard: at least one token
#      must appear in a news-entity suffix list ("Times", "Post", "News",
#      "Journal", "Wire", "Agency", etc.) or the sequence must be three
#      or more capitalised tokens in a row.
#
# When the scrubber fires we log via the validation-failure marker path
# by setting a sentinel value the orchestrator can detect, so schema
# policy violations become visible at the production boundary rather than
# being silently rewritten.
_SCOPE_VIOLATION_MARKER = "[scope:redacted-named-entity]"

_NAMED_PUBLISHER_BLOCKLIST = (
    # Major English-language wire services and newspapers
    "new york times", "nyt", "washington post", "wall street journal",
    "wsj", "financial times", "reuters", "associated press", "ap news",
    "bloomberg", "bbc", "cnn", "fox news", "msnbc", "nbc news",
    "cbs news", "abc news", "the guardian", "daily mail", "the times",
    "the telegraph", "the independent", "usa today", "los angeles times",
    "chicago tribune", "the atlantic", "the new yorker", "politico",
    "axios", "vox", "huffpost", "buzzfeed", "breitbart", "the hill",
    # Broadcast networks commonly named in narrative-laundering
    # literature; inclusion here is not an accusation, it is a
    # charter-enforcement: NO named publisher, regardless of direction.
    "rt", "russia today", "sputnik", "tass", "xinhua", "cgtn",
    "press tv", "al jazeera", "dw", "france 24", "nhk",
    # Fact-check organisations (symmetry: charter blocks naming them too)
    "snopes", "politifact", "factcheck.org", "lead stories", "afp fact",
)

# Word-boundary-aware blocklist regex. Naive substring matching would
# false-positive on fragments like "rt" inside "report" or "dw" inside
# "downward". We precompile a single alternation with \b anchors.
_BLOCKLIST_RE = re.compile(
    r"(?<![a-z0-9])(?:"
    + "|".join(re.escape(b) for b in sorted(_NAMED_PUBLISHER_BLOCKLIST, key=len, reverse=True))
    + r")(?![a-z0-9])",
    re.IGNORECASE,
)

_NEWS_ENTITY_SUFFIXES = frozenset(
    (
        "Times", "Post", "News", "Journal", "Tribune", "Herald", "Gazette",
        "Wire", "Agency", "Network", "Channel", "Broadcasting", "Media",
        "Press", "Daily", "Weekly", "Review", "Observer", "Guardian",
        "Standard", "Chronicle", "Register", "Dispatch", "Sentinel",
    )
)

_CAPITALISED_RUN = re.compile(
    r"\b[A-Z][a-zA-Z0-9]+(?:\s+(?:(?:the|of|for|and|&)\s+)?[A-Z][a-zA-Z0-9]+)+\b"
)


def _looks_like_named_entity(text: str) -> bool:
    """Conservative named-entity detector for scope enforcement.

    Returns True if the text contains signals that it names a specific
    publisher, organisation, or individual rather than describing a
    narrative pattern. Tuned for high recall on the policy-violation
    surface; false positives degrade gracefully to the scope marker.
    """
    if not text or not isinstance(text, str):
        return False
    # (1) Explicit blocklist hit (word-boundary aware).
    if _BLOCKLIST_RE.search(text):
        return True
    # (2) Capitalised run heuristic + news-entity suffix guard.
    for match in _CAPITALISED_RUN.finditer(text):
        run = match.group(0)
        tokens = [t for t in run.split() if t and t[0].isupper()]
        if not tokens:
            continue
        # Three or more consecutive Capitalised tokens is strong signal.
        if len(tokens) >= 3:
            return True
        # Two-token Capitalised run with a news-entity suffix.
        if any(tok in _NEWS_ENTITY_SUFFIXES for tok in tokens):
            return True
    return False


def _scrub_scope_violation(text: str) -> str:
    """Return the sanitized marker if text violates narrative-pattern scope,
    otherwise return text unchanged. See `_looks_like_named_entity` for the
    detection contract and the module docstring for the Codex rationale."""
    if _looks_like_named_entity(text):
        return _SCOPE_VIOLATION_MARKER
    return text


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
    ] = Field(
        default="low",
        description=(
            "Triage priority for human verification workflow. "
            "Not a legal, clinical, or regulatory determination. "
            "Internal analytical signal only."
        ),
    )

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
    # Sprint 2 PR 3 P2-11: `inferential_gap` is the LOAD-BEARING reparative
    # Pattern-Injection response. When the upstream pipeline detects
    # Gorgon Trap GT-003 (Pattern Injection) or a general fabricated-consensus
    # signature, the Bridge Builder's inferential_gap paragraph is the
    # primary repair channel: it names the kernel of truth, names the leap,
    # and separates the two explicitly. Any future change to this field or
    # to the prompt line that populates it must preserve the kernel+leap
    # structure (see bridge.py build_prompt "Layer 4 - Inferential Gap
    # Map"). Test suite: test_agents.py::TestBridgePromptPreservation.
    inferential_gap: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    feasibility_check: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    commercial_motives: Annotated[str, BeforeValidator(_null_to_empty_str)] = ""
    techniques_revealed: list[TechniqueReveal] = Field(default_factory=list)
    perception_gap: Annotated[str, BeforeValidator(_null_to_empty_str)]
    moral_foundations: dict[str, list[str]] = Field(default_factory=dict)
    reframe: Annotated[str, BeforeValidator(_null_to_empty_str)]
    socratic_dialogue: list[str] = Field(..., min_length=1, max_length=3)
    # --- Sprint 2 PR 3: Bridge scoped diagnostics ---
    # P2-10 Communication Posture (BG-042 Confidence-Posture Separation):
    # Orthogonal to overall_confidence. Confidence answers "how certain is
    # this analysis?"; posture answers "how should this be communicated to
    # someone who still holds the counter-narrative?". Three literals
    # correspond to three well-studied response strategies:
    #   direct_correction  -- classical refutation (reader open, frame shared)
    #   inoculation_first  -- technique-naming prebunk (McGuire 1964;
    #                         van der Linden 2020; Roozenbeek & van der
    #                         Linden 2022). Appropriate when the reader is
    #                         in the manipulation frame and a direct
    #                         correction would trigger identity defence.
    #   relational_first   -- Common Humanity / acknowledgment-first
    #                         (Perry et al. Common Humanity scale; Costello
    #                         protocol). Appropriate when identity stakes
    #                         dominate and the kernel of truth must be
    #                         acknowledged before any correction can land.
    # The posture MUST NOT move overall_confidence; the invariance is
    # enforced by test_orchestrator.py::TestVerificationPriorityFallback
    # (the communication_posture invariance tests live inside that class).
    #
    # ADVISORY-ONLY (Sprint 2 PR 3 fleet convergence, Romulan MUST #2):
    # This field is advisory to a downstream HUMAN communicator. It must
    # NOT be used as an automated routing gate, content-moderation signal,
    # or input to any automated decision with legal or similarly-significant
    # effect on an individual. Using this field to gate automated actions
    # without human review would convert an advisory register into a
    # GDPR Art. 22 / EU AI Act Annex III decision surface, which is out
    # of scope for this analysis-aid tool. The Charter Commitment 4
    # posture/content separation discipline applies at this boundary.
    communication_posture: Annotated[
        Literal["direct_correction", "inoculation_first", "relational_first"],
        BeforeValidator(_first_pipe_value),
    ] = Field(
        default="direct_correction",
        description=(
            "ADVISORY ONLY. Selects communicative register for downstream "
            "human communicators. Must not be used as an automated routing "
            "gate, content-moderation signal, or input to automated decisions "
            "with legal or similarly significant effect on individuals without "
            "human review. See GDPR Art. 22, EU AI Act Annex III."
        ),
    )
    # P2-6 (scoped, renamed from apophenia_bait_flag per Holodeck feedback).
    # Content-describing boolean: True iff the claim exhibits structural
    # features (repeated numeric coincidences, rhythmic lexical choices,
    # escalating concept chaining) that predispose readers to over-connect.
    # This is a warning about the CLAIM'S structural pull, never a
    # diagnosis of the reader.
    pattern_density_warning: bool = Field(
        default=False,
        description=(
            "Structural warning about the claim content. Not a moderation "
            "signal. Operators using this in automated pipelines must comply "
            "with applicable transparency obligations."
        ),
    )
    # P2-6 (scoped): structural description of what narrative pattern
    # filled an expertise or information vacuum around the claim. The
    # prompt constrains this strictly to narrative patterns -- never
    # named publishers, individuals, or organisations.
    vacuum_filled_by: Annotated[str, BeforeValidator(_null_to_empty_str)] = Field(
        default="",
        description=(
            "Narrative pattern description only. Never names publishers, "
            "individuals, or organisations. Schema-level scrubber enforces "
            "this constraint."
        ),
    )
    # P2-6 (scoped): technique warning, not a new factual assertion.
    # Example: "watch for the fabricated-source-mimicry pattern in
    # similar claims". The prompt constrains this to technique naming.
    #
    # Sprint 2 PR 3 fleet convergence (Borg Minor #4): enforce a hard
    # length cap at the schema level so the "one sentence" discipline in
    # the prompt is backed by a mechanical guard. 500 characters is
    # generous enough for a long English sentence but tight enough to
    # catch a prompt-compliance failure that produces a paragraph. The
    # cap mirrors the `socratic_dialogue` max_length=3 discipline from
    # Sprint 1 (schema-level protection for renderer assumptions).
    prebunking_note: Annotated[str, BeforeValidator(_null_to_empty_str)] = Field(
        default="",
        max_length=500,
        description=(
            "Technique-recognition cue. Not a new factual assertion. "
            "One sentence maximum."
        ),
    )

    @model_validator(mode="after")
    def _scope_scrub_narrative_pattern_fields(self) -> "BridgeOutput":
        """Sprint 2 PR 3 Codex mitigation (High severity):
        enforce the narrative-pattern-only scope on `vacuum_filled_by`
        and `prebunking_note` at the schema boundary rather than trusting
        prompt discipline alone.

        If either field contains named-publisher / named-organisation /
        named-individual content -- the exact charter violation the prompt
        warns against -- replace the value with `_SCOPE_VIOLATION_MARKER`
        so downstream renderers never receive the toxic string. Mirrors
        SubClaim's "degrade, do not crash" discipline: scrub rather than
        raise, so a single Bridge emission cannot take down the pipeline,
        but the marker is visible at the production boundary and can be
        asserted against in integration tests.
        """
        scrubbed_vacuum = _scrub_scope_violation(self.vacuum_filled_by)
        if scrubbed_vacuum != self.vacuum_filled_by:
            object.__setattr__(self, "vacuum_filled_by", scrubbed_vacuum)
        scrubbed_prebunk = _scrub_scope_violation(self.prebunking_note)
        if scrubbed_prebunk != self.prebunking_note:
            object.__setattr__(self, "prebunking_note", scrubbed_prebunk)
        return self


# --- Adversarial Auditor ---

class AuditVerdict(str, Enum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"


class AuditFinding(BaseModel):
    category: Annotated[Literal["bias", "accuracy", "completeness", "manipulation", "quality", "cognitive_warfare", "frame_capture"], BeforeValidator(_first_pipe_value)]
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
    # fact-checked. Sprint 3 PR 2 expanded AuditFinding.category with
    # "cognitive_warfare" and "frame_capture" literals; the docs generator
    # and gallery builder were updated in the same PR to handle both.
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


# --- API Response Envelope ---

class AnalysisResponse(BaseModel):
    """Sprint 3 PR 1: API response envelope.

    Wraps a projected AnalysisReport in a `data` field with envelope
    metadata. The `data` field is a strict subset of AnalysisReport
    (zero-regression constraint #3). Envelope metadata (suppressed_fields,
    api_version) is not subject to the strict-subset constraint."""

    data: dict
    suppressed_fields: list[str] = Field(default_factory=list)
    api_version: str = "0.11.0"
    audit_redacted: bool = False

    _FIELD_DEFAULTS: ClassVar[dict[str, object]] = {
        "communication_posture": "direct_correction",
        "pattern_density_warning": False,
        "vacuum_filled_by": "",
        "prebunking_note": "",
    }

    @classmethod
    def from_report(
        cls,
        report: "AnalysisReport",
        suppressed: frozenset[str],
    ) -> "AnalysisResponse":
        data = report.model_dump(mode="json")
        suppressed_list = []
        if suppressed and "bridge" in data:
            bridge = data["bridge"]
            for field_name in sorted(suppressed):
                if field_name in bridge and field_name in cls._FIELD_DEFAULTS:
                    bridge[field_name] = cls._FIELD_DEFAULTS[field_name]
                    suppressed_list.append(field_name)
        return cls(data=data, suppressed_fields=suppressed_list)
