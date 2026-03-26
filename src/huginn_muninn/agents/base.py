"""Base agent with LLM calling, JSON extraction, and error handling."""
from __future__ import annotations

import abc

from huginn_muninn.llm import LLMClient, extract_json_from_response


class AgentError(Exception):
    """Raised when an agent fails to produce valid output."""


class BaseAgent(abc.ABC):
    """Abstract base for all Method 2 agents."""

    name: str = "base"

    def __init__(self, client: LLMClient):
        self.client = client

    @abc.abstractmethod
    def system_prompt(self) -> str:
        """Return the agent's system-level instructions."""

    @abc.abstractmethod
    def build_prompt(self, input_data: dict) -> str:
        """Build the full prompt from input data."""

    @abc.abstractmethod
    def parse_output(self, raw: dict) -> dict:
        """Validate and transform raw LLM output."""

    def run(self, input_data: dict) -> dict:
        """Execute the agent: build prompt -> call LLM -> parse output."""
        try:
            prompt = f"{self.system_prompt()}\n\n{self.build_prompt(input_data)}"
            raw_text = self.client.generate(prompt)
            raw_dict = extract_json_from_response(raw_text)
            return self.parse_output(raw_dict)
        except AgentError:
            raise
        except Exception as e:
            raise AgentError(f"{self.name} failed: {e}") from e
