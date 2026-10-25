"""A null earliest_source means the model does not know the source.

Found 2026-10-25 by the blinded model rating: qwen3.5:9b returned
`"earliest_source": null` for every origin, TracerOutput validation failed and
the analysis came back degraded. Null now reads as "unknown", and an unknown
source cannot carry a self-reported high tier into the confidence score."""
from huginn_muninn.contracts import OriginEntry
from huginn_muninn.orchestrator import _effective_source_tier


def test_null_source_becomes_unknown():
    entry = OriginEntry(sub_claim="x", earliest_source=None, source_tier=2)
    assert entry.earliest_source == "unknown"


def test_named_source_is_kept():
    entry = OriginEntry(sub_claim="x", earliest_source="Kaysing 1976", source_tier=3)
    assert entry.earliest_source == "Kaysing 1976"


def test_unknown_source_gets_lowest_tier():
    assert _effective_source_tier({"earliest_source": "unknown", "source_tier": 1}) == 4


def test_described_source_keeps_model_tier():
    assert _effective_source_tier({"earliest_source": "Kaysing 1976", "source_tier": 3}) == 3
