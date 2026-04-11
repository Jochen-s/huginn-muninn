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


class TestDecomposerVerificationPriorityPrompt:
    """Sprint 2 P2-7: the Decomposer prompt must teach the LLM how to triage.

    These tests are the user-facing surface of the verification_priority
    feature. They are deliberately strict on the two load-bearing pieces:
    (1) the literal set must appear so the LLM cannot invent synonyms; and
    (2) the anti-inflation clause must appear verbatim so the LLM cannot be
    coaxed by emotional loading of the claim into marking everything critical.
    If either of these assertions fails, PR 2's triage discipline is broken."""

    def test_prompt_declares_verification_priority_field(self):
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        assert "verification_priority" in prompt

    def test_prompt_lists_all_three_literal_values(self):
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        assert "critical" in prompt
        assert "high" in prompt
        assert "low" in prompt

    def test_prompt_contains_anti_inflation_clause(self):
        """Load-bearing assertion: the prompt must include the anti-inflation
        clause. Removing it makes every politically-charged claim get marked
        critical, which defeats the triage purpose and inflates downstream
        verification cost.

        Federation #3 strengthening: the OR-conjunction originally used here
        made the test pass if either 'defeats' or 'triage purpose' survived
        in any context; that is too loose for a load-bearing assertion. Both
        must be present for the clause to count as intact."""
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        assert "marking everything" in prompt.lower()
        assert "critical" in prompt.lower()
        assert "defeats" in prompt.lower()
        assert "triage purpose" in prompt.lower()

    def test_prompt_disclaims_evidentiary_and_legal_reading(self):
        """Romulan + Holodeck L-roles mitigation: the prompt must contain
        an explicit epistemic disclaimer that verification_priority is an
        internal triage signal, not an evidentiary or legal classification.
        This prevents downstream readers from interpreting 'critical' as a
        finding of truth, legal liability, or wrongdoing."""
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        lower = prompt.lower()
        assert "internal triage signal" in lower
        assert "not an evidentiary rating" in lower
        assert "not a legal classification" in lower

    def test_prompt_does_not_use_legal_register_triggering_criteria(self):
        """Romulan #2 mitigation: the prompt must not define 'critical' by
        reference to 'legal liability' or 'criminal conduct', because those
        phrases invite defamation exposure and unauthorized-legal-practice
        concerns per the Romulan review. The rework replaces them with
        structural language ('material downstream harm', 'falsifiable
        numeric assertion')."""
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        lower = prompt.lower()
        # Legal-register phrases must be absent as triggering criteria.
        # The disclaimer line may still reference "not a legal classification"
        # and the prompt may contain "legal-register" as a warning, so we
        # assert the TRIGGER phrases "legal liability" and "criminal conduct"
        # are absent.
        assert "legal liability" not in lower, (
            "Prompt must not define 'critical' via 'legal liability' "
            "(Romulan #2 mitigation: defamation exposure)"
        )
        assert "criminal conduct" not in lower, (
            "Prompt must not define 'critical' via 'criminal conduct' "
            "(Romulan #2 mitigation: unauthorised legal classification)"
        )

    def test_prompt_says_default_is_low_when_in_doubt(self):
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        assert "when in doubt" in prompt.lower() or "default" in prompt.lower()

    def test_prompt_warns_against_political_loading_bias(self):
        """Anti-bias discipline carried forward from Sprint 2 PR 1: the prompt
        must explicitly tell the LLM not to mark a sub-claim critical merely
        because its topic is politically charged. This is the Decomposer-level
        mirror of the Gorgon symmetry discipline shipped in PR 1."""
        client = MagicMock(spec=OllamaClient)
        agent = DecomposerAgent(client)
        prompt = agent.build_prompt({"claim": "X"})
        assert "politically charged" in prompt.lower() or "emotionally loaded" in prompt.lower()

    def test_parse_output_accepts_explicit_priority(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = json.dumps({
            "sub_claims": [
                {"text": "X caused N deaths", "type": "factual", "verifiable": True, "verification_priority": "critical"},
                {"text": "X is divisive", "type": "opinion", "verifiable": False, "verification_priority": "low"},
            ],
            "original_claim": "X caused N deaths and X is divisive",
            "complexity": "moderate",
        })
        agent = DecomposerAgent(client)
        result = agent.run({"claim": "Test"})
        output = DecomposerOutput(**result)
        assert output.sub_claims[0].verification_priority == "critical"
        assert output.sub_claims[1].verification_priority == "low"

    def test_parse_output_accepts_legacy_dict_without_priority(self):
        """PR 2 must not regress on pre-Sprint-2 Decomposer outputs."""
        client = MagicMock(spec=OllamaClient)
        client.generate.return_value = MOCK_DECOMPOSER_RESPONSE
        agent = DecomposerAgent(client)
        result = agent.run({"claim": "Immigration increases crime rates"})
        output = DecomposerOutput(**result)
        # Legacy mock does not include verification_priority; all sub-claims
        # must default to "low" via the schema default.
        for sc in output.sub_claims:
            assert sc.verification_priority == "low"


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


class TestBridgePromptPreservation:
    """Sprint 2 PR 3 load-bearing safeguard: the existing
    inferential_gap, narrative_deconstruction, and consensus_explanation
    instructions must survive the P2-11 labeling change unchanged. These
    three instructions were identified in Sprint 2 planning as the load-
    bearing lines at bridge.py:45/49/62. The P2-11 relabeling is allowed
    to ADD context (the reparative Pattern-Injection response label), but
    must NEVER remove or rephrase the underlying instruction."""

    def _build_prompt(self) -> str:
        client = MagicMock(spec=OllamaClient)
        agent = BridgeAgent(client)
        return agent.build_prompt({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {},
            "intelligence": {},
            "ttps": {},
        })

    def test_inferential_gap_kernel_and_leap_structure_preserved(self):
        """The kernel+leap structure is the reparative Pattern-Injection
        response. If a future edit collapses this into a generic
        refutation, PR 3's main repair channel is broken."""
        prompt = self._build_prompt()
        assert "kernel of truth" in prompt
        assert "inferential leap" in prompt
        # The concrete exemplar must remain
        assert "X is documented fact" in prompt
        assert "leap to Y" in prompt

    def test_p211_label_present(self):
        """The P2-11 reparative-Pattern-Injection label must be in the
        prompt near Layer 4 so the intent is legible to future editors."""
        prompt = self._build_prompt()
        assert "REPARATIVE PATTERN-INJECTION RESPONSE" in prompt
        assert "GT-003" in prompt or "Pattern Injection" in prompt

    def test_narrative_deconstruction_instruction_preserved(self):
        prompt = self._build_prompt()
        assert "Narrative Deconstruction" in prompt
        assert "same underlying concern was split" in prompt or "split into opposing narratives" in prompt

    def test_consensus_explanation_instruction_preserved(self):
        """Sprint 2 PR 3 fleet convergence (Federation Minor #3): tighten
        the 'equal depth' assertion to the fuller canonical phrase
        'equal depth and specificity' which appears in the section A
        consensus-explanation instruction at bridge.py:49. Both the
        phrase and its adjacent scientific/mainstream-explanation
        framing must survive any Sprint 2+ prompt expansion."""
        prompt = self._build_prompt()
        assert "scientific consensus" in prompt.lower() or "consensus_explanation" in prompt
        assert "mainstream explanation" in prompt or "scientific or institutional explanation" in prompt
        # The full "equal depth and specificity" phrase is the canonical
        # epistemic commitment (section A, bridge.py:49). It must
        # survive Sprint 2 additions.
        lower = prompt.lower()
        assert "equal depth and specificity" in lower, (
            "Load-bearing consensus_explanation instruction 'equal depth "
            "and specificity' missing from Bridge prompt section A."
        )
        # And the shorter 'equal depth' reference must still appear in
        # the JSON schema body near the consensus_explanation label so
        # the JSON template teaches the same discipline. Use rindex to
        # anchor on the JSON-schema occurrence (the LAST 'consensus_
        # explanation' in the prompt), not the first -- the first may
        # appear in a scope-reminder preamble that lives upstream of
        # the JSON template.
        label_idx = lower.rindex("consensus_explanation")
        window = lower[label_idx : label_idx + 500]
        assert "equal depth" in window, (
            "'equal depth' must appear near the consensus_explanation "
            "JSON-schema label in the Bridge prompt."
        )


class TestBridgeCommunicationPosturePrompt:
    """Sprint 2 PR 3 P2-10: the Bridge prompt must teach the LLM how to
    select a communication posture. These tests enforce that (1) all three
    literal values are present in the prompt, (2) each posture maps to its
    scientific grounding, and (3) the prompt explicitly states the
    orthogonality between posture and confidence (BG-042)."""

    def _build_prompt(self) -> str:
        client = MagicMock(spec=OllamaClient)
        agent = BridgeAgent(client)
        return agent.build_prompt({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {},
            "intelligence": {},
            "ttps": {},
        })

    def test_prompt_lists_all_three_posture_literals(self):
        prompt = self._build_prompt()
        assert "direct_correction" in prompt
        assert "inoculation_first" in prompt
        assert "relational_first" in prompt

    def test_prompt_cites_inoculation_science(self):
        """Scientific grounding for inoculation_first. Without these
        citation anchors, the posture is a black-box hand-wave; with
        them, it is a technique-recognition cue a reader can chase."""
        prompt = self._build_prompt()
        lower = prompt.lower()
        assert "mcguire" in lower
        assert "van der linden" in lower

    def test_prompt_cites_common_humanity_science(self):
        """Scientific grounding for relational_first."""
        prompt = self._build_prompt()
        assert "Common Humanity" in prompt
        assert "Costello" in prompt

    def test_prompt_declares_orthogonality_to_confidence(self):
        """BG-042 discipline: the prompt must explicitly state that
        posture is orthogonal to analytical confidence. If this line
        disappears, future LLMs (and future editors) will conflate the
        two."""
        prompt = self._build_prompt()
        lower = prompt.lower()
        assert "orthogonal" in lower or "orthogonal to overall_confidence" in lower or "separate from" in lower
        # And the explicit anti-conflation instruction:
        assert "not how certain" in lower or "confidence lives in" in lower


class TestBridgeScopedP26Prompt:
    """Sprint 2 PR 3 scoped P2-6: the Bridge prompt must teach the LLM
    the strict scope constraints on vacuum_filled_by and prebunking_note.
    These are the Romulan/Holodeck-grade scope disciplines. Violations
    are defamation-adjacent exposures."""

    def _build_prompt(self) -> str:
        client = MagicMock(spec=OllamaClient)
        agent = BridgeAgent(client)
        return agent.build_prompt({
            "original_claim": "test",
            "sub_claims": [],
            "origins": {},
            "intelligence": {},
            "ttps": {},
        })

    def test_pattern_density_warning_is_content_describing(self):
        """The field must be framed as a CLAIM warning, not a reader
        pathology diagnosis. The 'apophenia' framing is deliberately
        absent (Holodeck feedback)."""
        prompt = self._build_prompt()
        lower = prompt.lower()
        assert "pattern_density_warning" in prompt
        # Must not pathologise the reader
        assert "apophenia" not in lower
        # Must describe the claim, not the reader
        assert "structural" in lower or "structural features" in lower

    def test_vacuum_filled_by_forbids_named_publishers(self):
        """The prompt must explicitly forbid naming publishers,
        individuals, or organisations in vacuum_filled_by."""
        prompt = self._build_prompt()
        # Both forbids must appear so the LLM does not infer a loophole
        assert "vacuum_filled_by" in prompt
        assert "never named publishers" in prompt.lower() or "never name publishers" in prompt.lower() or "not named publishers" in prompt.lower() or "not name publishers" in prompt.lower()
        assert "narrative pattern" in prompt.lower()

    def test_vacuum_filled_by_provides_acceptable_and_unacceptable_examples(self):
        """Concrete exemplars must be in the prompt so the LLM has a
        template to follow, not just a rule to obey."""
        prompt = self._build_prompt()
        assert "Acceptable" in prompt or "acceptable" in prompt
        assert "UNACCEPTABLE" in prompt or "unacceptable" in prompt

    def test_prebunking_note_forbids_new_factual_assertions(self):
        """The field must be a technique-recognition cue, not a new
        factual claim. The Romulan scope discipline.

        Sprint 2 PR 3 fleet convergence (Federation Minor #5, Klingon
        Minor #4): the previous assertion `"not" in lower` was vacuous
        -- "not" appears hundreds of times in any non-trivial English
        prompt. Replaced with an anchored assertion on the canonical
        section I header phrase 'NOT a new factual assertion' which
        lives in bridge.py:95."""
        prompt = self._build_prompt()
        lower = prompt.lower()
        assert "prebunking_note" in prompt
        assert "technique warning" in lower or "technique-recognition" in lower
        # Section I header 'Prebunking Note (technique warning, NOT a
        # new factual assertion)' is the canonical scope phrase. Anchor
        # the assertion on the section header so a future edit that
        # drops or weakens the header trips this test.
        assert "prebunking note" in lower, (
            "Section I header 'Prebunking Note' missing from prompt."
        )
        header_idx = lower.index("prebunking note")
        header_window = lower[header_idx : header_idx + 200]
        assert "not a new factual assertion" in header_window, (
            "The 'NOT a new factual assertion' phrase must appear in the "
            "Prebunking Note section header, mirroring the canonical "
            "Romulan scope-discipline from bridge.py:95."
        )
        # The 'NOT a substitute' clause (prebunking is additive to
        # Inferential Gap Map) must also appear somewhere in the prompt.
        assert "not a substitute" in lower, (
            "'NOT a substitute' clause missing from prompt -- section I "
            "must preserve the additive-not-substitute discipline."
        )
        assert "factual assertion" in lower or "factual claims" in lower

    def test_prebunking_note_is_additive_not_substitute(self):
        """PR 3 load-bearing: prebunking_note must not replace the
        inferential_gap reparative response. The prompt must make this
        explicit so future edits cannot silently promote the prebunking
        note into the primary repair channel."""
        prompt = self._build_prompt()
        lower = prompt.lower()
        assert "additive" in lower or "not a substitute" in lower


class TestBridgePromptTokenBudget:
    """Sprint 2 PR 3 Codex must-fix #5 (Medium severity):
    the Sprint 2 Zero-Regression Constraint #5 is 'Bridge prompt length
    budget: stay below 6,500 input tokens'. PR 3 adds four new sections
    (F/G/H/I) and a ~3,500-word science note is cited inline. Codex
    flagged that the budget was not re-locked after PR 3's expansion.

    This test measures the Bridge prompt at build time against a
    character budget that corresponds to approximately 6,500 tokens
    (conservative 3.6-char-per-token ratio for English prompt text,
    giving ~23,400 chars ceiling). The baseline PR 3 prompt is around
    12,300 chars / ~3,075 tokens so there is ample headroom, but the
    assertion locks the ceiling so a future prompt expansion cannot
    silently drift above 6,500 tokens without this test failing."""

    # Conservative token budget: the zero-regression constraint is
    # 6,500 input tokens. At ~3.6 English chars per token that is
    # ~23,400 characters. We set the hard limit to that value.
    MAX_PROMPT_CHARS = 23_400
    # A softer warning ceiling at 80% of the hard limit for early
    # signal on a prompt expansion that is still within budget but
    # eroding headroom. This is a pure assertion -- no warning API.
    WARN_PROMPT_CHARS = 18_720

    def _build_bridge_prompt(self) -> str:
        client = MagicMock(spec=OllamaClient)
        agent = BridgeAgent(client)
        return agent.build_prompt({
            "original_claim": "A representative claim of typical length for this pipeline",
            "sub_claims": [
                {"text": "Sub-claim A", "type": "factual", "verifiable": True},
                {"text": "Sub-claim B", "type": "causal", "verifiable": True},
            ],
            "origins": [
                {
                    "sub_claim": "Sub-claim A",
                    "earliest_source": "example.org",
                    "earliest_date": "2024-01-01",
                    "source_tier": 2,
                    "propagation_path": ["example.org", "news.example"],
                }
            ],
            "actors": [
                {
                    "name": "Actor One",
                    "type": "media",
                    "motivation": "audience",
                    "credibility": 0.5,
                    "evidence": "sample evidence",
                }
            ],
            "ttp_matches": [
                {
                    "disarm_id": "T0001",
                    "technique_name": "Distortion",
                    "confidence": 0.6,
                    "evidence": "sample",
                }
            ],
            "narrative_summary": "A short narrative summary for budget measurement.",
            "claim": "Test claim",
        })

    def test_bridge_prompt_stays_below_6500_token_budget(self):
        """Hard ceiling: Bridge prompt must not exceed the approximate
        6,500 input-token budget set by Sprint 2 Zero-Regression #5."""
        prompt = self._build_bridge_prompt()
        assert len(prompt) <= self.MAX_PROMPT_CHARS, (
            f"Bridge prompt is {len(prompt)} chars (~{len(prompt) // 4} "
            f"tokens), exceeding the {self.MAX_PROMPT_CHARS}-char ceiling "
            f"(~6,500 tokens). Sprint 2 Zero-Regression Constraint #5 "
            f"requires the Bridge prompt to stay below 6,500 input tokens."
        )

    def test_bridge_prompt_headroom_warning_ceiling(self):
        """Early-warning ceiling at 80% of budget. If this assertion
        fails while the hard ceiling still passes, the next PR should
        re-negotiate the budget explicitly rather than creeping upward.
        Current PR 3 baseline is ~12,300 chars, deep under 18,720."""
        prompt = self._build_bridge_prompt()
        assert len(prompt) <= self.WARN_PROMPT_CHARS, (
            f"Bridge prompt is {len(prompt)} chars, above the "
            f"{self.WARN_PROMPT_CHARS}-char warning ceiling (80% of "
            f"the 6,500-token budget). Headroom is eroding; explicit "
            f"review required before the next prompt expansion."
        )


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

    def test_prompt_includes_gorgon_signals_when_present(self):
        """gorgon_signals (the deterministic hypothesis-expansion dict) must
        reach the LLM prompt. Without this the helper would be dead code."""
        client = MagicMock(spec=OllamaClient)
        agent = AuditorAgent(client)
        prompt = agent.build_prompt({
            "original_claim": "test",
            "decomposition": {"sub_claims": [], "hypothesis_crowding": "high"},
            "origins": {"origins": [], "notable_omissions": ["peer-reviewed primary research"]},
            "intelligence": {"actors": []},
            "ttps": {"ttp_matches": [{"disarm_id": "GT-001", "technique_name": "White Noise", "confidence": 0.8, "evidence": "flood"}]},
            "bridge": {"universal_needs": []},
            "gorgon_signals": {
                "hypothesis_expansion_score": 0.8,
                "hypothesis_crowding": "high",
                "notable_omissions_count": 1,
                "has_gt_ttps": True,
            },
        })
        assert "gorgon_signals" in prompt
        assert "hypothesis_expansion_score" in prompt
        assert "has_gt_ttps" in prompt

    def test_prompt_omits_gorgon_signals_when_absent(self):
        """Backward-compat: callers that don't pass gorgon_signals still work."""
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
        assert "gorgon_signals" not in prompt

    def test_prompt_includes_frame_capture_audit_block(self):
        """The 'DISTINCT from fact-checking' clause must reach the LLM so frame
        capture is not conflated with verification suppression."""
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
        # The phrase may be split across a line break in the f-string;
        # normalize whitespace before asserting.
        normalized = " ".join(prompt.split())
        assert "DISTINCT from fact-checking" in normalized
        assert "frame_capture_risk" in prompt
