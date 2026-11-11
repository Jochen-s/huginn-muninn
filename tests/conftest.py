"""Shared test fixtures for Huginn & Muninn."""
import json
import os

import httpx
import pytest

# End-to-end tests run on the newest Claude model first, through the Claude
# Code CLI (the operator's login, no API key). HUGINN_E2E_PROVIDER=ollama runs
# them on the local model instead. A missing provider skips with its name in
# the reason; it never falls back to another model.
E2E_PROVIDER = os.environ.get("HUGINN_E2E_PROVIDER", "claude-code")
E2E_DEFAULT_MODELS = {"claude-code": "claude-fable-5-2", "ollama": "qwen3.5:9b"}
E2E_MODEL = os.environ.get("HUGINN_E2E_MODEL") or E2E_DEFAULT_MODELS.get(E2E_PROVIDER, "")
# A Claude run must finish every agent; a small local model may drop one.
E2E_STRICT = E2E_PROVIDER == "claude-code"


def assert_no_agent_failures(report: dict) -> None:
    """On a strict run, a degraded report is allowed only for an Auditor veto,
    which is the pipeline working as designed."""
    if not E2E_STRICT or not report.get("degraded"):
        return
    reason = report.get("degraded_reason") or ""
    assert reason.startswith("Auditor veto"), f"{E2E_MODEL} degraded: {reason}"


def extract_json_from_cli(text: str) -> dict:
    """Extract the first JSON object from mixed CLI output (stderr + stdout)."""
    start = text.index("{")
    return json.loads(text[start:])


def _ollama_available(model: str = "qwen3.5:9b") -> bool:
    """Check if Ollama is running and the model is pulled."""
    try:
        resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        base = model.split(":")[0]
        return any(base in m for m in models)
    except (httpx.HTTPError, KeyError):
        return False


@pytest.fixture
def llm_client():
    """The real client the E2E tests run on (see E2E_PROVIDER)."""
    from huginn_muninn.llm import ClaudeCodeClient, OllamaClient
    if E2E_PROVIDER == "claude-code":
        client = ClaudeCodeClient(model=E2E_MODEL)
        if not client.check_available():
            pytest.skip(f"claude CLI not on PATH -- skipping E2E test on {E2E_MODEL}")
    elif E2E_PROVIDER == "ollama":
        if not _ollama_available(E2E_MODEL):
            pytest.skip(f"Ollama or {E2E_MODEL} not available -- skipping E2E test")
        client = OllamaClient(model=E2E_MODEL)
    else:
        pytest.fail(f"HUGINN_E2E_PROVIDER={E2E_PROVIDER!r}: use claude-code or ollama")
    with client:
        yield client


@pytest.fixture
def e2e_cli_args(llm_client):
    """Group options that point the CLI at the same provider and model."""
    return ["--provider", E2E_PROVIDER, "--model", E2E_MODEL]


@pytest.fixture
def sample_claim():
    return "Vaccines cause autism in children according to a 2024 study."


@pytest.fixture
def sample_nonpolarizing_claim():
    return "The Eiffel Tower is 330 meters tall."
