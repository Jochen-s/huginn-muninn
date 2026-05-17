"""Tests for Bridge Builder OARS dialogue structure and sycophancy guard.

Sprint 4 Phase 1: Validates that the Bridge Builder prompt enforces the
OARS validation-first protocol (Round 1 = pure affective validation,
Round 2 = evidence-based examination) and contains sycophancy guards
that prevent claim endorsement in the validation round.

These are PROMPT-LEVEL tests (verify instruction content), not output-level
tests (which require LLM execution). They match the pattern in test_agents.py.
"""
from unittest.mock import MagicMock

import pytest

from huginn_muninn.agents.bridge import BridgeAgent
from huginn_muninn.llm import OllamaClient


BRIDGE_INPUT = {
    "original_claim": "Vaccines cause autism",
    "sub_claims": [{"text": "Vaccines cause autism", "type": "causal", "verifiable": True}],
    "origins": {"origins": []},
    "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
    "ttps": {"ttp_matches": [], "primary_tactic": "Execute"},
}


def _get_bridge_prompt() -> str:
    client = MagicMock(spec=OllamaClient)
    agent = BridgeAgent(client)
    return agent.build_prompt(BRIDGE_INPUT)


def _get_bridge_system_prompt() -> str:
    client = MagicMock(spec=OllamaClient)
    agent = BridgeAgent(client)
    return agent.system_prompt()


class TestOARSPromptStructure:
    """OARS dialogue restructure instructions must appear in the prompt."""

    def test_prompt_contains_oars_protocol_reference(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "oars" in lower or "affective validation" in lower, (
            "Bridge prompt must reference OARS protocol or affective validation"
        )

    def test_prompt_contains_round1_validation_instruction(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "round 1" in lower
        assert any(w in lower for w in ["validation", "emotional", "affective", "listener"]), (
            "Round 1 instructions must reference validation/emotional/affective/listener"
        )

    def test_prompt_instructs_no_evidence_in_round1(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "do not introduce evidence" in lower or "no evidence" in lower or (
            "not introduce evidence" in lower
        ), "Prompt must instruct no evidence in Round 1"

    def test_prompt_contains_permission_bridge(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "permission bridge" in lower or "would it be okay" in lower, (
            "Prompt must reference permission bridge transition to Round 2"
        )

    def test_prompt_contains_round2_evidence_instruction(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "round 2" in lower
        assert "evidence" in lower

    def test_prompt_preserves_three_round_limit(self):
        prompt = _get_bridge_prompt()
        assert "NEVER more than 3 dialogue rounds" in prompt

    def test_prompt_preserves_no_controlling_language(self):
        prompt = _get_bridge_prompt()
        assert "controlling language" in prompt.lower()


class TestSycophancyGuard:
    """Sycophancy guard language must appear in the Bridge prompt."""

    def test_prompt_distinguishes_emotion_validation_from_claim_endorsement(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "emotion" in lower or "feeling" in lower or "emotional experience" in lower
        assert "never the factual claim" in lower or "not the factual claim" in lower or (
            "never validate" in lower and "claim" in lower
        ), "Prompt must distinguish validating emotions from endorsing claims"

    def test_prompt_contains_correct_validation_example(self):
        prompt = _get_bridge_prompt()
        assert "fear for" in prompt.lower() or "worry" in prompt.lower() or (
            "safety" in prompt.lower() and "understand" in prompt.lower()
        )

    def test_prompt_contains_wrong_validation_example(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "catastroph" in lower or "wrong" in lower, (
            "Prompt must show a 'wrong' example of claim endorsement"
        )

    def test_prompt_warns_against_claim_laundering(self):
        """Klingon HIGH #2: prompt must warn against sanitizing absurd claims
        into reasonable-sounding worries during empathic restatement."""
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "launder" in lower or "sanitiz" in lower or (
            "also wrong" in lower
        ), (
            "Prompt must warn against restatement-laundering of claims"
        )

    def test_prompt_does_not_ban_but_or_however_globally(self):
        """The 'no but/however in Round 1' instruction must be scoped to
        Round 1, not the entire response."""
        prompt = _get_bridge_prompt()
        assert "Round 1" in prompt
        lower = prompt.lower()
        assert "but" in lower or "however" in lower, (
            "Prompt should not globally ban 'but'/'however'; only in Round 1"
        )


class TestBridgePromptPreservation:
    """Existing load-bearing instructions must survive the OARS addition."""

    def test_inferential_gap_map_preserved(self):
        prompt = _get_bridge_prompt()
        assert "Inferential Gap Map" in prompt

    def test_load_bearing_label_preserved(self):
        prompt = _get_bridge_prompt()
        assert "REPARATIVE PATTERN-INJECTION RESPONSE" in prompt

    def test_technique_reveal_preserved(self):
        prompt = _get_bridge_prompt()
        assert "Name the Trick" in prompt

    def test_asymmetric_weight_preserved(self):
        prompt = _get_bridge_prompt()
        assert "Asymmetric Weight" in prompt or "Pattern Gravity" in prompt

    def test_communication_posture_preserved(self):
        prompt = _get_bridge_prompt()
        assert "communication_posture" in prompt

    def test_scope_fields_preserved(self):
        prompt = _get_bridge_prompt()
        assert "vacuum_filled_by" in prompt
        assert "prebunking_note" in prompt

    def test_system_prompt_preserves_warmth_and_no_controlling_language(self):
        system = _get_bridge_system_prompt()
        assert "warmth" in system.lower()
        assert "controlling language" in system.lower()


class TestCharterC6Round3:
    """Charter Commitment 6: autonomy-preserving. Round 3 must end with
    a question, not a call to action or solidarity mobilization."""

    def test_prompt_requires_round3_to_end_with_question(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "round 3" in lower
        assert any(phrase in lower for phrase in [
            "end with a question",
            "close with a question",
            "ends with a question",
            "must be a genuine question",
            "must be a question",
            "last sentence is a question",
        ]), "Round 3 instruction must explicitly require ending with a question"

    def test_prompt_bans_solidarity_mobilization_in_round3(self):
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "solidarity mobilization" in lower or (
            "never" in lower and any(p in lower for p in [
                "the most powerful thing",
                "call to action",
                "solidarity",
                "mobiliz",
            ])
        ), "Prompt must ban solidarity mobilization / call-to-action language in Round 3"

    def test_prompt_round3_preserves_integration_function(self):
        """Round 3 still integrates and bridges; C6 only changes the ENDING."""
        prompt = _get_bridge_prompt()
        lower = prompt.lower()
        assert "round 3" in lower
        assert any(w in lower for w in ["integration", "common ground", "shared"]), (
            "Round 3 must still perform integration function"
        )
