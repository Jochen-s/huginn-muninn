"""Model registry: load model configs from JSON, create LLM clients."""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

from pydantic import BaseModel, Field

from huginn_muninn.llm import LLMClient, create_client

log = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    """Configuration for a single LLM model."""

    name: str
    provider: str
    base_url: str
    model: str
    api_key: str | None = None
    temperature: float = 0.3
    max_tokens: int = 4096
    reconcile: bool = Field(default=False, description="Use as reconciliation model")


class ModelRegistry:
    """Loads model configs from a JSON file. Lazy, cached, tolerant of missing file."""

    def __init__(self, config_path: str | Path | None = None):
        self._config_path = Path(config_path) if config_path else None
        self._models: list[ModelConfig] | None = None
        self._lock = threading.Lock()

    def _load(self) -> list[ModelConfig]:
        with self._lock:
            if self._models is not None:
                return self._models
            if self._config_path is None or not self._config_path.exists():
                self._models = []
                return self._models
            try:
                raw = json.loads(self._config_path.read_text())
                self._models = [ModelConfig(**m) for m in raw]
            except Exception as e:
                log.warning("Failed to load models config from %s: %s", self._config_path, e)
                self._models = []
            return self._models

    def get(self, name: str) -> ModelConfig | None:
        for m in self._load():
            if m.name == name:
                return m
        return None

    def list_names(self) -> list[str]:
        return [m.name for m in self._load()]

    def create_client(self, name: str) -> LLMClient:
        """Create an LLMClient instance for the named model."""
        config = self.get(name)
        if config is None:
            msg = f"Model not found in registry: {name}"
            raise KeyError(msg)
        kwargs: dict = {}
        if config.provider == "openai":
            kwargs["temperature"] = config.temperature
            kwargs["max_tokens"] = config.max_tokens
        return create_client(
            provider=config.provider,
            base_url=config.base_url,
            model=config.model,
            api_key=config.api_key,
            **kwargs,
        )

    def get_reconcile_model(self) -> str | None:
        """Return the name of the model marked for reconciliation, if any."""
        for m in self._load():
            if m.reconcile:
                return m.name
        return None
