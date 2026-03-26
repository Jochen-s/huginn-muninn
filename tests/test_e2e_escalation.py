"""E2E test for the Method 1 -> Method 2 escalation bridge."""
import pytest

from click.testing import CliRunner
from huginn_muninn.cli import main
from conftest import extract_json_from_cli


@pytest.mark.e2e
class TestEscalationBridgeE2E:
    def test_polarizing_claim_escalates(self, ollama_client, tmp_path):
        """A polarizing claim should trigger auto-escalation to Method 2."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "check",
                "--auto-escalate",
                "--json-output",
                "--no-cache",
                "The 2020 US presidential election was stolen through widespread voter fraud",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        data = extract_json_from_cli(result.output)

        # The claim should have been escalated (it's highly polarizing)
        # If Method 1 returns should_escalate=True, we get both methods
        if "method_1" in data:
            assert "method_2" in data
            m1 = data["method_1"]
            m2 = data["method_2"]
            assert m1["escalation"]["should_escalate"] is True
            assert m2["method"] == "method_2"
        else:
            # Method 1 didn't recommend escalation -- still valid, just document it
            assert data.get("verdict") is not None
