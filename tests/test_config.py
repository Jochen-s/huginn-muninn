"""Tests for environment-based configuration."""
import os
from pathlib import Path

import pytest


class TestSettings:
    def test_defaults(self):
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.ollama_base_url == "http://localhost:11434"
        assert s.default_model == "qwen3.5:9b"
        assert s.cors_origins == ["*"]
        assert "huginn.db" in str(s.db_path)

    def test_env_override_ollama_url(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.ollama_base_url == "http://ollama:11434"

    def test_env_override_db_path(self, monkeypatch):
        monkeypatch.setenv("HUGINN_DB_PATH", "/data/test.db")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.db_path == Path("/data/test.db")

    def test_env_override_model(self, monkeypatch):
        monkeypatch.setenv("HUGINN_DEFAULT_MODEL", "llama3:8b")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.default_model == "llama3:8b"

    def test_cors_origins_comma_separated(self, monkeypatch):
        monkeypatch.setenv("HUGINN_CORS_ORIGINS", "http://localhost:3000,http://example.com")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.cors_origins == ["http://localhost:3000", "http://example.com"]

    def test_cors_origins_wildcard(self, monkeypatch):
        monkeypatch.setenv("HUGINN_CORS_ORIGINS", "*")
        from huginn_muninn.config import Settings
        s = Settings()
        assert s.cors_origins == ["*"]

    def test_get_settings_singleton(self):
        from huginn_muninn.config import get_settings, _reset_settings
        _reset_settings()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_get_settings_reset(self):
        from huginn_muninn.config import get_settings, _reset_settings
        s1 = get_settings()
        _reset_settings()
        s2 = get_settings()
        assert s1 is not s2
