"""Located findings (design C, 2026-11-10).

The Auditor quotes the passage each finding is about. A deterministic step
checks that the quote occurs in the named section and records where, so
renderers can show the finding beside the passage. No LLM is involved, and
a quote that cannot be found leaves the finding unlocated, never guessed.
"""
import json

from huginn_muninn.contracts import AnalysisReport, AuditFinding, AuditorOutput
from huginn_muninn.locate import MIN_QUOTE_CHARS, locate_findings, locate_quote
from huginn_muninn.orchestrator import Orchestrator
from huginn_muninn.projection import project_analysis
from test_orchestrator import MOCK_RESPONSES, make_mock_client

SECTIONS = {
    "decomposition": {"sub_claims": [{"text": "Warming is not occurring at all."}]},
    "origins": {"origins": [{"earliest_source": "A 2009 blog post about leaked emails."}]},
    "intelligence": {"narrative_summary": "Outlets repeated the claim during 2010."},
    "ttps": {"ttp_matches": []},
    "bridge": {
        "socratic_dialogue": ["Round one says the data was faked.", "What would change your mind?"],
        "prebunking_note": "Watch for the cherry-picked start year.",
    },
}


class TestLocateQuote:
    def test_finds_exact_quote_in_named_section(self):
        assert locate_quote(SECTIONS, "bridge", "the data was faked") == ["bridge.socratic_dialogue[0]"]

    def test_quote_outside_named_section_is_not_found(self):
        assert locate_quote(SECTIONS, "origins", "the data was faked") == []

    def test_unknown_section_is_not_found(self):
        assert locate_quote(SECTIONS, "audit", "the data was faked") == []

    def test_short_quote_is_not_found(self):
        assert locate_quote(SECTIONS, "bridge", "faked") == []
        assert MIN_QUOTE_CHARS >= 10

    def test_empty_quote_is_not_found(self):
        assert locate_quote(SECTIONS, "bridge", "   ") == []

    def test_whitespace_and_typographic_quotes_are_normalised(self):
        s = {"bridge": {"reframe": "It’s about   trust\nin  institutions."}}
        assert locate_quote(s, "bridge", "It's about trust in institutions") == ["bridge.reframe"]

    def test_json_escaped_quote_matches_unicode_text(self):
        s = {"origins": {"origins": [{"earliest_source": "Claude Allègre, L'imposture climatique"}]}}
        assert locate_quote(s, "origins", "Claude All\\u00e8gre, L'imposture climatique") == ["origins.origins[0].earliest_source"]

    def test_prompt_encoded_quote_marks_match(self):
        # The Auditor reads json.dumps output passed through sanitize_for_prompt.
        s = {"bridge": {"reframe": 'He said "the data was faked" twice.'}}
        for q in ('said \\&quot;the data was faked\\&quot; twice',
                  'said &quot;the data was faked&quot; twice',
                  'said "the data was faked" twice'):
            assert locate_quote(s, "bridge", q) == ["bridge.reframe"], q

    def test_quote_in_two_places_returns_both_paths(self):
        s = {"bridge": {"reframe": "the same sentence here", "issue_overlap": "the same sentence here"}}
        assert sorted(locate_quote(s, "bridge", "the same sentence here")) == [
            "bridge.issue_overlap", "bridge.reframe"]

    def test_match_is_case_sensitive(self):
        assert locate_quote(SECTIONS, "bridge", "THE DATA WAS FAKED") == []


