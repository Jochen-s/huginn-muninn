"""Tests for OpenAIClient, LLMClient Protocol, and create_client factory."""
from __future__ import annotations

import json

import httpx
import pytest

from huginn_muninn.llm import (
    LLMClient,
    OllamaClient,
    OpenAIClient,
    create_client,
)


def _openai_response(content: str = "Hello") -> dict:
    return {"choices": [{"message": {"content": content}}]}


class TestLLMClientProtocol:
    def test_ollama_satisfies_protocol(self):
        assert isinstance(OllamaClient(), LLMClient)

    def test_openai_satisfies_protocol(self):
        client = OpenAIClient(base_url="http://localhost:4000", model="test")
        assert isinstance(client, LLMClient)
        client.close()

    def test_arbitrary_object_does_not_satisfy(self):
        assert not isinstance(object(), LLMClient)


class TestOpenAIClient:
    def test_generate_extracts_content(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("test response"),
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="gpt-4o")
        result = client.generate("Hello")
        assert result == "test response"
        client.close()

    def test_generate_sends_correct_payload(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("ok"),
        )
        client = OpenAIClient(
            base_url="http://localhost:4000",
            model="gpt-4o",
            temperature=0.5,
            max_tokens=2048,
        )
        client.generate("test prompt")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["model"] == "gpt-4o"
        assert body["messages"] == [{"role": "user", "content": "test prompt"}]
        assert body["temperature"] == 0.5
        assert body["max_tokens"] == 2048
        client.close()

    def test_api_key_sent_as_bearer(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("ok"),
        )
        client = OpenAIClient(
            base_url="http://localhost:4000",
            model="test",
            api_key="sk-test-key",
        )
        client.generate("hello")
        request = httpx_mock.get_request()
        assert request.headers["authorization"] == "Bearer sk-test-key"
        client.close()

    def test_no_api_key_no_auth_header(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("ok"),
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="test")
        client.generate("hello")
        request = httpx_mock.get_request()
        assert "authorization" not in request.headers
        client.close()

    def test_trailing_slash_stripped_from_base_url(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("ok"),
        )
        client = OpenAIClient(base_url="http://localhost:4000/", model="test")
        client.generate("hello")
        request = httpx_mock.get_request()
        assert "//" not in str(request.url).replace("http://", "")
        client.close()

    def test_http_error_propagates(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            status_code=500,
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="test")
        with pytest.raises(httpx.HTTPStatusError):
            client.generate("hello")
        client.close()

    def test_context_manager(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/chat/completions",
            json=_openai_response("ok"),
        )
        with OpenAIClient(base_url="http://localhost:4000", model="test") as client:
            result = client.generate("hello")
            assert result == "ok"


class TestOpenAIClientCheckAvailable:
    def test_model_found_exact_match(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/models",
            json={"data": [{"id": "default"}, {"id": "gpt-4o"}]},
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="default")
        assert client.check_available() is True
        client.close()

    def test_model_found_substring_match(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/models",
            json={"data": [{"id": "qwen3-coder-30b-a3b"}]},
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="qwen3-coder")
        assert client.check_available() is True
        client.close()

    def test_model_not_found(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/models",
            json={"data": [{"id": "gpt-4o"}]},
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="nonexistent")
        assert client.check_available() is False
        client.close()

    def test_http_error_returns_false(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/models",
            status_code=500,
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="test")
        assert client.check_available() is False
        client.close()

    def test_empty_data_returns_false(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:4000/v1/models",
            json={"data": []},
        )
        client = OpenAIClient(base_url="http://localhost:4000", model="test")
        assert client.check_available() is False
        client.close()


class TestCreateClientFactory:
    def test_create_ollama_client(self):
        client = create_client("ollama", "http://localhost:11434", "qwen3.5:9b")
        assert isinstance(client, OllamaClient)
        assert client.model == "qwen3.5:9b"
        client.close()

    def test_create_openai_client(self):
        client = create_client(
            "openai", "http://localhost:4000", "gpt-4o", api_key="sk-test"
        )
        assert isinstance(client, OpenAIClient)
        assert client.model == "gpt-4o"
        client.close()

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            create_client("unknown", "http://localhost", "model")

    def test_kwargs_forwarded_to_ollama(self):
        client = create_client(
            "ollama", "http://localhost:11434", "test", timeout=60.0
        )
        assert client.timeout == 60.0
        client.close()

    def test_kwargs_forwarded_to_openai(self):
        client = create_client(
            "openai", "http://localhost:4000", "test",
            api_key="sk-test", temperature=0.7,
        )
        assert client._temperature == 0.7
        client.close()
