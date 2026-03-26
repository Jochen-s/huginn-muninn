"""Shared test fixtures for Huginn & Muninn."""
import json

import httpx
import pytest


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
def ollama_client():
    """Provide a real OllamaClient. Skip test if Ollama unavailable."""
    from huginn_muninn.llm import OllamaClient
    if not _ollama_available():
        pytest.skip("Ollama not available -- skipping E2E test")
    with OllamaClient(model="qwen3.5:9b") as client:
        yield client


@pytest.fixture
def sample_claim():
    return "Vaccines cause autism in children according to a 2024 study."


@pytest.fixture
def sample_nonpolarizing_claim():
    return "The Eiffel Tower is 330 meters tall."
