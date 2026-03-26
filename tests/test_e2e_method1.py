"""E2E smoke test for Method 1 pipeline against real Ollama."""
import json

import pytest

from huginn_muninn.llm import extract_json_from_response
from huginn_muninn.models import VerdictOutput
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt


@pytest.mark.e2e
class TestMethod1E2E:
    def test_simple_true_claim(self, ollama_client):
        """Water is H2O -- should produce valid JSON through both passes."""
        claim = "Water is composed of hydrogen and oxygen"

        # Pass 1: evidence extraction
        p1_raw = ollama_client.generate(build_pass1_prompt(claim))
        p1_data = extract_json_from_response(p1_raw)
        assert "evidence_for" in p1_data
        assert "evidence_against" in p1_data

        # Pass 2: verdict + common ground
        p2_raw = ollama_client.generate(build_pass2_prompt(claim, json.dumps(p1_data)))
        p2_data = extract_json_from_response(p2_raw)

        # Must validate against the full Pydantic contract
        output = VerdictOutput(claim=claim, **p2_data)
        assert output.verdict.value == "true"
        assert output.confidence >= 0.9
        assert output.common_ground.reflection.endswith("?")

    def test_polarizing_false_claim(self, ollama_client):
        """5G/COVID -- should detect framing technique and produce escalation data."""
        claim = "5G towers spread COVID-19"

        p1_raw = ollama_client.generate(build_pass1_prompt(claim))
        p1_data = extract_json_from_response(p1_raw)

        p2_raw = ollama_client.generate(build_pass2_prompt(claim, json.dumps(p1_data)))
        p2_data = extract_json_from_response(p2_raw)

        output = VerdictOutput(claim=claim, **p2_data)
        assert output.verdict.value == "false"
        assert output.confidence >= 0.85
        assert output.common_ground.framing_technique != "none_detected"
