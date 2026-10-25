"""Environment-based configuration for Huginn & Muninn."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_MODEL = "qwen3.5:9b"
MODEL_ENV_VAR = "HUGINN_DEFAULT_MODEL"

_SUPPRESSIBLE_FIELDS = frozenset({
    "communication_posture",
    "pattern_density_warning",
    "vacuum_filled_by",
    "prebunking_note",
    "confidence_profile",
    "cnqs",
})


def _parse_suppress_fields() -> tuple[str, ...]:
    raw = os.environ.get("HUGINN_SUPPRESS_FIELDS", "")
    if not raw.strip():
        return ()
    fields = tuple(f.strip() for f in raw.split(",") if f.strip())
    for f in fields:
        if f not in _SUPPRESSIBLE_FIELDS:
            raise ValueError(
                f"Unknown suppressed field: {f!r}. "
                f"Valid fields: {sorted(_SUPPRESSIBLE_FIELDS)}"
            )
    return fields


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    db_path: Path = field(
        default_factory=lambda: Path(os.environ.get("HUGINN_DB_PATH", str(Path.home() / ".huginn" / "huginn.db")))
    )
    default_model: str = field(
        default_factory=lambda: os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL)
    )
    cors_origins: list[str] = field(default_factory=lambda: _parse_cors())
    webhook_secret: str | None = field(
        default_factory=lambda: os.environ.get("HUGINN_WEBHOOK_SECRET")
    )
    max_jobs: int = field(
        default_factory=lambda: int(os.environ.get("HUGINN_MAX_JOBS", "1000"))
    )
    models_config_path: str | None = field(
        default_factory=lambda: os.environ.get(
            "HUGINN_MODELS_CONFIG",
            str(Path.home() / ".huginn" / "models.json"),
        )
    )
    max_batch_size: int = field(
        default_factory=lambda: int(os.environ.get("HUGINN_MAX_BATCH_SIZE", "50"))
    )
    search_api_key: str | None = field(
        default_factory=lambda: os.environ.get("HUGINN_SEARCH_API_KEY")
    )
    search_provider: str = field(
        default_factory=lambda: os.environ.get("HUGINN_SEARCH_PROVIDER", "brave")
    )
    llm_provider: str = field(
        default_factory=lambda: os.environ.get("HUGINN_LLM_PROVIDER", "ollama")
    )
    llm_api_key: str | None = field(
        default_factory=lambda: os.environ.get("HUGINN_LLM_API_KEY")
    )
    # Reasoning effort for the Claude providers (anthropic, claude-code).
    llm_effort: str | None = field(
        default_factory=lambda: os.environ.get("HUGINN_LLM_EFFORT") or None
    )
    suppressed_fields: tuple[str, ...] = field(
        default_factory=_parse_suppress_fields
    )


# Same-origin by default: the web UI is served by this app, so no cross-origin
# caller needs access unless the operator names one. Was "*" until 2026-09-03.
_DEFAULT_CORS = "http://localhost:8000,http://127.0.0.1:8000"


def _parse_cors() -> list[str]:
    raw = os.environ.get("HUGINN_CORS_ORIGINS", _DEFAULT_CORS)
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def _reset_settings() -> None:
    """Reset singleton (for testing)."""
    global _settings
    _settings = None
