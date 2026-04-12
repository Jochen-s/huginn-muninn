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


class TestAuditRedacted:
    """Sprint 4: audit_redacted disclosure on AnalysisResponse."""

    def setup_method(self):
        _reset_settings()

    def teardown_method(self):
        _reset_settings()

    def test_audit_redacted_defaults_to_false(self):
        from huginn_muninn.contracts import AnalysisResponse
        resp = AnalysisResponse(data={"test": True})
        assert resp.audit_redacted is False

    def test_audit_redacted_in_envelope(self):
        raw = TestProjectAnalysis()._make_raw_analysis()
        result = project_analysis(raw)
        assert "audit_redacted" in result
        assert result["audit_redacted"] is False


class TestScrubAuditText:
    """Sprint 4: sentence-level scrubbing of suppressed field references."""

    def test_scrubs_field_name_underscore(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The vacuum_filled_by field correctly identifies the pattern. Other finding."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert "[content redacted]" in result
        assert "Other finding." in result
        assert changed is True

    def test_scrubs_field_name_space_variant(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The vacuum filled by correctly identifies the gap."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert "[content redacted]" in result
        assert changed is True

    def test_scrubs_case_insensitive(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The Vacuum_Filled_By shows good analysis."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert "[content redacted]" in result
        assert changed is True

    def test_preserves_non_matching_sentences(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "First sentence is clean. The prebunking_note is good. Third is also clean."
        result, changed = _scrub_audit_text(text, frozenset({"prebunking_note"}))
        assert "First sentence is clean." in result
        assert "Third is also clean." in result
        assert "prebunking_note" not in result
        assert changed is True

    def test_no_scrub_when_no_match(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "This finding is about bias in source selection."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert result == text
        assert changed is False

    def test_no_scrub_when_no_suppression(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The vacuum_filled_by is accurate."
        result, changed = _scrub_audit_text(text, frozenset())
        assert result == text
        assert changed is False

    def test_bare_prebunking_not_scrubbed(self):
        """4/6 fleet: bare 'prebunking' shortform was a false-positive risk."""
        from huginn_muninn.projection import _scrub_audit_text
        text = "The prebunking technique cue is well-formed."
        result, changed = _scrub_audit_text(text, frozenset({"prebunking_note"}))
        assert result == text
        assert changed is False

    def test_scrubs_prebunking_note_full_form(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The prebunking note is well-formed."
        result, changed = _scrub_audit_text(text, frozenset({"prebunking_note"}))
        assert "[content redacted]" in result
        assert changed is True

    def test_scrubs_pattern_density_warning_full_form(self):
        from huginn_muninn.projection import _scrub_audit_text
        text = "The pattern density warning signal is appropriate."
        result, changed = _scrub_audit_text(text, frozenset({"pattern_density_warning"}))
        assert "[content redacted]" in result
        assert changed is True

    def test_handles_abbreviations_in_text(self):
        """6/6 fleet: naive split on '.' broke on abbreviations like Dr. or e.g."""
        from huginn_muninn.projection import _scrub_audit_text
        text = "Dr. Smith noted the vacuum_filled_by is accurate. The analysis is sound."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert "[content redacted]" in result
        assert "The analysis is sound." in result
        assert changed is True

    def test_handles_decimal_numbers(self):
        """6/6 fleet: naive split broke on decimals like 0.7."""
        from huginn_muninn.projection import _scrub_audit_text
        text = "Confidence is 0.7 and the vacuum_filled_by is noted. Other text here."
        result, changed = _scrub_audit_text(text, frozenset({"vacuum_filled_by"}))
        assert "[content redacted]" in result
        assert "Other text here." in result
        assert changed is True


class TestAuditExfiltrationGuard:
    """Sprint 4: end-to-end audit scrubbing through projection."""

    def setup_method(self):
        _reset_settings()

    def teardown_method(self):
        _reset_settings()

    def _make_raw_with_leaky_audit(self) -> dict:
        raw = TestProjectAnalysis()._make_raw_analysis()
        raw["audit"]["findings"] = [
            {
                "category": "quality",
                "severity": "medium",
                "description": "The vacuum_filled_by field correctly identifies state-media patterns. Good analysis.",
                "recommendation": "Consider expanding the prebunking_note to cover more techniques.",
            }
        ]
        raw["audit"]["summary"] = "Analysis is sound. The communication posture is appropriate."
        raw["audit"]["frame_capture_evidence"] = ""
        return raw

    def test_finding_description_scrubbed(self):
        result = project_analysis(
            self._make_raw_with_leaky_audit(),
            suppressed=frozenset({"vacuum_filled_by"}),
        )
        desc = result["data"]["audit"]["findings"][0]["description"]
        assert "vacuum_filled_by" not in desc
        assert "[content redacted]" in desc
        assert "Good analysis." in desc

    def test_finding_recommendation_scrubbed(self):
        result = project_analysis(
            self._make_raw_with_leaky_audit(),
            suppressed=frozenset({"prebunking_note"}),
        )
        rec = result["data"]["audit"]["findings"][0]["recommendation"]
        assert "prebunking_note" not in rec
        assert "[content redacted]" in rec

    def test_summary_scrubbed(self):
        result = project_analysis(
            self._make_raw_with_leaky_audit(),
            suppressed=frozenset({"communication_posture"}),
        )
        summary = result["data"]["audit"]["summary"]
        assert "communication posture" not in summary.lower()
        assert "[content redacted]" in summary

    def test_frame_capture_evidence_scrubbed(self):
        """Borg finding: frame_capture_evidence had zero test coverage."""
        raw = self._make_raw_with_leaky_audit()
        raw["audit"]["frame_capture_evidence"] = "The vacuum_filled_by content confirms framing adoption."
        result = project_analysis(raw, suppressed=frozenset({"vacuum_filled_by"}))
        evidence = result["data"]["audit"]["frame_capture_evidence"]
        assert "vacuum_filled_by" not in evidence
        assert "[content redacted]" in evidence

    def test_audit_redacted_true_when_scrubbed(self):
        result = project_analysis(
            self._make_raw_with_leaky_audit(),
            suppressed=frozenset({"vacuum_filled_by"}),
        )
        assert result["audit_redacted"] is True

    def test_audit_redacted_false_when_no_scrubbing(self):
        raw = TestProjectAnalysis()._make_raw_analysis()
        result = project_analysis(raw, suppressed=frozenset({"vacuum_filled_by"}))
        assert result["audit_redacted"] is False

    def test_no_scrubbing_without_suppression(self):
        result = project_analysis(self._make_raw_with_leaky_audit())
        desc = result["data"]["audit"]["findings"][0]["description"]
        assert "vacuum_filled_by" in desc
        assert result["audit_redacted"] is False
