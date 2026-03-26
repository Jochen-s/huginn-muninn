"""Tests for ModelRegistry."""
from __future__ import annotations

import json

import pytest

from huginn_muninn.llm import OllamaClient, OpenAIClient
from huginn_muninn.model_registry import ModelConfig, ModelRegistry


@pytest.fixture
def models_json(tmp_path):
    """Create a temporary models.json file."""
    config = [
        {
            "name": "local-qwen",
            "provider": "ollama",
            "base_url": "http://localhost:11434",
            "model": "qwen3.5:9b",
        },
        {
            "name": "litellm-claude",
            "provider": "openai",
            "base_url": "http://litellm:4000",
            "model": "claude-sonnet-4-6",
            "api_key": "sk-test",
            "temperature": 0.5,
            "reconcile": True,
        },
    ]
    path = tmp_path / "models.json"
    path.write_text(json.dumps(config))
    return path


class TestModelConfig:
    def test_defaults(self):
        mc = ModelConfig(
            name="test", provider="ollama",
            base_url="http://localhost:11434", model="test:latest",
        )
        assert mc.temperature == 0.3
        assert mc.max_tokens == 4096
        assert mc.reconcile is False
        assert mc.api_key is None


class TestModelRegistry:
    def test_load_from_file(self, models_json):
        reg = ModelRegistry(models_json)
        assert reg.list_names() == ["local-qwen", "litellm-claude"]

    def test_get_existing_model(self, models_json):
        reg = ModelRegistry(models_json)
        m = reg.get("local-qwen")
        assert m is not None
        assert m.provider == "ollama"

    def test_get_missing_model(self, models_json):
        reg = ModelRegistry(models_json)
        assert reg.get("nonexistent") is None

    def test_missing_file_returns_empty(self, tmp_path):
        reg = ModelRegistry(tmp_path / "missing.json")
        assert reg.list_names() == []

    def test_none_path_returns_empty(self):
        reg = ModelRegistry(None)
        assert reg.list_names() == []

    def test_create_ollama_client(self, models_json):
        reg = ModelRegistry(models_json)
        client = reg.create_client("local-qwen")
        assert isinstance(client, OllamaClient)
        client.close()

    def test_create_openai_client(self, models_json):
        reg = ModelRegistry(models_json)
        client = reg.create_client("litellm-claude")
        assert isinstance(client, OpenAIClient)
        assert client._temperature == 0.5
        client.close()

    def test_create_client_unknown_name_raises(self, models_json):
        reg = ModelRegistry(models_json)
        with pytest.raises(KeyError, match="Model not found"):
            reg.create_client("nonexistent")

    def test_get_reconcile_model(self, models_json):
        reg = ModelRegistry(models_json)
        assert reg.get_reconcile_model() == "litellm-claude"

    def test_no_reconcile_model(self, tmp_path):
        config = [{"name": "test", "provider": "ollama",
                    "base_url": "http://localhost:11434", "model": "test"}]
        path = tmp_path / "models.json"
        path.write_text(json.dumps(config))
        reg = ModelRegistry(path)
        assert reg.get_reconcile_model() is None

    def test_invalid_json_returns_empty(self, tmp_path):
        path = tmp_path / "models.json"
        path.write_text("not json")
        reg = ModelRegistry(path)
        assert reg.list_names() == []

    def test_lazy_loading_cached(self, models_json):
        reg = ModelRegistry(models_json)
        # First access loads
        names1 = reg.list_names()
        # Delete file -- cached result should persist
        models_json.unlink()
        names2 = reg.list_names()
        assert names1 == names2
