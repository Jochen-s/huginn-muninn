"""Every free-text field in AnalysisReport has a recorded scrubbing decision (K-007).

The scope scrubber in contracts.py covers the fields whose job is to describe
a narrative pattern and must never name a person (Charter Commitment 1). The
2026-09-03 fleet review found that the covered set was seven fields chosen by
hand while the report holds far more free text. This test does not scrub more;
it makes the coverage decision explicit: every str or list[str] field reachable
from AnalysisReport is either SCRUBBED or listed in ALLOWED with the reason it
may carry names. A new free-text field fails this test until it is classified.
"""
from __future__ import annotations

import types
import typing

from pydantic import BaseModel

from huginn_muninn.contracts import AnalysisReport

# Fields the contract-level scope scrubber rewrites (see _scrub_scope_violation callers).
SCRUBBED = {
    "ConvergenceGroup.label",
    "ConvergenceGroup.framing",
    "ConvergenceGroup.core_grievance",
    "ConvergenceGroup.proposed_solution",
    "ConvergenceMatrix.bridge_narratives",
    "BridgeOutput.vacuum_filled_by",
    "BridgeOutput.prebunking_note",
    "CounterNarrativeQualityScore.evaluated_source",
}

# Fields that may legitimately carry names, with the reason. Audit free text
# is additionally sentence-scrubbed at projection for suppressed-field
# references (projection._scrub_audit_text); it is listed here because that
# scrub is reference-based, not entity-based.
ALLOWED = {
    "AnalysisReport.claim": "the user's own input, echoed back",
    "AnalysisReport.degraded_reason": "pipeline status string, not narrative",
    "DecomposerOutput.original_claim": "the user's own input",
    "SubClaim.text": "decomposition of the user's input",
    "OriginEntry.sub_claim": "decomposition of the user's input",
    "OriginEntry.earliest_source": "a URL or outlet, which is the point of provenance",
    "OriginEntry.earliest_date": "date string",
    "OriginEntry.propagation_path": "outlets and platforms; provenance",
    "EpistemicProvenance.region": "region label",
    "EpistemicProvenance.language_of_origin": "language code",
    "NarrativeMutation.original": "quoted claim text",
    "NarrativeMutation.mutated": "quoted claim text",
    "NarrativeMutation.source": "outlet or platform; provenance",
    "TemporalContext.era": "period label",
    "TemporalContext.date_range": "date string",
    "TemporalContext.dominant_framing": "historical framing summary",
    "TemporalContext.key_actors": "historical actors, documented public roles",
    "TemporalContext.power_context": "historical context",
    "TemporalContext.irony_or_inversion": "historical context",
    "TracerOutput.notable_omissions": "what the sources omit",
    "TracerOutput.epistemic_diversity_gap": "gap description",
    "Actor.name": "actors are named organisations and public actors by design; credibility is categorical, never numeric (Commitment 1)",
    "Actor.motivation": "documented motive, tied to evidence",
    "Actor.evidence": "citation of the documentation",
    "Actor.credibility_basis": "categorical label",
    "ActorRelation.source_actor": "refers to Actor.name",
    "ActorRelation.target_actor": "refers to Actor.name",
    "ConvergenceMatrix.amplification_risk": "risk note, length-capped",
    "MapperOutput.narrative_summary": "summary of documented actors; same basis as Actor.name",
    "TTPMatch.disarm_id": "identifier, format-validated",
    "TTPMatch.technique_name": "taxonomy label",
    "TTPMatch.evidence": "quote from the claim",
    "TechniqueReveal.technique": "taxonomy label",
    "TechniqueReveal.how_it_works": "mechanism description",
    "TechniqueReveal.used_by": "historical users of the technique (documented campaigns)",
    "TechniqueReveal.where_used_here": "quote from the claim",
    "TechniqueReveal.historical_precedent": "documented history",
    "BridgeOutput.universal_needs": "needs vocabulary",
    "BridgeOutput.issue_overlap": "common-ground prose about positions, not persons",
    "BridgeOutput.narrative_deconstruction": "pattern description",
    "BridgeOutput.perception_gap": "pattern description",
    "BridgeOutput.reframe": "reframe prose",
    "BridgeOutput.socratic_dialogue": "the dialogue script",
    "BridgeOutput.commercial_motives": "names organisations and revenue streams by design (who profits); same basis as Actor.name",
    "BridgeOutput.consensus_explanation": "explains the evidence consensus, not persons",
    "BridgeOutput.feasibility_check": "reasoning about the claim's mechanism",
    "BridgeOutput.inferential_gap": "reasoning about the claim's logic",
    "ConfidenceProfile.ecf_level": "enum-like",
    "AuditFinding.description": "audit prose; projection scrubs suppressed-field references",
    "AuditFinding.recommendation": "audit prose; projection scrubs suppressed-field references",
    "AuditorOutput.summary": "audit prose; projection scrubs suppressed-field references",
    "AuditorOutput.frame_capture_evidence": "audit prose; projection scrubs suppressed-field references",
}


def _unwrap(tp):
    """Yield the concrete types inside Optional/Annotated/list wrappers."""
    origin = typing.get_origin(tp)
    if origin is typing.Annotated:
        yield from _unwrap(typing.get_args(tp)[0])
    elif origin in (typing.Union, types.UnionType):
        for arg in typing.get_args(tp):
            if arg is not type(None):
                yield from _unwrap(arg)
    elif origin in (list, tuple, set, frozenset):
        args = typing.get_args(tp)
        if args:
            yield ("list", next(iter(_unwrap(args[0]))))
        else:
            yield ("list", str)
    elif origin is dict:
        yield ("dict", None)
    elif origin is typing.Literal:
        yield ("literal", None)
    else:
        yield tp


def _text_fields(model: type[BaseModel], seen: set[type]) -> set[str]:
    if model in seen:
        return set()
    seen.add(model)
    out: set[str] = set()
    for name, info in model.model_fields.items():
        for inner in _unwrap(info.annotation):
            if isinstance(inner, tuple):
                kind, elem = inner
                if kind == "list" and elem is str:
                    out.add(f"{model.__name__}.{name}")
                elif kind == "list" and isinstance(elem, type) and issubclass(elem, BaseModel):
                    out |= _text_fields(elem, seen)
            elif inner is str:
                out.add(f"{model.__name__}.{name}")
            elif isinstance(inner, type) and issubclass(inner, BaseModel):
                out |= _text_fields(inner, seen)
    return out


def test_every_free_text_field_has_a_scrub_decision():
    found = _text_fields(AnalysisReport, set())
    classified = SCRUBBED | set(ALLOWED)
    unclassified = sorted(found - classified)
    stale = sorted(classified - found)
    assert unclassified == [], f"free-text fields without a scrub decision: {unclassified}"
    assert stale == [], f"classified fields that no longer exist: {stale}"


def test_scrubbed_set_matches_the_scrubber_call_sites():
    """The SCRUBBED list above must be what contracts.py actually scrubs."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "src" / "huginn_muninn" / "contracts.py").read_text(encoding="utf-8")
    for entry in SCRUBBED:
        field = entry.split(".", 1)[1]
        assert field in src, entry
    assert src.count("_scrub_scope_violation(") >= 5
