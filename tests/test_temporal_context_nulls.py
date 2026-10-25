"""Local models emit null for optional TemporalContext text; that must not degrade the pipeline.

Found 2026-10-24 by the model comparison: qwen3.5:9b and qwen3.8:27b both returned
`"irony_or_inversion": null`, TracerOutput validation failed, and 4 of 5 Method 2
calibration runs came back degraded."""
from huginn_muninn.contracts import TemporalContext

BASE = {"era": "2020s", "date_range": "2020-2024", "dominant_framing": "x"}


def test_null_irony_becomes_empty_string():
    assert TemporalContext(**BASE, irony_or_inversion=None).irony_or_inversion == ""


def test_null_power_context_becomes_empty_string():
    assert TemporalContext(**BASE, power_context=None).power_context == ""


def test_text_is_kept():
    assert TemporalContext(**BASE, irony_or_inversion="paradox").irony_or_inversion == "paradox"
