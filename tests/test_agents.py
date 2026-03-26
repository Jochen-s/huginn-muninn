"""Tests for Method 2 agents."""
import json
from unittest.mock import MagicMock

import pytest

from huginn_muninn.agents.base import BaseAgent, AgentError
from huginn_muninn.llm import OllamaClient


class ConcreteAgent(BaseAgent):
    """Test-only concrete agent."""
    name = "test_agent"

    def system_prompt(self) -> str:
        return "You are a test agent."

    def build_prompt(self, input_data: dict) -> str:
        return f"Analyze: {input_data['text']}"

    def parse_output(self, raw: dict) -> dict:
        return raw


class TestBaseAgent:
    def test_agent_has_name(self):
        client = MagicMock(spec=OllamaClient)
        agent = ConcreteAgent(client)
        assert agent.name == "test_agent"

    def test_run_calls_llm_and_parses(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = '{"result": "ok"}'
        agent = ConcreteAgent(client)
        result = agent.run({"text": "test"})
        assert result == {"result": "ok"}
        client.generate.assert_called_once()

    def test_run_wraps_errors(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = Exception("timeout")
        agent = ConcreteAgent(client)
        with pytest.raises(AgentError, match="test_agent failed"):
            agent.run({"text": "test"})

    def test_run_handles_invalid_json(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = "This is not JSON at all"
        agent = ConcreteAgent(client)
        with pytest.raises(AgentError, match="test_agent failed"):
            agent.run({"text": "test"})


from huginn_muninn.agents.decomposer import DecomposerAgent
from huginn_muninn.contracts import DecomposerOutput, SubClaimType


MOCK_DECOMPOSER_RESPONSE = json.dumps({
    "sub_claims": [
        {"text": "Immigration has increased", "type": "factual", "verifiable": True},
        {"text": "Crime rates have risen", "type": "factual", "verifiable": True},
        {"text": "Immigration causes crime", "type": "causal", "verifiable": True},
    ],
    "original_claim": "Immigration increases crime rates",
    "complexity": "moderate",
})


class TestDecomposerAgent:
    def test_parse_output_validates_contract(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = json.dumps({"sub_claims": [], "original_claim": "x", "complexity": "simple"})
        agent = DecomposerAgent(client)
        with pytest.raises(AgentError, match="claim_decomposer failed"):
            agent.run({"claim": "test"})  # empty sub_claims violates min_length=1

    def test_decompose_claim(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_DECOMPOSER_RESPONSE
        agent = DecomposerAgent(client)
        result = agent.run({"claim": "Immigration increases crime rates"})
        output = DecomposerOutput(**result)
        assert len(output.sub_claims) == 3
        assert output.complexity == "moderate"
        assert output.sub_claims[2].type == SubClaimType.CAUSAL

    def test_prompt_contains_claim(self):
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "Test claim here"})
        assert "Test claim here" in prompt


from huginn_muninn.agents.tracer import TracerAgent
from huginn_muninn.contracts import TracerOutput


MOCK_TRACER_RESPONSE = json.dumps({
    "origins": [
        {
            "sub_claim": "Immigration has increased",
            "earliest_source": "bls.gov/statistics",
            "earliest_date": "2024-03-01",
            "source_tier": 1,
            "propagation_path": ["bls.gov", "reuters.com", "twitter.com"],
        }
    ],
    "mutations": [
        {
            "original": "Net migration increased by 2%",
            "mutated": "Immigration is out of control",
            "mutation_type": "amplification",
            "source": "twitter.com/influencer",
        }
    ],
})


class TestTracerAgent:
    def test_trace_origins(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_TRACER_RESPONSE
        agent = TracerAgent(client)
        result = agent.run({
            "sub_claims": [{"text": "Immigration has increased", "type": "factual"}],
            "original_claim": "Immigration increases crime",
        })
        output = TracerOutput(**result)
        assert len(output.origins) == 1
        assert output.origins[0].source_tier == 1
        assert len(output.mutations) == 1
        assert output.mutations[0].mutation_type == "amplification"

    def test_prompt_includes_subclaims(self):
        client = MagicMock(spec=OllamaClient)
        agent = TracerAgent(client)
        prompt = agent.build_prompt({
            "sub_claims": [{"text": "X happened", "type": "factual"}],
            "original_claim": "X caused Y",
        })
        assert "X happened" in prompt

    def test_prompt_sanitizes_claim(self):
        client = MagicMock(spec=OllamaClient)
        agent = TracerAgent(client)
        prompt = agent.build_prompt({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "original_claim": "<script>alert('xss')</script>",
        })
        assert "<script>" not in prompt
        assert "&lt;script&gt;" in prompt


from huginn_muninn.agents.mapper import MapperAgent
from huginn_muninn.contracts import MapperOutput


MOCK_MAPPER_RESPONSE = json.dumps({
    "actors": [
        {
            "name": "News Outlet A",
            "type": "media",
            "motivation": "audience capture through outrage",
            "credibility": 0.5,
            "evidence": "Consistently amplifies one-sided framing",
        },
        {
            "name": "Political Group B",
            "type": "organization",
            "motivation": "electoral advantage",
            "credibility": 0.3,
            "evidence": "Funded ad campaigns using the claim",
        },
    ],
    "relations": [
        {
            "source_actor": "Political Group B",
            "target_actor": "News Outlet A",
            "relation_type": "amplifies",
            "confidence": 0.7,
        }
    ],
    "narrative_summary": "The claim is amplified by a media-politics feedback loop.",
})


class TestMapperAgent:
    def test_map_actors(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_MAPPER_RESPONSE
        agent = MapperAgent(client)
        result = agent.run({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "original_claim": "test",
            "origins": {"origins": [], "mutations": []},
        })
        output = MapperOutput(**result)
        assert len(output.actors) == 2
        assert len(output.relations) == 1
        assert output.relations[0].relation_type == "amplifies"

    def test_prompt_includes_origin_data(self):
        client = MagicMock(spec=OllamaClient)
        agent = MapperAgent(client)
        prompt = agent.build_prompt({
            "sub_claims": [{"text": "X", "type": "factual"}],
            "original_claim": "test claim",
            "origins": {"origins": [{"sub_claim": "X", "earliest_source": "twitter.com"}], "mutations": []},
        })
        assert "twitter.com" in prompt


from huginn_muninn.agents.classifier import ClassifierAgent
from huginn_muninn.contracts import ClassifierOutput


MOCK_CLASSIFIER_RESPONSE = json.dumps({
    "ttp_matches": [
        {
            "disarm_id": "T0056",
            "technique_name": "Amplify existing narratives",
            "confidence": 0.85,
            "evidence": "Multiple actors boost organic grievance without adding new facts",
        },
        {
            "disarm_id": "T0023",
            "technique_name": "Distort facts",
            "confidence": 0.7,
            "evidence": "Statistical data reframed without context",
        },
    ],
    "primary_tactic": "Execute",
})


class TestClassifierAgent:
    def test_classify_ttps(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_CLASSIFIER_RESPONSE
        agent = ClassifierAgent(client)
        result = agent.run({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {"origins": [], "mutations": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
        })
        output = ClassifierOutput(**result)
        assert len(output.ttp_matches) == 2
        assert output.ttp_matches[0].disarm_id == "T0056"

    def test_parse_output_rejects_invalid_tactic(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = json.dumps({
            "ttp_matches": [], "primary_tactic": "InvalidTactic",
        })
        agent = ClassifierAgent(client)
        with pytest.raises(AgentError, match="ttp_classifier failed"):
            agent.run({
                "original_claim": "test", "sub_claims": [],
                "origins": {}, "intelligence": {},
            })

    def test_prompt_includes_disarm_reference(self):
        client = MagicMock(spec=OllamaClient)
        agent = ClassifierAgent(client)
        prompt = agent.build_prompt({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {},
            "intelligence": {},
        })
        assert "DISARM" in prompt
        assert "T0049" in prompt


from huginn_muninn.agents.bridge import BridgeAgent
from huginn_muninn.contracts import BridgeOutput


MOCK_BRIDGE_RESPONSE = json.dumps({
    "universal_needs": ["safety", "economic security", "belonging"],
    "issue_overlap": "Both groups cite affordable housing as a top-3 priority (72% overlap in surveys).",
    "narrative_deconstruction": (
        "Actor A framed housing costs as an immigration problem. "
        "Actor B framed the same costs as a corporate investment problem. "
        "Both framings obscure shared concern about housing affordability."
    ),
    "perception_gap": "Each side estimates 60% of opponents want open borders/closed borders; actual rates are 12% and 8%.",
    "moral_foundations": {
        "side_a": ["loyalty", "authority"],
        "side_b": ["care", "fairness"],
    },
    "reframe": "Rather than 'immigration vs natives', this is about 'how do we ensure affordable housing for everyone already here and arriving?'",
    "socratic_dialogue": [
        "If I understand correctly, the concern is that housing costs are rising and that feels threatening to your stability. That's a real and legitimate worry. Is that fair?",
        "One thing I noticed: both groups in this debate cite housing affordability as their top concern. The framing splits them into opposing camps, but the underlying worry is the same. What do you make of that?",
        "Given that most people on both sides actually want the same thing -- affordable, stable housing -- who benefits from making them think they disagree on everything?",
    ],
})


class TestBridgeAgent:
    def test_build_bridge(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_BRIDGE_RESPONSE
        agent = BridgeAgent(client)
        result = agent.run({
            "original_claim": "Immigration drives up housing costs",
            "sub_claims": [],
            "origins": {},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Execute"},
        })
        output = BridgeOutput(**result)
        assert "safety" in output.universal_needs
        assert len(output.socratic_dialogue) == 3

    def test_prompt_references_design_principles(self):
        client = MagicMock(spec=OllamaClient)
        agent = BridgeAgent(client)
        prompt = agent.build_prompt({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {},
            "intelligence": {},
            "ttps": {},
        })
        assert "Socratic" in prompt
        assert "controlling language" in prompt


from huginn_muninn.agents.auditor import AuditorAgent
from huginn_muninn.contracts import AuditorOutput, AuditVerdict


MOCK_AUDITOR_PASS = json.dumps({
    "verdict": "pass",
    "findings": [],
    "confidence_adjustment": 0.0,
    "veto": False,
    "summary": "Analysis is well-supported with diverse sources.",
})

MOCK_AUDITOR_FAIL = json.dumps({
    "verdict": "fail",
    "findings": [
        {
            "category": "bias",
            "severity": "high",
            "description": "All sources are from a single political perspective",
            "recommendation": "Include sources from opposing viewpoints",
        }
    ],
    "confidence_adjustment": -0.3,
    "veto": True,
    "summary": "Critical bias detected -- single-perspective analysis.",
})


class TestAuditorAgent:
    def test_pass_audit(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_AUDITOR_PASS
        agent = AuditorAgent(client)
        result = agent.run({
            "original_claim": "test",
            "decomposition": {},
            "origins": {},
            "intelligence": {},
            "ttps": {},
            "bridge": {},
        })
        output = AuditorOutput(**result)
        assert output.verdict == AuditVerdict.PASS
        assert not output.veto

    def test_fail_audit_with_veto(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_AUDITOR_FAIL
        agent = AuditorAgent(client)
        result = agent.run({
            "original_claim": "test",
            "decomposition": {},
            "origins": {},
            "intelligence": {},
            "ttps": {},
            "bridge": {},
        })
        output = AuditorOutput(**result)
        assert output.verdict == AuditVerdict.FAIL
        assert output.veto
        assert len(output.findings) == 1

    def test_parse_output_rejects_veto_with_pass(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = json.dumps({
            "verdict": "pass", "findings": [], "confidence_adjustment": 0.0,
            "veto": True, "summary": "Contradictory",
        })
        agent = AuditorAgent(client)
        with pytest.raises(AgentError, match="adversarial_auditor failed"):
            agent.run({
                "original_claim": "test", "decomposition": {},
                "origins": {}, "intelligence": {}, "ttps": {}, "bridge": {},
            })

    def test_prompt_checks_all_upstream(self):
        client = MagicMock(spec=OllamaClient)
        agent = AuditorAgent(client)
        prompt = agent.build_prompt({
            "original_claim": "test",
            "decomposition": {"sub_claims": []},
            "origins": {"origins": []},
            "intelligence": {"actors": []},
            "ttps": {"ttp_matches": []},
            "bridge": {"universal_needs": []},
        })
        assert "bias" in prompt.lower()
        assert "veto" in prompt.lower()
