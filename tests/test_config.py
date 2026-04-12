"""Tests for environment-based configuration."""
import os
from pathlib import Path

import pytest
from huginn_muninn.config import Settings, get_settings, _reset_settings


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


VALID_SUPPRESSIBLE = {
    "communication_posture", "pattern_density_warning",
    "vacuum_filled_by", "prebunking_note",
}


class TestSuppressedFieldsConfig:
    def setup_method(self):
        _reset_settings()

    def teardown_method(self):
        _reset_settings()
        os.environ.pop("HUGINN_SUPPRESS_FIELDS", None)

    def test_default_suppressed_fields_is_empty_tuple(self):
        settings = Settings()
        assert settings.suppressed_fields == ()

    def test_suppressed_fields_parsed_from_env(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by,prebunking_note")
        settings = Settings()
        assert settings.suppressed_fields == ("vacuum_filled_by", "prebunking_note")

    def test_suppressed_fields_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", " vacuum_filled_by , prebunking_note ")
        settings = Settings()
        assert settings.suppressed_fields == ("vacuum_filled_by", "prebunking_note")

    def test_empty_env_var_produces_empty_tuple(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "")
        settings = Settings()
        assert settings.suppressed_fields == ()

    def test_unknown_field_name_raises_at_init(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vaccum_filled_by")
        with pytest.raises(ValueError, match="vaccum_filled_by"):
            Settings()

    def test_overall_confidence_cannot_be_suppressed(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "overall_confidence")
        with pytest.raises(ValueError, match="overall_confidence"):
            Settings()

    def test_singleton_caches_settings(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by")
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_reset_clears_singleton(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by")
        s1 = get_settings()
        _reset_settings()
        monkeypatch.delenv("HUGINN_SUPPRESS_FIELDS")
        s2 = get_settings()
        assert s1 is not s2
        assert s2.suppressed_fields == ()
