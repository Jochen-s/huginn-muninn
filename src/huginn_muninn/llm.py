"""LLM client abstraction: Ollama + OpenAI-compatible providers."""
from __future__ import annotations

import json
import logging
import re
from typing import Protocol, runtime_checkable

import httpx

log = logging.getLogger(__name__)


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM clients. OllamaClient and OpenAIClient satisfy this."""

    model: str

    def generate(self, prompt: str) -> str: ...
    def check_available(self) -> bool: ...
    def close(self) -> None: ...


def extract_json_from_response(text: str) -> dict:
    """Extract JSON object from LLM response, handling markdown fences."""
    # Try markdown code block first
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Try parsing the full text as JSON (handles clean responses)
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass

    # Fallback: LLM emitted narrative with embedded JSON objects.
    # Prefer the dict with the most top-level keys (the actual response
    # is always larger than small inline fragments).
    decoder = json.JSONDecoder()
    best: dict | None = None
    idx = text.find("{")
    while idx != -1:
        try:
            obj, _ = decoder.raw_decode(text, idx)
            if isinstance(obj, dict):
                if best is None or len(obj) > len(best):
                    best = obj
        except json.JSONDecodeError:
            pass
        idx = text.find("{", idx + 1)
    if best is not None:
        return best
    log.debug("No valid JSON in LLM response (len=%d): %.500s", len(text), text)
    raise ValueError("LLM response did not contain valid JSON")


class OllamaClient:
    """Client for Ollama local LLM inference."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3.5:9b",
        timeout: float = 300.0,
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def generate(self, prompt: str) -> str:
        """Send prompt to Ollama and return the response text."""
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096},
        }
        # Disable thinking mode for Qwen 3.x models via API parameter
        # (thinking wastes token budget on internal reasoning for structured output)
        if "qwen3" in self.model.lower():
            payload["think"] = False
        response = self._client.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        return response.json()["response"]

    def check_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            resp = self._client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            base_model = self.model.split(":")[0]
            return any(base_model in m for m in models)
        except (httpx.HTTPError, KeyError):
            return False

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class OpenAIClient:
    """Client for OpenAI-compatible APIs (LiteLLM, OpenRouter, Groq, etc.)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(timeout=timeout, headers=headers)

    def generate(self, prompt: str) -> str:
        """Send prompt via /v1/chat/completions and return content."""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        url = f"{self.base_url}/v1/chat/completions"
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def check_available(self) -> bool:
        """Check if the OpenAI-compatible API is reachable and the model exists."""
        try:
            resp = self._client.get(f"{self.base_url}/v1/models")
            resp.raise_for_status()
            models = [m["id"] for m in resp.json().get("data", [])]
            return self.model in models or any(self.model in m for m in models)
        except (httpx.HTTPError, KeyError):
            return False

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class AnthropicClient:
    """Client for Anthropic API (Claude models)."""

    def __init__(
        self,
        model: str = "claude-opus-4-6",
        api_key: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        import anthropic

        self.model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def generate(self, prompt: str) -> str:
        """Send prompt via Anthropic Messages API and return content."""
        message = self._client.messages.create(
            model=self.model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def check_available(self) -> bool:
        """Check if Anthropic API is reachable."""
        try:
            self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def create_client(
    provider: str,
    base_url: str,
    model: str,
    api_key: str | None = None,
    **kwargs,
) -> LLMClient:
    """Factory: create an LLMClient from provider name."""
    if provider == "ollama":
        return OllamaClient(base_url=base_url, model=model, **kwargs)
    elif provider == "openai":
        return OpenAIClient(
            base_url=base_url,
            model=model,
            api_key=api_key or "",
            **kwargs,
        )
    elif provider == "anthropic":
        return AnthropicClient(
            model=model,
            api_key=api_key,
            **kwargs,
        )
    else:
        msg = f"Unknown provider: {provider}"
        raise ValueError(msg)
