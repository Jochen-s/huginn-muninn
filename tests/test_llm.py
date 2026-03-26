"""Tests for Ollama LLM client."""
import json

import pytest

from huginn_muninn.llm import OllamaClient, extract_json_from_response


class TestExtractJson:
    def test_clean_json(self):
        raw = '{"verdict": "true", "confidence": 0.9}'
        result = extract_json_from_response(raw)
        assert result["verdict"] == "true"

    def test_json_in_markdown_block(self):
        raw = 'Here is my analysis:\n```json\n{"verdict": "false"}\n```\nDone.'
        result = extract_json_from_response(raw)
        assert result["verdict"] == "false"

    def test_json_with_surrounding_text(self):
        raw = 'Analysis complete. {"verdict": "mixed", "confidence": 0.5} End.'
        result = extract_json_from_response(raw)
        assert result["verdict"] == "mixed"

    def test_no_json_raises(self):
        with pytest.raises(ValueError, match="did not contain valid JSON"):
            extract_json_from_response("No JSON here at all")

    def test_narrative_with_fragment_prefers_largest(self):
        """When LLM emits a small dict before the main response, pick the largest."""
        raw = (
            'The moral foundations are: {"side_a": ["care"], "side_b": ["loyalty"]}.\n'
            'Here is my full analysis:\n'
            '{"universal_needs": ["safety"], "issue_overlap": "both agree", '
            '"narrative_deconstruction": "split", "perception_gap": "gap", '
            '"reframe": "shared", "socratic_dialogue": ["R1"]}'
        )
        result = extract_json_from_response(raw)
        assert "universal_needs" in result
        assert len(result) == 6  # full response, not the 2-key fragment

    def test_clean_json_with_nested_dicts(self):
        """Clean JSON with nested dicts should return the outer object."""
        raw = json.dumps({
            "origins": [{"sub_claim": "X", "source": "y.com", "tier": 1, "date": "2024", "path": []}],
            "mutations": [],
        })
        result = extract_json_from_response(raw)
        assert "origins" in result
        assert "mutations" in result


class TestOllamaClient:
    def test_client_init_defaults(self):
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "qwen3.5:9b"

    def test_client_custom_model(self):
        client = OllamaClient(model="llama3.1:8b")
        assert client.model == "llama3.1:8b"
