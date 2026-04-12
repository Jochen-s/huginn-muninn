"""Sprint 3 PR 1: AnalysisResponse projection helper.

Single entry point for projecting analysis results at all external
serialization boundaries. Handles BG-050 normalization (for legacy
cache hits) followed by AnalysisResponse envelope construction.

Used by: api.py, worker.py, cli.py (JSON output path)."""
from __future__ import annotations

import logging

from pydantic import ValidationError

from huginn_muninn.config import get_settings
from huginn_muninn.contracts import AnalysisReport, AnalysisResponse

log = logging.getLogger(__name__)


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
        log.warning("Failed to validate analysis for projection; returning raw")
        return raw

    response = AnalysisResponse.from_report(report, suppressed=suppressed)
    return response.model_dump(mode="json")
