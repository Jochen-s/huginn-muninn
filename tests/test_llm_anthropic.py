"""Tests for AnthropicClient request shape and response handling (SDK mocked)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("anthropic")

from huginn_muninn.llm import AnthropicClient, LLMClient  # noqa: E402


def _message(blocks, stop_reason="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop_reason, stop_details=None)


def _text(t):
    return SimpleNamespace(type="text", text=t)


def _thinking():
    return SimpleNamespace(type="thinking", thinking="")


class _FakeMessages:
    def __init__(self, reply):
        self.reply = reply
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.reply


def _client(reply, **kw) -> tuple[AnthropicClient, _FakeMessages]:
    c = AnthropicClient(api_key="test-key", **kw)
    fake = _FakeMessages(reply)
    c._client = SimpleNamespace(messages=fake)
    return c, fake


class TestAnthropicClient:
    def test_default_model_is_opus_5_5(self):
        c, _ = _client(_message([_text("x")]))
        assert c.model == "claude-opus-5-5"

    def test_satisfies_protocol(self):
        c, _ = _client(_message([_text("x")]))
        assert isinstance(c, LLMClient)

    def test_no_sampling_parameters_sent(self):
        c, fake = _client(_message([_text("x")]))
        c.generate("hi")
        assert not {"temperature", "top_p", "top_k"} & fake.calls[0].keys()

    def test_effort_sent_in_output_config(self):
        c, fake = _client(_message([_text("x")]), effort="medium")
        c.generate("hi")
        assert fake.calls[0]["output_config"] == {"effort": "medium"}

    def test_no_output_config_without_effort(self):
        c, fake = _client(_message([_text("x")]))
        c.generate("hi")
        assert "output_config" not in fake.calls[0]

    def test_text_extracted_after_thinking_block(self):
        c, _ = _client(_message([_thinking(), _text('{"a": 1}')]))
        assert c.generate("hi") == '{"a": 1}'

    def test_multiple_text_blocks_joined(self):
        c, _ = _client(_message([_text("ab"), _thinking(), _text("cd")]))
        assert c.generate("hi") == "abcd"

    def test_refusal_raises(self):
        c, _ = _client(_message([], stop_reason="refusal"))
        with pytest.raises(RuntimeError, match="refus"):
            c.generate("hi")

    def test_max_tokens_truncation_raises(self):
        c, _ = _client(_message([_text('{"a":')], stop_reason="max_tokens"))
        with pytest.raises(RuntimeError, match="max_tokens"):
            c.generate("hi")



def test_check_available_lists_models_without_a_paid_call():
    from types import SimpleNamespace

    c, fake = _client("x")
    calls = []
    c._client = SimpleNamespace(messages=fake, models=SimpleNamespace(list=lambda **kw: calls.append(kw)))
    assert c.check_available() is True
    assert calls == [{"limit": 1}]
    assert fake.calls == []
