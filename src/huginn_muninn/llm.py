"""LLM client abstraction: Ollama + OpenAI-compatible providers."""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
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


def extract_json_from_response(
    text: str, expected_keys: frozenset[str] | set[str] | None = None
) -> dict:
    """Extract JSON object from LLM response, handling markdown fences.

    `expected_keys` are the top-level keys of the schema the caller will
    validate against. When the response holds several JSON objects (the model
    narrated, or echoed a JSON blob that was embedded in the analysed claim),
    the candidate sharing the most keys with the schema wins; size is only
    the tie-break. Before 2026-09-03 the largest object won outright, so a
    claim carrying a large decoy object could supply the verdict (K-005)."""
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
    best_rank: tuple[int, int] = (-1, -1)
    keys = frozenset(expected_keys) if expected_keys else frozenset()
    idx = text.find("{")
    while idx != -1:
        try:
            obj, _ = decoder.raw_decode(text, idx)
            if isinstance(obj, dict):
                rank = (len(keys & obj.keys()), len(obj))
                if rank > best_rank:
                    best, best_rank = obj, rank
        except json.JSONDecodeError:
            pass
        idx = text.find("{", idx + 1)
    if best is not None:
        return best
    log.debug("No valid JSON in LLM response (len=%d): %.500s", len(text), text)
    raise ValueError("LLM response did not contain valid JSON")


class OllamaClient:
    """Client for Ollama local LLM inference."""

    provider = "ollama"

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3.5:9b",
        timeout: float | None = None,
        num_ctx: int | None = None,
    ):
        # Larger local models need more than 300 s for a long agent answer;
        # HUGINN_OLLAMA_NUM_CTX keeps a big model fully on the GPU.
        if timeout is None:
            timeout = float(os.environ.get("HUGINN_OLLAMA_TIMEOUT", "300"))
        if num_ctx is None and os.environ.get("HUGINN_OLLAMA_NUM_CTX"):
            num_ctx = int(os.environ["HUGINN_OLLAMA_NUM_CTX"])
        self.base_url = base_url
        self.model = model
        self.timeout = float(timeout)
        self.num_ctx = num_ctx
        self._client = httpx.Client(timeout=self.timeout)

    def generate(self, prompt: str) -> str:
        """Send prompt to Ollama and return the response text."""
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096},
        }
        if self.num_ctx:
            payload["options"]["num_ctx"] = self.num_ctx
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

    provider = "openai"

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

    provider = "anthropic"

    def __init__(
        self,
        model: str = "claude-opus-5-5",
        api_key: str | None = None,
        effort: str | None = None,
        max_tokens: int = 16000,
    ):
        # No temperature: API version 2026-10-21 (the SDK 2.x default) rejects
        # sampling parameters on every model. Thinking is always on for current
        # models and counts against max_tokens; effort is the depth control.
        import anthropic

        self.model = model
        self.effort = effort
        self._max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def generate(self, prompt: str) -> str:
        """Send prompt via Anthropic Messages API and return the text blocks."""
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self._max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        message = self._client.messages.create(**kwargs)
        if message.stop_reason == "refusal":
            category = getattr(message.stop_details, "category", None)
            raise RuntimeError(f"{self.model} refused the request (category: {category})")
        if message.stop_reason == "max_tokens":
            raise RuntimeError(f"{self.model} hit max_tokens={self._max_tokens}; output truncated")
        return "".join(b.text for b in message.content if b.type == "text")

    def check_available(self) -> bool:
        """Check that the API key works, without spending tokens (models list)."""
        try:
            self._client.models.list(limit=1)
            return True
        except Exception:
            return False

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class ClaudeCodeClient:
    """Runs each prompt through the headless Claude Code CLI (`claude -p`).

    Uses the operator's Claude Code login instead of an API key. The flags strip
    the operator's own harness (settings, hooks, plugins, MCP servers, tools,
    slash commands) and the fixed system prompt replaces Claude Code's agent
    prompt, so the model sees the analysis prompt and little else. It runs in a
    neutral temp directory so no project CLAUDE.md is discovered."""

    provider = "claude-code"
    SYSTEM_PROMPT = (
        "You are an analysis component inside a fact-checking pipeline. "
        "Follow the user's instructions exactly and return only the requested output."
    )

    def __init__(
        self,
        model: str = "claude-opus-5-5",
        effort: str | None = None,
        timeout: float = 900.0,
        **_ignored,
    ):
        self.model = model
        self.effort = effort
        self.timeout = float(timeout)
        self.total_cost_usd = 0.0
        self._workdir = Path(tempfile.gettempdir()) / "huginn-claude-code"

    def _command(self) -> list[str]:
        cmd = [
            shutil.which("claude") or "claude", "-p",
            "--model", self.model,
            "--output-format", "json",
            "--system-prompt", self.SYSTEM_PROMPT,
            "--setting-sources", "",
            "--strict-mcp-config",
            "--tools", "",
            "--disable-slash-commands",
            "--no-session-persistence",
        ]
        if self.effort:
            cmd += ["--effort", self.effort]
        return cmd

    def generate(self, prompt: str) -> str:
        """Send prompt on stdin and return the CLI's final result text."""
        self._workdir.mkdir(exist_ok=True)
        try:
            proc = subprocess.run(
                self._command(), input=prompt, capture_output=True, text=True,
                encoding="utf-8", timeout=self.timeout, cwd=self._workdir,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"claude CLI timed out after {self.timeout:.0f}s") from e
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI exited {proc.returncode}: {(proc.stderr or proc.stdout)[:500]}")
        data = json.loads(proc.stdout)
        self.total_cost_usd += float(data.get("total_cost_usd") or 0.0)
        if data.get("is_error"):
            raise RuntimeError(f"claude CLI error: {str(data.get('result'))[:500]}")
        return data.get("result") or ""

    def check_available(self) -> bool:
        """True when the claude CLI is on PATH (no model call is spent)."""
        return shutil.which("claude") is not None

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# Providers whose clients take an effort setting. The CLI, the API and the
# cache key all read this one tuple, so they cannot drift apart.
EFFORT_PROVIDERS = ("anthropic", "claude-code")


def cache_key(provider: str, model: str, effort: str | None = None) -> str:
    """Name of the model that produced a cached result: provider/model, plus
    @effort where the provider uses it. Results are served only to the same key."""
    key = f"{provider}/{model}"
    if effort and provider in EFFORT_PROVIDERS:
        key += f"@{effort}"
    return key


def client_cache_key(client: object) -> str | None:
    """cache_key for a client instance; None for a client that names no provider."""
    provider = getattr(client, "provider", None)
    model = getattr(client, "model", None)
    if not isinstance(provider, str) or not isinstance(model, str):
        return None
    return cache_key(provider, model, getattr(client, "effort", None))


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
    elif provider == "claude-code":
        return ClaudeCodeClient(model=model, **kwargs)
    else:
        msg = f"Unknown provider: {provider}"
        raise ValueError(msg)
