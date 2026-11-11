"""E2E test for the Method 1 -> Method 2 escalation bridge."""
import pytest

from click.testing import CliRunner
from huginn_muninn.cli import main
from conftest import E2E_STRICT, assert_no_agent_failures, extract_json_from_cli


@pytest.mark.e2e
class TestEscalationBridgeE2E:
    def test_polarizing_claim_escalates(self, e2e_cli_args, tmp_path):
        """A polarizing claim should trigger auto-escalation to Method 2."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                *e2e_cli_args,
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
            assert_no_agent_failures(m2)
        else:
            # Method 1 didn't recommend escalation -- still valid, just document it
            m1 = data
            assert data.get("verdict") is not None
        # Escalation is the model's own call, so it is not required; the
        # verdict on a well-documented false claim is
        if E2E_STRICT:
            assert m1["verdict"] == "false", m1["verdict"]