class TestLocateFindings:
    def _audit(self, locations):
        return {"findings": [{"category": "accuracy", "severity": "high", "description": "d",
                              "recommendation": "r", "locations": locations}]}

    def test_sets_paths_and_located(self):
        audit = self._audit([{"section": "bridge", "quote": "the data was faked"}])
        stats = locate_findings(audit, SECTIONS)
        f = audit["findings"][0]
        assert f["locations"][0]["paths"] == ["bridge.socratic_dialogue[0]"]
        assert f["located"] is True
        assert stats == {"findings": 1, "located": 1, "quotes": 1, "quotes_found": 1}

    def test_model_supplied_paths_and_located_are_overwritten(self):
        audit = self._audit([{"section": "bridge", "quote": "not in the text anywhere", "paths": ["bridge.reframe"]}])
        audit["findings"][0]["located"] = True
        locate_findings(audit, SECTIONS)
        f = audit["findings"][0]
        assert f["locations"][0]["paths"] == []
        assert f["located"] is False

    def test_finding_without_locations_is_unlocated(self):
        audit = {"findings": [{"category": "completeness", "severity": "medium",
                               "description": "d", "recommendation": "r"}]}
        locate_findings(audit, SECTIONS)
        assert audit["findings"][0]["located"] is False
        assert audit["findings"][0]["locations"] == []

    def test_one_found_quote_of_two_locates_the_finding(self):
        audit = self._audit([{"section": "bridge", "quote": "not in the text anywhere"},
                             {"section": "intelligence", "quote": "repeated the claim during 2010"}])
        stats = locate_findings(audit, SECTIONS)
        assert audit["findings"][0]["located"] is True
        assert stats["quotes"] == 2 and stats["quotes_found"] == 1

    def test_malformed_location_entries_are_dropped_from_the_count_not_fatal(self):
        audit = self._audit(["just a string", {"section": "bridge"}, None])
        locate_findings(audit, SECTIONS)
        f = audit["findings"][0]
        assert f["located"] is False
        assert all(loc["paths"] == [] for loc in f["locations"])


class TestContract:
    def test_finding_accepts_locations(self):
        f = AuditFinding(category="accuracy", severity="high", description="d", recommendation="r",
                         locations=[{"section": "bridge", "quote": "the data was faked"}])
        assert f.locations[0].quote == "the data was faked"
        assert f.located is False

    def test_old_finding_without_locations_still_validates(self):
        f = AuditFinding(category="accuracy", severity="high", description="d", recommendation="r")
        assert f.locations == [] and f.located is False

    def test_bad_location_does_not_fail_the_audit(self):
        out = AuditorOutput(verdict="pass_with_warnings", confidence_adjustment=0.0, summary="s",
                            findings=[{"category": "accuracy", "severity": "high", "description": "d",
                                       "recommendation": "r",
                                       "locations": ["bare string", {"section": 3}, {"quote": "x"}]}])
        assert len(out.findings) == 1


class TestOrchestratorLocates:
    def test_report_carries_located_finding(self):
        responses = {**MOCK_RESPONSES}
        responses["adversarial_auditor"] = {
            **MOCK_RESPONSES["adversarial_auditor"], "verdict": "pass_with_warnings",
            "findings": [{"category": "manipulation", "severity": "medium", "description": "d",
                          "recommendation": "r",
                          "locations": [{"section": "bridge", "quote": "Both sides agree on X"}]}],
        }
        result = Orchestrator(make_mock_client(responses)).run("X is true because Y")
        f = result["audit"]["findings"][0]
        assert f["located"] is True
        assert f["locations"][0]["paths"] == ["bridge.issue_overlap"]
        AnalysisReport(**result)


