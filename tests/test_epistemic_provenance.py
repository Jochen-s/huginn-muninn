"""Sprint 5 tests: Epistemic Provenance + Regional Source Registry.

Covers:
- EpistemicProvenance model validation
- OriginEntry with provenance field
- TracerOutput gap detection (bidirectional, 80% threshold)
- Regional source registry loading and schema
- Acceptance criteria: default "unclassified", bidirectional gap detection,
  (tradition, region) tuples, registry framed as advisory
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from huginn_muninn.contracts import (
    EpistemicProvenance,
    OriginEntry,
    TracerOutput,
)
from huginn_muninn.sources import load_regional_sources


# ---------------------------------------------------------------------------
# EpistemicProvenance model
# ---------------------------------------------------------------------------


class TestEpistemicProvenance:

    def test_default_is_unclassified(self):
        """AC: EpistemicProvenance default is 'unclassified'."""
        p = EpistemicProvenance()
        assert p.tradition == "unclassified"
        assert p.region == ""
        assert p.language_of_origin == ""

    def test_valid_traditions(self):
        for tradition in (
            "western_academic", "western_institutional",
            "global_south_academic", "global_south_institutional",
            "community_experiential", "indigenous_knowledge",
            "unclassified",
        ):
            p = EpistemicProvenance(tradition=tradition)
            assert p.tradition == tradition

    def test_invalid_tradition_rejected(self):
        with pytest.raises(Exception):
            EpistemicProvenance(tradition="invented_tradition")

    def test_pipe_sanitizer_takes_first_value(self):
        p = EpistemicProvenance(tradition="western_academic|global_south_academic")
        assert p.tradition == "western_academic"

    def test_serializes_in_model_dump(self):
        p = EpistemicProvenance(
            tradition="global_south_academic",
            region="West Africa",
            language_of_origin="fr",
        )
        d = p.model_dump()
        assert d["tradition"] == "global_south_academic"
        assert d["region"] == "West Africa"
        assert d["language_of_origin"] == "fr"

    def test_region_and_language_have_length_limits(self):
        with pytest.raises(Exception):
            EpistemicProvenance(region="x" * 257)
        with pytest.raises(Exception):
            EpistemicProvenance(language_of_origin="x" * 11)


# ---------------------------------------------------------------------------
# OriginEntry with provenance
# ---------------------------------------------------------------------------


class TestOriginEntryProvenance:

    def test_provenance_defaults_to_none(self):
        entry = OriginEntry(
            sub_claim="test",
            earliest_source="source",
            source_tier=1,
        )
        assert entry.epistemic_provenance is None

    def test_provenance_round_trips_through_model_dump(self):
        entry = OriginEntry(
            sub_claim="test",
            earliest_source="source",
            source_tier=2,
            epistemic_provenance=EpistemicProvenance(
                tradition="indigenous_knowledge",
                region="Oceania",
                language_of_origin="mi",
            ),
        )
        d = entry.model_dump()
        assert d["epistemic_provenance"]["tradition"] == "indigenous_knowledge"
        assert d["epistemic_provenance"]["region"] == "Oceania"

    def test_existing_origin_entries_still_parse_without_provenance(self):
        raw = {
            "sub_claim": "test",
            "earliest_source": "nature.com",
            "source_tier": 1,
            "propagation_path": ["a", "b"],
        }
        entry = OriginEntry(**raw)
        assert entry.epistemic_provenance is None
        assert entry.source_tier == 1


# ---------------------------------------------------------------------------
# TracerOutput gap detection
# ---------------------------------------------------------------------------


class TestEpistemicDiversityGap:

    def _make_origin(self, tradition: str, region: str = "") -> dict:
        return {
            "sub_claim": f"claim about {tradition}",
            "earliest_source": "source",
            "source_tier": 2,
            "epistemic_provenance": {
                "tradition": tradition,
                "region": region,
            },
        }

    def test_no_gap_when_no_provenance(self):
        t = TracerOutput(origins=[
            {"sub_claim": "x", "earliest_source": "s", "source_tier": 1},
        ])
        assert t.epistemic_diversity_gap is None

    def test_no_gap_when_fewer_than_two_provenances(self):
        t = TracerOutput(origins=[
            self._make_origin("western_academic"),
        ])
        assert t.epistemic_diversity_gap is None

    def test_gap_fires_at_80_percent_western(self):
        """AC: Gap detection fires bidirectionally on any 80%+ tradition."""
        origins = [self._make_origin("western_academic")] * 4
        origins.append(self._make_origin("global_south_academic"))
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is not None
        assert "western_academic" in t.epistemic_diversity_gap
        assert "80%" in t.epistemic_diversity_gap

    def test_gap_fires_bidirectionally_on_global_south(self):
        """AC: Bidirectional means any tradition, not just Western."""
        origins = [self._make_origin("global_south_institutional")] * 5
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is not None
        assert "global_south_institutional" in t.epistemic_diversity_gap
        assert "100%" in t.epistemic_diversity_gap

    def test_no_gap_at_75_percent(self):
        origins = [self._make_origin("western_academic")] * 3
        origins.append(self._make_origin("global_south_academic"))
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is None

    def test_no_gap_when_all_unclassified(self):
        origins = [self._make_origin("unclassified")] * 5
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is None

    def test_gap_ignores_entries_without_provenance(self):
        origins = [
            self._make_origin("western_academic"),
            self._make_origin("western_academic"),
            {"sub_claim": "no provenance", "earliest_source": "s", "source_tier": 3},
            {"sub_claim": "no provenance 2", "earliest_source": "s", "source_tier": 4},
        ]
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is not None
        assert "100%" in t.epistemic_diversity_gap

    def test_diverse_sources_no_gap(self):
        origins = [
            self._make_origin("western_academic", "North America"),
            self._make_origin("global_south_academic", "West Africa"),
            self._make_origin("indigenous_knowledge", "Oceania"),
            self._make_origin("community_experiential", "South Asia"),
            self._make_origin("western_institutional", "Europe"),
        ]
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is None

    def test_gap_message_includes_percentage(self):
        origins = [self._make_origin("community_experiential")] * 9
        origins.append(self._make_origin("western_academic"))
        t = TracerOutput(origins=origins)
        assert t.epistemic_diversity_gap is not None
        assert "90%" in t.epistemic_diversity_gap


# ---------------------------------------------------------------------------
# Regional Source Registry
# ---------------------------------------------------------------------------


class TestRegionalSourceRegistry:

    def test_registry_loads_successfully(self):
        registry = load_regional_sources()
        assert "regions" in registry
        assert "metadata" in registry

    def test_registry_has_governance_metadata(self):
        registry = load_regional_sources()
        meta = registry["metadata"]
        assert "curator" in meta
        assert "inclusion_criteria" in meta
        assert "last_reviewed" in meta

    def test_registry_framed_as_advisory(self):
        """AC: Registry framed as 'sources to consider,' not 'trusted sources'."""
        registry = load_regional_sources()
        purpose = registry["metadata"]["purpose"]
        assert "NOT a trust list" in purpose or "not a trust list" in purpose.lower()
        note = registry.get("note", "")
        assert "advisory" in note.lower()
        assert "trust" not in purpose.lower().replace("not a trust list", "")

    def test_registry_note_warns_about_static_bias(self):
        registry = load_regional_sources()
        note = registry.get("note", "")
        assert "bias" in note.lower()

    def test_registry_has_expected_regions(self):
        registry = load_regional_sources()
        regions = registry["regions"]
        assert len(regions) >= 4

    def test_registry_entries_have_required_fields(self):
        registry = load_regional_sources()
        for region_name, categories in registry["regions"].items():
            for category_name, entries in categories.items():
                for entry in entries:
                    assert "name" in entry, f"Missing name in {region_name}/{category_name}"
                    assert "tradition" in entry, f"Missing tradition in {region_name}/{category_name}"
                    assert entry["tradition"] in (
                        "global_south_academic", "global_south_institutional",
                        "community_experiential", "indigenous_knowledge",
                    ), f"Invalid tradition {entry['tradition']} in {region_name}/{category_name}"

    def test_registry_json_valid(self):
        path = Path(__file__).parent.parent / "data" / "regional_sources.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_registry_no_trusted_sources_language(self):
        """The registry must never use 'trusted source' language."""
        path = Path(__file__).parent.parent / "data" / "regional_sources.json"
        text = path.read_text(encoding="utf-8").lower()
        assert "trusted source" not in text
        assert "authoritative source" not in text
