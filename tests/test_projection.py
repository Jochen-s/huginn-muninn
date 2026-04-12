"""Tests for the AnalysisResponse projection helper."""
import pytest
from huginn_muninn.projection import project_analysis
from huginn_muninn.config import _reset_settings


class TestProjectAnalysis:
    """Sprint 3 PR 1: projection helper used at all 10 boundaries."""

    def setup_method(self):
        _reset_settings()

    def teardown_method(self):
        _reset_settings()

    def _make_raw_analysis(self) -> dict:
        return {
            "claim": "X",
            "decomposition": {
                "sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
                "original_claim": "X",
                "complexity": "simple",
            },
            "origins": {"origins": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["safety"],
                "issue_overlap": "o", "narrative_deconstruction": "d",
                "perception_gap": "g", "moral_foundations": {},
                "reframe": "r", "socratic_dialogue": ["R1"],
                "communication_posture": "inoculation_first",
                "vacuum_filled_by": "pattern description",
                "prebunking_note": "technique warning",
                "pattern_density_warning": True,
            },
            "audit": {
                "verdict": "pass", "findings": [],
                "confidence_adjustment": 0.0, "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.7,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

    def test_project_with_no_suppression(self):
        result = project_analysis(self._make_raw_analysis())
        assert result["data"]["bridge"]["vacuum_filled_by"] == "pattern description"
        assert result["suppressed_fields"] == []

    def test_project_with_suppression(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by")
        result = project_analysis(self._make_raw_analysis())
        assert result["data"]["bridge"]["vacuum_filled_by"] == ""
        assert result["suppressed_fields"] == ["vacuum_filled_by"]

    def test_project_with_explicit_suppression(self):
        result = project_analysis(
            self._make_raw_analysis(),
            suppressed=frozenset({"vacuum_filled_by"}),
        )
        assert result["data"]["bridge"]["vacuum_filled_by"] == ""
        assert result["suppressed_fields"] == ["vacuum_filled_by"]

    def test_project_normalizes_legacy_cache_hit(self):
        """BG-050: legacy dict missing Sprint 2 fields gets defaults."""
        raw = self._make_raw_analysis()
        del raw["bridge"]["communication_posture"]
        del raw["bridge"]["vacuum_filled_by"]
        del raw["bridge"]["prebunking_note"]
        del raw["bridge"]["pattern_density_warning"]
        result = project_analysis(raw)
        assert result["data"]["bridge"]["communication_posture"] == "direct_correction"

    def test_project_returns_envelope_shape(self):
        result = project_analysis(self._make_raw_analysis())
        assert "data" in result
        assert "suppressed_fields" in result
        assert "api_version" in result

    def test_project_non_method2_returns_as_is(self):
        """Method 1 verdicts should not be wrapped in an envelope."""
        verdict = {"claim": "X", "verdict": "likely_true", "confidence": 0.9}
        result = project_analysis(verdict, is_method2=False)
        assert result == verdict

    def test_project_invalid_dict_returns_raw(self):
        """If the dict can't validate as AnalysisReport, return it raw."""
        bad = {"not_a_report": True}
        result = project_analysis(bad)
        assert result == bad