class TestProjectionDropsSuppressedQuotes:
    def _raw(self, locations):
        return {
            "claim": "X",
            "decomposition": {"sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
                              "original_claim": "X", "complexity": "simple"},
            "origins": {"origins": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {"universal_needs": ["safety"], "issue_overlap": "o", "narrative_deconstruction": "d",
                       "perception_gap": "g", "moral_foundations": {},
                       "reframe": "some reframe text here, visible to all",
                       "socratic_dialogue": ["R1"], "prebunking_note": "Watch for the cherry-picked start year."},
            "audit": {"verdict": "pass_with_warnings", "confidence_adjustment": 0.0, "veto": False,
                      "summary": "OK",
                      "findings": [{"category": "accuracy", "severity": "high", "description": "d",
                                    "recommendation": "r", "locations": locations,
                                    "located": any(loc.get("paths") for loc in locations)}]},
            "overall_confidence": 0.7, "method": "method_2", "degraded": False, "degraded_reason": None,
        }

    def test_quote_from_suppressed_field_is_removed(self):
        raw = self._raw([{"section": "bridge", "quote": "the cherry-picked start year",
                          "paths": ["bridge.prebunking_note"]}])
        out = project_analysis(raw, suppressed=frozenset({"prebunking_note"}))
        f = out["data"]["audit"]["findings"][0]
        assert "cherry-picked" not in json.dumps(f)
        assert f["located"] is False
        assert out["audit_redacted"] is True

    def test_unlocated_quote_is_removed_when_fields_are_suppressed(self):
        raw = self._raw([{"section": "bridge", "quote": "the cherry-picked start year", "paths": []}])
        out = project_analysis(raw, suppressed=frozenset({"prebunking_note"}))
        assert "cherry-picked" not in json.dumps(out["data"]["audit"])

    def test_quote_from_visible_field_is_kept(self):
        raw = self._raw([{"section": "bridge", "quote": "some reframe text here", "paths": ["bridge.reframe"]}])
        out = project_analysis(raw, suppressed=frozenset({"prebunking_note"}))
        f = out["data"]["audit"]["findings"][0]
        assert f["locations"][0]["quote"] == "some reframe text here"
        assert f["located"] is True

    def test_no_suppression_keeps_quotes(self):
        raw = self._raw([{"section": "bridge", "quote": "the cherry-picked start year",
                          "paths": ["bridge.prebunking_note"]}])
        out = project_analysis(raw)
        assert out["data"]["audit"]["findings"][0]["locations"][0]["quote"] == "the cherry-picked start year"


class TestAuditorPromptAsksForQuotes:
    def test_package_prompt_requests_locations(self):
        from huginn_muninn.agents.auditor import AuditorAgent
        from unittest.mock import MagicMock
        p = AuditorAgent(MagicMock()).build_prompt({"original_claim": "X", "decomposition": {}})
        assert '"locations"' in p and '"section"' in p and '"quote"' in p
        assert "copied exactly" in p

    def test_runner_prompt_carries_the_same_block(self):
        from pathlib import Path
        from huginn_muninn.agents.auditor import AuditorAgent
        from unittest.mock import MagicMock

        def block(text):
            start = text.index("LOCATING FINDINGS:")
            return text[start:text.index("VETO is a RARE", start)]
        runner = (Path(__file__).parent / "run_scenario_claude.py").read_text(encoding="utf-8")
        p = AuditorAgent(MagicMock()).build_prompt({"original_claim": "X"})
        assert block(p) == block(runner)


class TestReviewFindings:
    """Cases from the design C review (2026-11-10)."""

    def _raw(self, locations):
        return TestProjectionDropsSuppressedQuotes()._raw(locations)

    def test_veto_drops_quotes_from_the_withheld_bridge(self):
        responses = {**MOCK_RESPONSES}
        responses["adversarial_auditor"] = {
            **MOCK_RESPONSES["adversarial_auditor"], "verdict": "fail", "veto": True,
            "findings": [{"category": "manipulation", "severity": "critical", "description": "d",
                          "recommendation": "r",
                          "locations": [{"section": "bridge", "quote": "Both sides agree on X"}]}],
        }
        result = Orchestrator(make_mock_client(responses)).run("X is true because Y")
        assert result["bridge_withheld"] is True
        assert "Both sides agree" not in json.dumps(result["audit"])
        assert result["audit"]["findings"][0]["located"] is False

    def test_forged_path_is_recomputed_before_projection(self):
        raw = self._raw([{"section": "bridge", "quote": "Watch for the cherry-picked start year.",
                          "paths": ["bridge.reframe"]}])
        out = project_analysis(raw, suppressed=frozenset({"prebunking_note"}))
        assert "cherry-picked" not in json.dumps(out["data"]["audit"])
        assert out["audit_redacted"] is True

    def test_report_ignores_producer_located_flag(self):
        raw = self._raw([])
        raw["audit"]["findings"][0]["located"] = True
        assert AnalysisReport(**raw).audit.findings[0].located is False

    def test_non_boolean_located_does_not_fail_the_audit(self):
        for v in (None, "unknown", "n/a", 1):
            out = AuditorOutput(verdict="pass_with_warnings", confidence_adjustment=0.0, summary="s",
                                findings=[{"category": "accuracy", "severity": "high", "description": "d",
                                           "recommendation": "r", "located": v}])
            assert out.findings[0].located is False

    def test_literal_backslash_and_entity_text_is_found(self):
        s = {"bridge": {"reframe": r"Save it under C:\temp\new files and reopen the report.",
                        "issue_overlap": "The page title reads Tom &quot;The Hammer&quot; Smith on climate."}}
        assert locate_quote(s, "bridge", r"under C:\temp\new files and reopen") == ["bridge.reframe"]
        assert locate_quote(s, "bridge", "reads Tom &quot;The Hammer&quot; Smith") == ["bridge.issue_overlap"]

    def test_section_name_is_normalised(self):
        for name in ("Bridge", " bridge ", "BRIDGE", "bridge.socratic_dialogue", "bridge|ttps"):
            assert locate_quote(SECTIONS, name, "the data was faked") == ["bridge.socratic_dialogue[0]"], name

    def test_three_word_fragment_is_not_found(self):
        assert locate_quote(SECTIONS, "bridge", "data was faked") == []

    def test_locations_are_capped_and_long_quotes_dropped(self):
        locs = [{"section": "bridge", "quote": "x" * 401}] + [{"section": "bridge", "quote": "q"}] * 5
        f = AuditFinding(category="accuracy", severity="high", description="d", recommendation="r",
                         locations=locs)
        assert len(f.locations) == 3
        assert f.locations[0].quote == ""

    def test_single_location_object_is_kept(self):
        f = AuditFinding(category="accuracy", severity="high", description="d", recommendation="r",
                         locations={"section": "bridge", "quote": "the data was faked"})
        assert [loc.quote for loc in f.locations] == ["the data was faked"]

    def test_quote_the_scrub_would_change_is_dropped(self):
        raw = self._raw([{"section": "bridge", "quote": "The prebunking note idea is common"}])
        raw["bridge"]["reframe"] = "The prebunking note idea is common in the literature."
        out = project_analysis(raw, suppressed=frozenset({"prebunking_note"}))
        f = out["data"]["audit"]["findings"][0]
        assert f["locations"] == [] and f["located"] is False
        assert out["audit_redacted"] is True


class TestCliShowsPassages:
    def _report(self, paths, veto=False):
        return {
            "overall_confidence": 0.5, "degraded": False, "bridge_withheld": veto,
            "decomposition": {"sub_claims": [], "complexity": "simple"},
            "bridge": {"universal_needs": ["fairness"], "reframe": "Round one says the data was faked.",
                       "socratic_dialogue": ["R1"]},
            "audit": {"verdict": "pass_with_warnings", "veto": veto, "summary": "s", "findings": [
                {"severity": "medium", "description": "Overstated.",
                 "locations": [{"section": "bridge", "quote": "the data was faked", "paths": paths}]}]},
        }

    def test_located_passage_is_printed(self, capsys):
        from huginn_muninn.cli import _print_analysis
        _print_analysis(self._report(["bridge.reframe"]))
        assert 'about bridge.reframe: "the data was faked"' in capsys.readouterr().out

    def test_passage_is_rechecked_not_trusted(self, capsys):
        from huginn_muninn.cli import _print_analysis
        r = self._report(["bridge.reframe"])
        r["bridge"]["reframe"] = "Something else entirely here."
        _print_analysis(r)
        assert "the data was faked" not in capsys.readouterr().out

    def test_veto_hides_bridge_passages(self, capsys):
        from huginn_muninn.cli import _print_analysis
        _print_analysis(self._report(["bridge.reframe"], veto=True))
        assert "the data was faked" not in capsys.readouterr().out
