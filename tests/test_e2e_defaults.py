"""The E2E tests run on Claude Fable 5.2 unless the operator picks another model."""
import conftest


def test_e2e_default_provider_is_the_claude_cli():
    assert conftest.E2E_DEFAULT_MODELS["claude-code"] == "claude-fable-5-2"


def test_e2e_runs_on_fable_when_nothing_is_set(monkeypatch):
    import importlib
    monkeypatch.delenv("HUGINN_E2E_PROVIDER", raising=False)
    monkeypatch.delenv("HUGINN_E2E_MODEL", raising=False)
    fresh = importlib.reload(conftest)
    try:
        assert (fresh.E2E_PROVIDER, fresh.E2E_MODEL) == ("claude-code", "claude-fable-5-2")
    finally:
        importlib.reload(conftest)


def test_strict_check_fails_on_an_agent_failure(monkeypatch):
    import pytest
    monkeypatch.setattr(conftest, "E2E_STRICT", True)
    with pytest.raises(AssertionError, match="Agent failures"):
        conftest.assert_no_agent_failures({"degraded": True, "degraded_reason": "Agent failures: tracer"})


def test_strict_check_allows_a_veto(monkeypatch):
    monkeypatch.setattr(conftest, "E2E_STRICT", True)
    conftest.assert_no_agent_failures({"degraded": True, "degraded_reason": "Auditor veto: unsafe bridge"})
