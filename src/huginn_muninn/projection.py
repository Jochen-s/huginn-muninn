"""Sprint 3 PR 1: AnalysisResponse projection helper.

Single entry point for projecting analysis results at all external
serialization boundaries. Handles BG-050 normalization (for legacy
cache hits) followed by AnalysisResponse envelope construction.

Sprint 4: audit text scrubbing to close the exfiltration channel
where suppressed Bridge field content leaks through Auditor free-text.

Used by: api.py, worker.py, cli.py (JSON output path)."""
from __future__ import annotations

import logging
import re

from pydantic import ValidationError

from huginn_muninn.config import get_settings
from huginn_muninn.contracts import AnalysisReport, AnalysisResponse

log = logging.getLogger(__name__)

_REDACTION_MARKER = "[content redacted]"

# Match patterns for each suppressible field (underscore and space variants only).
# Short-form aliases like bare "prebunking" are excluded to avoid false-positive
# redaction of legitimate audit prose discussing techniques (4/6 fleet convergence).
_FIELD_PATTERNS: dict[str, list[str]] = {
    "vacuum_filled_by": ["vacuum_filled_by", "vacuum filled by"],
    "prebunking_note": ["prebunking_note", "prebunking note"],
    "communication_posture": ["communication_posture", "communication posture"],
    "pattern_density_warning": ["pattern_density_warning", "pattern density warning"],
    "confidence_profile": ["confidence_profile", "confidence profile", "ecf_level"],
    "cnqs": ["cnqs", "counter_narrative_quality", "counter-narrative quality"],
}

# Sentence boundary: split after sentence-ending punctuation followed by whitespace.
# Keeps the delimiter with the preceding sentence, avoiding the naive text.split(".")
# bug that breaks on abbreviations ("Dr."), decimals ("0.7"), and URLs (6/6 fleet).
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _scrub_audit_text(
    text: str, suppressed: frozenset[str]
) -> tuple[str, bool]:
    """Replace sentences referencing suppressed field names with a redaction marker.

    Returns (scrubbed_text, was_changed). Sentence boundaries are detected via
    punctuation-followed-by-whitespace regex to handle abbreviations and decimals.
    """
    if not text or not suppressed:
        return text, False

    patterns = []
    for field_name in suppressed:
        patterns.extend(_FIELD_PATTERNS.get(field_name, [field_name]))
    if not patterns:
        return text, False

    combined = re.compile("|".join(re.escape(p) for p in patterns), re.IGNORECASE)

    sentences = _SENTENCE_SPLIT.split(text)
    changed = False
    result = []
    for sentence in sentences:
        if combined.search(sentence):
            result.append(_REDACTION_MARKER)
            changed = True
        else:
            result.append(sentence)

    return " ".join(result) if changed else text, changed


def project_analysis(
    raw: dict,
    *,
    suppressed: frozenset[str] | None = None,
    is_method2: bool = True,
) -> dict:
    """Normalize and project an analysis result for external consumption.

    Args:
        raw: Raw analysis dict (from orchestrator, job store, or DB cache).
        suppressed: Field names to suppress. If None, reads from Settings.
        is_method2: If False, returns the dict unchanged (Method 1 passthrough).

    Returns:
        AnalysisResponse envelope dict (if Method 2) or raw dict (if Method 1).
    """
    if not is_method2:
        return raw

    if suppressed is None:
        suppressed = frozenset(get_settings().suppressed_fields)

    # BG-050: normalize through the contract to populate any missing
    # defaults from schema evolution (legacy cache hits).
    try:
        report = AnalysisReport.model_validate(raw)
    except ValidationError:
        # Fail closed. Returning the raw dict skipped field suppression and
        # audit scrubbing, so an unvalidatable payload was the one path on
        # which suppressed content reached the boundary unfiltered.
        log.warning("Failed to validate analysis for projection; returning degraded envelope")
        return {
            "data": {},
            "suppressed_fields": sorted(suppressed),
            "api_version": AnalysisResponse.model_fields["api_version"].default,
            "audit_redacted": False,
            "experimental_fields": [],
            "degraded": True,
            "degraded_reason": "contract_validation_failed",
        }

    response = AnalysisResponse.from_report(report, suppressed=suppressed)
    resp_data = response.model_dump(mode="json")

    # Sprint 4: scrub audit free-text fields that reference suppressed content
    audit_redacted = False
    if suppressed:
        audit = resp_data.get("data", {}).get("audit", {})
        if audit:
            for finding in audit.get("findings", []):
                for key in ("description", "recommendation"):
                    if finding.get(key):
                        finding[key], was_scrubbed = _scrub_audit_text(
                            finding[key], suppressed
                        )
                        audit_redacted = audit_redacted or was_scrubbed
            if audit.get("summary"):
                audit["summary"], was_scrubbed = _scrub_audit_text(
                    audit["summary"], suppressed
                )
                audit_redacted = audit_redacted or was_scrubbed
            if audit.get("frame_capture_evidence"):
                audit["frame_capture_evidence"], was_scrubbed = _scrub_audit_text(
                    audit["frame_capture_evidence"], suppressed
                )
                audit_redacted = audit_redacted or was_scrubbed
        # The veto path copies audit.summary into degraded_reason and, when
        # the Bridge is withheld, into socratic_dialogue[0]. Those carriers
        # are scrubbed with the same rule (review finding, 2026-09-03).
        report = resp_data.get("data", {})
        if report.get("degraded_reason"):
            report["degraded_reason"], was_scrubbed = _scrub_audit_text(
                report["degraded_reason"], suppressed
            )
            audit_redacted = audit_redacted or was_scrubbed
        if report.get("bridge_withheld"):
            dialogue = (report.get("bridge") or {}).get("socratic_dialogue") or []
            scrubbed_lines = []
            for line in dialogue:
                line, was_scrubbed = _scrub_audit_text(line, suppressed)
                audit_redacted = audit_redacted or was_scrubbed
                scrubbed_lines.append(line)
            report["bridge"]["socratic_dialogue"] = scrubbed_lines

    # Deliberate design choice (3/6 fleet flagged Streisand risk): audit_redacted
    # is always emitted in the envelope. This is the hybrid-C disclosure: operators
    # know scrubbing is best-effort (paraphrased content may survive). Hiding the
    # flag would create false assurance; showing it is honest. Operators who need
    # zero-knowledge suppression must implement downstream filtering.
    resp_data["audit_redacted"] = audit_redacted

    experimental = []
    report_data = resp_data.get("data", {})
    if report_data.get("cnqs") is not None:
        experimental.append("cnqs")
    resp_data["experimental_fields"] = experimental
    return resp_data
