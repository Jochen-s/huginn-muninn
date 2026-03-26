"""Integration tests for the full Method 1 pipeline."""
import json
from unittest.mock import MagicMock, patch

import pytest

from huginn_muninn.llm import OllamaClient
from huginn_muninn.models import VerdictOutput
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt


# Mock LLM response for integration testing without Ollama running
MOCK_PASS1_RESPONSE = json.dumps({
    "evidence_for": [],
    "evidence_against": [
        {
            "text": "Multiple large-scale studies found no link",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/example",
            "source_quality": "high",
        }
    ],
    "unknowns": [],
    "claim_complexity": "simple",
    "polarization_detected": True,
    "groups_involved": ["anti-vaccine advocates", "medical establishment"],
})

MOCK_PASS2_RESPONSE = json.dumps({
    "verdict": "false",
    "confidence": 0.92,
    "evidence_for": [],
    "evidence_against": [
        {
            "text": "Multiple studies found no link",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/example",
            "source_tier": 1,
            "supports_claim": False,
        }
    ],
    "unknowns": [],
    "abstain_reason": None,
    "common_ground": {
        "shared_concern": "Both sides share a deep concern for children's health and safety",
        "framing_technique": "false_dichotomy",
        "technique_explanation": (
            "This debate is often framed as 'pro-vaccine vs anti-vaccine', "
            "hiding the shared goal of keeping children healthy and the legitimate "
            "questions about how best to do that."
        ),
        "reflection": (
            "What if parents on both sides are driven by the same fierce "
            "love for their children, just with different information?"
        ),
    },
    "escalation": {
        "score": 0.35,
        "should_escalate": False,
        "reason": "Well-established scientific consensus",
    },
})


class TestMethodOnePipeline:
    @patch.object(OllamaClient, "generate")
    @patch.object(OllamaClient, "check_available", return_value=True)
    def test_full_pipeline(self, mock_available, mock_generate):
        mock_generate.side_effect = [MOCK_PASS1_RESPONSE, MOCK_PASS2_RESPONSE]

        client = OllamaClient()
        claim = "Vaccines cause autism in children"

        # Pass 1
        p1_prompt = build_pass1_prompt(claim)
        p1_raw = client.generate(p1_prompt)
        p1_data = json.loads(p1_raw)

        # Pass 2
        p2_prompt = build_pass2_prompt(claim, p1_raw)
        p2_raw = client.generate(p2_prompt)
        p2_data = json.loads(p2_raw)

        # Validate output matches schema
        output = VerdictOutput(claim=claim, **p2_data)
        assert output.verdict.value == "false"
        assert output.confidence > 0.8
        assert output.common_ground.shared_concern != ""
        assert output.common_ground.reflection.endswith("?")
        assert output.common_ground.framing_technique == "false_dichotomy"
