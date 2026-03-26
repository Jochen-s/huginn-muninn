"""Tests for CLI interface."""
import json

import pytest
from click.testing import CliRunner

from huginn_muninn.cli import main
from conftest import extract_json_from_cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Huginn" in result.output or "fact-check" in result.output.lower()

    def test_check_requires_claim(self, runner):
        result = runner.invoke(main, ["check"])
        assert result.exit_code != 0

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestAutoEscalate:
    @pytest.fixture
    def _mock_db(self):
        """Provide a mock HuginnDB that returns no cached data."""
        from unittest.mock import MagicMock, patch
        mock_db = MagicMock()
        mock_db.get_cached_verdict.return_value = None
        mock_db.get_cached_analysis.return_value = None
        with patch("huginn_muninn.cli.HuginnDB") as mock_db_cls:
            mock_db_cls.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_db_cls.return_value.__exit__ = MagicMock(return_value=False)
            yield mock_db_cls, mock_db

    def test_auto_escalate_triggers_method2(self, runner, _mock_db):
        """When --auto-escalate is set and Method 1 says should_escalate, Method 2 runs."""
        from unittest.mock import MagicMock, patch

        # Method 1 output with should_escalate=True
        p2_data = {
            "verdict": "mixed",
            "confidence": 0.5,
            "evidence_for": [{"text": "e", "source_url": "http://x.com", "source_tier": 2, "supports_claim": True}],
            "evidence_against": [{"text": "e", "source_url": "http://y.com", "source_tier": 1, "supports_claim": False}],
            "unknowns": [],
            "abstain_reason": None,
            "common_ground": {
                "shared_concern": "Test",
                "framing_technique": "false_dichotomy",
                "technique_explanation": "Test",
                "reflection": "What do we share?",
            },
            "escalation": {
                "score": 0.7,
                "should_escalate": True,
                "reason": "Complex claim",
            },
        }

        # Method 2 output (from orchestrator)
        m2_result = {
            "claim": "test claim",
            "decomposition": {
                "sub_claims": [{"text": "test", "type": "factual", "verifiable": True}],
                "original_claim": "test claim",
                "complexity": "simple",
            },
            "origins": {"origins": [], "mutations": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["fairness"],
                "issue_overlap": "",
                "narrative_deconstruction": "",
                "perception_gap": "",
                "moral_foundations": {},
                "reframe": "",
                "socratic_dialogue": ["Round 1"],
            },
            "audit": {
                "verdict": "pass",
                "findings": [],
                "confidence_adjustment": 0.0,
                "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.7,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

        mock_client = MagicMock()
        mock_client.check_available.return_value = True
        mock_client.generate.side_effect = [
            json.dumps({"evidence_for": [], "evidence_against": [], "unknowns": [],
                         "claim_complexity": "complex", "polarization_detected": True,
                         "groups_involved": ["A", "B"]}),
            json.dumps(p2_data),
        ]

        mock_orch_instance = MagicMock()
        mock_orch_instance.run.return_value = m2_result

        with patch("huginn_muninn.cli.OllamaClient") as mock_client_cls, \
             patch("huginn_muninn.orchestrator.Orchestrator", return_value=mock_orch_instance):
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = runner.invoke(main, ["check", "--auto-escalate", "--json-output", "test claim"])

        assert result.exit_code == 0, result.output
        output = extract_json_from_cli(result.output)
        assert "method_1" in output
        assert "method_2" in output

    def test_auto_escalate_skips_when_not_needed(self, runner, _mock_db):
        """When should_escalate is False, Method 2 does not run."""
        from unittest.mock import MagicMock, patch

        p2_data = {
            "verdict": "true",
            "confidence": 0.95,
            "evidence_for": [{"text": "e", "source_url": "http://x.com", "source_tier": 1, "supports_claim": True}],
            "evidence_against": [],
            "unknowns": [],
            "abstain_reason": None,
            "common_ground": {
                "shared_concern": "Test",
                "framing_technique": "none_detected",
                "technique_explanation": "None",
                "reflection": "Is this not interesting?",
            },
            "escalation": {
                "score": 0.1,
                "should_escalate": False,
                "reason": "Simple claim",
            },
        }

        mock_client = MagicMock()
        mock_client.check_available.return_value = True
        mock_client.generate.side_effect = [
            json.dumps({"evidence_for": [], "evidence_against": [], "unknowns": [],
                         "claim_complexity": "simple", "polarization_detected": False,
                         "groups_involved": []}),
            json.dumps(p2_data),
        ]

        with patch("huginn_muninn.cli.OllamaClient") as mock_client_cls:
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = runner.invoke(main, ["check", "--auto-escalate", "--json-output", "simple claim"])

        assert result.exit_code == 0, result.output
        output = extract_json_from_cli(result.output)
        assert output.get("verdict") == "true"
        assert "method_2" not in output

    def test_auto_escalate_uses_cached_verdict_for_method2(self, runner):
        """When cached verdict has should_escalate=True, skip Method 1 and run Method 2."""
        from unittest.mock import MagicMock, patch

        cached_verdict = {
            "verdict": "mixed",
            "confidence": 0.5,
            "evidence_for": [{"text": "e", "source_url": "http://x.com", "source_tier": 2, "supports_claim": True}],
            "evidence_against": [{"text": "e", "source_url": "http://y.com", "source_tier": 1, "supports_claim": False}],
            "unknowns": [],
            "abstain_reason": None,
            "common_ground": {
                "shared_concern": "Test",
                "framing_technique": "false_dichotomy",
                "technique_explanation": "Test",
                "reflection": "What do we share?",
            },
            "escalation": {
                "score": 0.7,
                "should_escalate": True,
                "reason": "Complex claim",
            },
        }

        m2_result = {
            "claim": "cached claim",
            "decomposition": {
                "sub_claims": [{"text": "test", "type": "factual", "verifiable": True}],
                "original_claim": "cached claim",
                "complexity": "simple",
            },
            "origins": {"origins": [], "mutations": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["fairness"],
                "issue_overlap": "",
                "narrative_deconstruction": "",
                "perception_gap": "",
                "moral_foundations": {},
                "reframe": "",
                "socratic_dialogue": ["Round 1"],
            },
            "audit": {
                "verdict": "pass",
                "findings": [],
                "confidence_adjustment": 0.0,
                "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.7,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

        mock_db = MagicMock()
        mock_db.get_cached_verdict.return_value = cached_verdict

        mock_client = MagicMock()
        mock_client.check_available.return_value = True

        mock_orch_instance = MagicMock()
        mock_orch_instance.run.return_value = m2_result

        with patch("huginn_muninn.cli.HuginnDB") as mock_db_cls, \
             patch("huginn_muninn.cli.OllamaClient") as mock_client_cls, \
             patch("huginn_muninn.orchestrator.Orchestrator", return_value=mock_orch_instance):
            mock_db_cls.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_db_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = runner.invoke(main, ["check", "--auto-escalate", "--json-output", "cached claim"])

        assert result.exit_code == 0, result.output
        output = extract_json_from_cli(result.output)
        assert "method_1" in output
        assert "method_2" in output
        # Method 1 should NOT have been called — we used the cache
        mock_client.generate.assert_not_called()

    def test_auto_escalate_flag_in_help(self, runner):
        """The --auto-escalate flag should appear in check help."""
        result = runner.invoke(main, ["check", "--help"])
        assert "--auto-escalate" in result.output


class TestAnalyzeCLI:
    def test_analyze_help(self):
        from click.testing import CliRunner
        from huginn_muninn.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Method 2" in result.output or "Deep analysis" in result.output

    def test_analyze_requires_claim(self):
        from click.testing import CliRunner
        from huginn_muninn.cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["analyze"])
        assert result.exit_code != 0
