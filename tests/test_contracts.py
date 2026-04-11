"""Tests for Method 2 inter-agent contracts."""
import pytest
from pydantic import ValidationError

from huginn_muninn.contracts import (
    SubClaim,
    SubClaimType,
    DecomposerOutput,
    OriginEntry,
    NarrativeMutation,
    TracerOutput,
    Actor,
    ActorRelation,
    MapperOutput,
    TTPMatch,
    ClassifierOutput,
    BridgeOutput,
    AuditFinding,
    AuditVerdict,
    AuditorOutput,
    AnalysisInput,
    AnalysisReport,
)


class TestPipeSanitizer:
    """Test that pipe-separated enum values from LLM are handled gracefully."""

    def test_actor_type_pipe_separated(self):
        actor = Actor(
            name="Test", type="influencer|bot_network",
            motivation="test", credibility=0.5,
        )
        assert actor.type == "influencer"

    def test_relation_type_pipe_separated(self):
        rel = ActorRelation(
            source_actor="A", target_actor="B",
            relation_type="funds|coordinates", confidence=0.8,
        )
        assert rel.relation_type == "funds"

    def test_mutation_type_pipe_separated(self):
        mut = NarrativeMutation(
            original="x", mutated="y",
            mutation_type="distortion|amplification", source="z",
        )
        assert mut.mutation_type == "distortion"

    def test_subclaim_type_pipe_separated(self):
        sc = SubClaim(text="test", type="factual|opinion")
        assert sc.type == SubClaimType.FACTUAL

    def test_audit_verdict_pipe_separated(self):
        out = AuditorOutput(
            verdict="pass_with_warnings|fail",
            findings=[], confidence_adjustment=0.0,
            veto=False, summary="test",
        )
        assert out.verdict == AuditVerdict.PASS_WITH_WARNINGS

    def test_clean_values_unaffected(self):
        actor = Actor(
            name="Test", type="media",
            motivation="test", credibility=0.5,
        )
        assert actor.type == "media"


class TestSubClaim:
    def test_valid_subclaim(self):
        sc = SubClaim(text="CO2 levels are rising", type=SubClaimType.FACTUAL)
        assert sc.text == "CO2 levels are rising"
        assert sc.type == SubClaimType.FACTUAL

    def test_empty_text_rejected(self):
        with pytest.raises(ValidationError):
            SubClaim(text="", type=SubClaimType.FACTUAL)


class TestDecomposerOutput:
    def test_valid_output(self):
        out = DecomposerOutput(
            sub_claims=[SubClaim(text="X is true", type=SubClaimType.FACTUAL)],
            original_claim="X is true because Y",
            complexity="simple",
        )
        assert len(out.sub_claims) == 1

    def test_at_least_one_subclaim(self):
        with pytest.raises(ValidationError):
            DecomposerOutput(
                sub_claims=[], original_claim="test", complexity="simple"
            )


class TestTracerOutput:
    def test_valid_output(self):
        out = TracerOutput(
            origins=[
                OriginEntry(
                    sub_claim="X", earliest_source="twitter.com/user",
                    earliest_date="2024-01-15", source_tier=4,
                )
            ],
            mutations=[],
        )
        assert out.origins[0].source_tier == 4

    def test_source_tier_out_of_bounds(self):
        with pytest.raises(ValidationError):
            OriginEntry(sub_claim="X", earliest_source="y.com", source_tier=5)


class TestMapperOutput:
    def test_valid_output(self):
        out = MapperOutput(
            actors=[
                Actor(
                    name="News Outlet A", type="media",
                    motivation="audience capture",
                    credibility=0.6,
                )
            ],
            relations=[],
            narrative_summary="A single narrative about X",
        )
        assert out.actors[0].credibility == 0.6

    def test_credibility_bounds(self):
        with pytest.raises(ValidationError):
            Actor(name="X", type="media", motivation="Y", credibility=1.5)


class TestClassifierOutput:
    def test_valid_output(self):
        out = ClassifierOutput(
            ttp_matches=[
                TTPMatch(
                    disarm_id="T0049",
                    technique_name="Flood the information space",
                    confidence=0.8,
                    evidence="High volume of posts in 24h window",
                )
            ],
            primary_tactic="Execute",
        )
        assert out.ttp_matches[0].disarm_id == "T0049"

    def test_primary_tactic_must_be_valid_literal(self):
        with pytest.raises(ValidationError):
            ClassifierOutput(ttp_matches=[], primary_tactic="InvalidTactic")


class TestBridgeOutput:
    def test_valid_output(self):
        out = BridgeOutput(
            universal_needs=["safety", "economic security"],
            issue_overlap="Both groups cite healthcare access as top priority",
            narrative_deconstruction="Actor A framed X as immigration; Actor B framed X as corporate greed",
            perception_gap="Supporters estimate 55% of opponents want X; actual rate is 18%",
            moral_foundations={"side_a": ["care", "fairness"], "side_b": ["loyalty", "authority"]},
            reframe="Rather than Group A vs Group B, this is about ensuring X for everyone",
            socratic_dialogue=[
                "If I understand correctly, the concern is...",
                "One thing I noticed about that evidence...",
                "There are actually several groups with different views...",
            ],
        )
        assert len(out.socratic_dialogue) == 3

    def test_max_three_dialogue_rounds(self):
        with pytest.raises(ValidationError):
            BridgeOutput(
                universal_needs=["safety"],
                issue_overlap="overlap",
                narrative_deconstruction="deconstruction",
                perception_gap="gap",
                moral_foundations={},
                reframe="reframe",
                socratic_dialogue=["1", "2", "3", "4"],
            )

    def test_null_perception_gap_coerced_to_empty(self):
        out = BridgeOutput(
            universal_needs=["safety"],
            issue_overlap="overlap",
            narrative_deconstruction="deconstruction",
            perception_gap=None,
            moral_foundations={},
            reframe="reframe",
            socratic_dialogue=["R1"],
        )
        assert out.perception_gap == ""

    def test_empty_universal_needs_rejected(self):
        with pytest.raises(ValidationError):
            BridgeOutput(
                universal_needs=[],
                issue_overlap="overlap",
                narrative_deconstruction="deconstruction",
                perception_gap="gap",
                moral_foundations={},
                reframe="reframe",
                socratic_dialogue=["R1"],
            )


class TestAuditorOutput:
    def test_pass_verdict(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS,
            findings=[],
            confidence_adjustment=0.0,
            veto=False,
            summary="Analysis is well-supported",
        )
        assert not out.veto

    def test_veto_verdict(self):
        out = AuditorOutput(
            verdict=AuditVerdict.FAIL,
            findings=[
                AuditFinding(
                    category="bias", severity="high",
                    description="Western-centric framing",
                    recommendation="Add non-Western sources",
                )
            ],
            confidence_adjustment=-0.2,
            veto=True,
            summary="Critical bias detected",
        )
        assert out.veto

    def test_confidence_adjustment_out_of_bounds(self):
        with pytest.raises(ValidationError):
            AuditorOutput(
                verdict=AuditVerdict.PASS, findings=[], confidence_adjustment=-1.5,
                veto=False, summary="Test",
            )

    def test_veto_with_pass_rejected(self):
        with pytest.raises(ValidationError, match="inconsistent"):
            AuditorOutput(
                verdict=AuditVerdict.PASS, findings=[], confidence_adjustment=0.0,
                veto=True, summary="Contradictory",
            )

    def test_veto_with_pass_with_warnings_allowed(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS_WITH_WARNINGS,
            findings=[
                AuditFinding(
                    category="quality", severity="high",
                    description="Weak sourcing", recommendation="Add sources",
                )
            ],
            confidence_adjustment=-0.1,
            veto=True,
            summary="Severe quality issue warrants veto",
        )
        assert out.veto


class TestGorgonFieldDefaults:
    """Regression guards for the cognitive-warfare taxonomy fields: every new
    field must have a safe default so older LLM outputs, fallback dicts, and
    cached JSON still parse at the AnalysisReport validation boundary."""

    def test_decomposer_hypothesis_crowding_defaults_to_low(self):
        out = DecomposerOutput(
            sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
            original_claim="X",
            complexity="simple",
        )
        assert out.hypothesis_crowding == "low"

    def test_decomposer_manipulation_vector_density_defaults_to_zero(self):
        out = DecomposerOutput(
            sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
            original_claim="X",
            complexity="simple",
        )
        assert out.manipulation_vector_density == 0.0

    def test_decomposer_complexity_explosion_flag_defaults_false(self):
        out = DecomposerOutput(
            sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
            original_claim="X",
            complexity="simple",
        )
        assert out.complexity_explosion_flag is False

    def test_decomposer_accepts_explicit_high_crowding(self):
        out = DecomposerOutput(
            sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
            original_claim="X",
            complexity="complex",
            hypothesis_crowding="high",
            manipulation_vector_density=0.6,
            complexity_explosion_flag=True,
        )
        assert out.hypothesis_crowding == "high"
        assert out.manipulation_vector_density == 0.6
        assert out.complexity_explosion_flag is True

    def test_decomposer_manipulation_vector_density_bounds(self):
        with pytest.raises(ValidationError):
            DecomposerOutput(
                sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
                original_claim="X",
                complexity="simple",
                manipulation_vector_density=1.5,
            )

    def test_old_format_decomposer_dict_still_parses(self):
        """Regression guard: pre-Gorgon LLM outputs must still parse."""
        old_dict = {
            "sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
            "original_claim": "X",
            "complexity": "simple",
        }
        out = DecomposerOutput(**old_dict)
        assert out.hypothesis_crowding == "low"
        assert out.manipulation_vector_density == 0.0
        assert out.complexity_explosion_flag is False

    def test_mutation_relay_type_defaults_to_ambiguous(self):
        mut = NarrativeMutation(
            original="a", mutated="b",
            mutation_type="distortion", source="s",
        )
        assert mut.relay_type == "ambiguous"

    def test_mutation_relay_type_pipe_separated(self):
        mut = NarrativeMutation(
            original="a", mutated="b",
            mutation_type="distortion", source="s",
            relay_type="knowing|unknowing",
        )
        assert mut.relay_type == "knowing"

    def test_tracer_notable_omissions_defaults_empty(self):
        out = TracerOutput(origins=[])
        assert out.notable_omissions == []

    def test_tracer_notable_omissions_accepts_up_to_three(self):
        out = TracerOutput(
            origins=[],
            notable_omissions=["peer-reviewed primary research", "contemporaneous news", "official statements"],
        )
        assert len(out.notable_omissions) == 3

    def test_tracer_notable_omissions_rejects_more_than_three(self):
        with pytest.raises(ValidationError):
            TracerOutput(
                origins=[],
                notable_omissions=["a", "b", "c", "d"],
            )

    def test_old_format_tracer_dict_still_parses(self):
        """Regression guard: pre-Gorgon Tracer fallback must still parse."""
        old_dict = {"origins": [], "mutations": []}
        out = TracerOutput(**old_dict)
        assert out.notable_omissions == []

    def test_auditor_frame_capture_risk_defaults_to_none(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS,
            findings=[],
            confidence_adjustment=0.0,
            veto=False,
            summary="ok",
        )
        assert out.frame_capture_risk == "none"
        assert out.frame_capture_evidence == ""

    def test_auditor_frame_capture_risk_accepts_high(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS_WITH_WARNINGS,
            findings=[],
            confidence_adjustment=-0.1,
            veto=False,
            summary="imported causal chain without restatement",
            frame_capture_risk="high",
            frame_capture_evidence="Decomposer adopted the claim's 'X causes Y' label without restatement",
        )
        assert out.frame_capture_risk == "high"

    def test_old_format_auditor_dict_still_parses(self):
        """Regression guard: pre-Gorgon Auditor fallback must still parse."""
        old_dict = {
            "verdict": "pass_with_warnings",
            "findings": [],
            "confidence_adjustment": -0.1,
            "veto": False,
            "summary": "ok",
        }
        out = AuditorOutput(**old_dict)
        assert out.frame_capture_risk == "none"
        assert out.frame_capture_evidence == ""


class TestSubClaimVerificationPriority:
    """Sprint 2 P2-7: triage priority on sub-claims. Every new field must
    (1) default to a safe value so older LLM outputs still parse,
    (2) validate the literal set strictly,
    (3) survive orchestrator fallback, and
    (4) never regress Sprint 1's backwards-compat guarantee.

    The priority is explicitly 'low' by default -- not 'high' or 'critical' --
    so that failing to triage never inflates verification debt. The anti-
    inflation clause lives in the Decomposer prompt (see test_agents.py);
    this contract-level test only enforces the literal discipline and the
    default-safety discipline."""

    def test_verification_priority_defaults_to_low(self):
        sc = SubClaim(text="CO2 levels are rising", type=SubClaimType.FACTUAL)
        assert sc.verification_priority == "low"

    def test_verification_priority_accepts_critical(self):
        sc = SubClaim(
            text="X caused the deaths of N people",
            type=SubClaimType.FACTUAL,
            verification_priority="critical",
        )
        assert sc.verification_priority == "critical"

    def test_verification_priority_accepts_high(self):
        sc = SubClaim(
            text="Policy Y will raise costs by Z percent",
            type=SubClaimType.FACTUAL,
            verification_priority="high",
        )
        assert sc.verification_priority == "high"

    def test_verification_priority_accepts_low(self):
        sc = SubClaim(
            text="Commentator A said B",
            type=SubClaimType.OPINION,
            verification_priority="low",
        )
        assert sc.verification_priority == "low"

    def test_verification_priority_rejects_unknown_literal(self):
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority="urgent",  # not in the literal set
            )

    def test_verification_priority_rejects_empty_string(self):
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority="",
            )

    def test_verification_priority_rejects_trailing_space(self):
        """Codex PR 2 Q2 drift matrix: 'critical ' with a trailing space is
        an observed LLM drift pattern. The literal gate must reject it
        rather than silently parse it as critical."""
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority="critical ",
            )

    def test_verification_priority_rejects_punctuation(self):
        """Codex PR 2 Q2 drift matrix: 'Critical!' with punctuation is an
        observed LLM drift pattern, especially for urgency-coded outputs."""
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority="Critical!",
            )

    def test_verification_priority_rejects_capitalized_uppercase(self):
        """Codex PR 2 Q2 drift matrix: 'URGENT' / 'Critical' / 'HIGH' are
        observed LLM drift patterns. The Literal set is case-sensitive."""
        for variant in ["URGENT", "Critical", "HIGH", "LOW"]:
            with pytest.raises(ValidationError):
                SubClaim(
                    text="X",
                    type=SubClaimType.FACTUAL,
                    verification_priority=variant,
                )

    def test_verification_priority_rejects_none(self):
        """Codex PR 2 Q2 drift matrix: explicit None (not 'missing key')
        must be rejected. Missing key is handled by the default; None is an
        affirmative invalid value."""
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority=None,
            )

    def test_verification_priority_rejects_comma_separated(self):
        """Codex PR 2 Q2 drift matrix: 'critical, high' is an observed LLM
        drift pattern distinct from the pipe-separated form that
        _first_pipe_value handles. Comma-separated must be rejected."""
        with pytest.raises(ValidationError):
            SubClaim(
                text="X",
                type=SubClaimType.FACTUAL,
                verification_priority="critical, high",
            )

    def test_incoherent_unverifiable_critical_downgrades_to_high(self):
        """Holodeck I-roles mitigation: verifiable=False combined with
        verification_priority='critical' is incoherent (nothing to verify,
        yet marked as a critical verification target). The schema-level
        validator must downgrade rather than raise, because a single
        incoherent Decomposer output must not take down the whole pipeline
        (mirrors Sprint 1 'degrade, do not crash' discipline)."""
        sc = SubClaim(
            text="This is an opinion",
            type=SubClaimType.OPINION,
            verifiable=False,
            verification_priority="critical",
        )
        # Downgraded to "high" by the model_validator, not to "low".
        # "low" would over-correct and suppress the signal entirely.
        assert sc.verification_priority == "high"

    def test_verifiable_false_with_low_priority_preserved(self):
        """Regression guard for the cross-field validator: the degrade
        path must only fire when verifiable=False AND priority=critical.
        Every other combination must be untouched."""
        sc = SubClaim(
            text="opinion",
            type=SubClaimType.OPINION,
            verifiable=False,
            verification_priority="low",
        )
        assert sc.verification_priority == "low"

    def test_verifiable_false_with_high_priority_preserved(self):
        sc = SubClaim(
            text="opinion",
            type=SubClaimType.OPINION,
            verifiable=False,
            verification_priority="high",
        )
        assert sc.verification_priority == "high"

    def test_verifiable_true_with_critical_priority_preserved(self):
        sc = SubClaim(
            text="X caused N deaths",
            type=SubClaimType.FACTUAL,
            verifiable=True,
            verification_priority="critical",
        )
        assert sc.verification_priority == "critical"

    def test_verification_priority_pipe_separated_takes_first(self):
        """LLMs occasionally emit 'critical|high' style values; the existing
        _first_pipe_value validator must cover this new field as well."""
        sc = SubClaim(
            text="X",
            type=SubClaimType.FACTUAL,
            verification_priority="critical|high",
        )
        assert sc.verification_priority == "critical"

    def test_old_format_subclaim_dict_still_parses(self):
        """Regression guard: pre-PR-2 LLM outputs (no verification_priority
        key) must still parse to a SubClaim with the low default. This is the
        Sprint 1 backwards-compat discipline carried forward."""
        old_dict = {"text": "X", "type": "factual", "verifiable": True}
        sc = SubClaim(**old_dict)
        assert sc.verification_priority == "low"

    def test_decomposer_output_round_trips_verification_priority(self):
        """End-to-end contract exercise: a DecomposerOutput constructed from
        a dict containing sub-claims with verification_priority keys must
        round-trip through model_dump() without losing the field."""
        out = DecomposerOutput(
            sub_claims=[
                SubClaim(
                    text="Claim A",
                    type=SubClaimType.FACTUAL,
                    verification_priority="critical",
                ),
                SubClaim(
                    text="Claim B",
                    type=SubClaimType.OPINION,
                    verification_priority="low",
                ),
            ],
            original_claim="Claim A and Claim B",
            complexity="moderate",
        )
        dumped = out.model_dump()
        assert dumped["sub_claims"][0]["verification_priority"] == "critical"
        assert dumped["sub_claims"][1]["verification_priority"] == "low"

    def test_analysis_report_validates_with_verification_priority(self):
        """The production-boundary validator at orchestrator.py must accept
        an AnalysisReport whose Decomposer sub-claims carry explicit priority
        values. Regression guard for blind spot #2 (validation marker)."""
        report = AnalysisReport(
            claim="Test",
            decomposition=DecomposerOutput(
                sub_claims=[
                    SubClaim(
                        text="X",
                        type=SubClaimType.FACTUAL,
                        verification_priority="high",
                    ),
                ],
                original_claim="Test",
                complexity="simple",
            ),
            origins=TracerOutput(origins=[]),
            intelligence=MapperOutput(actors=[], relations=[], narrative_summary=""),
            ttps=ClassifierOutput(ttp_matches=[], primary_tactic="Execute"),
            bridge=BridgeOutput(
                universal_needs=["safety"],
                issue_overlap="",
                narrative_deconstruction="",
                perception_gap="",
                moral_foundations={},
                reframe="",
                socratic_dialogue=["R1"],
            ),
            audit=AuditorOutput(
                verdict=AuditVerdict.PASS,
                findings=[],
                confidence_adjustment=0.0,
                veto=False,
                summary="",
            ),
            overall_confidence=0.7,
        )
        assert report.decomposition.sub_claims[0].verification_priority == "high"


class TestAnalysisInput:
    def test_valid_input(self):
        inp = AnalysisInput(claim="Test claim", context=None, language="en")
        assert inp.claim == "Test claim"

    def test_empty_claim_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisInput(claim="", context=None, language="en")


class TestAnalysisReport:
    def test_valid_report(self):
        report = AnalysisReport(
            claim="Test claim",
            decomposition=DecomposerOutput(
                sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
                original_claim="Test claim",
                complexity="simple",
            ),
            origins=TracerOutput(origins=[]),
            intelligence=MapperOutput(actors=[], relations=[], narrative_summary="N/A"),
            ttps=ClassifierOutput(ttp_matches=[], primary_tactic="Execute"),
            bridge=BridgeOutput(
                universal_needs=["safety"],
                issue_overlap="overlap",
                narrative_deconstruction="deconstruction",
                perception_gap="gap",
                moral_foundations={},
                reframe="reframe",
                socratic_dialogue=["Round 1"],
            ),
            audit=AuditorOutput(
                verdict=AuditVerdict.PASS,
                findings=[],
                confidence_adjustment=0.0,
                veto=False,
                summary="Good",
            ),
            overall_confidence=0.75,
        )
        assert report.method == "method_2"
        assert not report.degraded

    def test_confidence_bounds(self):
        """overall_confidence must be 0.0-1.0."""
        with pytest.raises(ValidationError):
            AnalysisReport(
                claim="X",
                decomposition=DecomposerOutput(
                    sub_claims=[SubClaim(text="X", type=SubClaimType.FACTUAL)],
                    original_claim="X", complexity="simple",
                ),
                origins=TracerOutput(origins=[]),
                intelligence=MapperOutput(actors=[], relations=[], narrative_summary=""),
                ttps=ClassifierOutput(ttp_matches=[], primary_tactic="Execute"),
                bridge=BridgeOutput(
                    universal_needs=["safety"], issue_overlap="", narrative_deconstruction="",
                    perception_gap="", moral_foundations={}, reframe="",
                    socratic_dialogue=["R1"],
                ),
                audit=AuditorOutput(
                    verdict=AuditVerdict.PASS, findings=[], confidence_adjustment=0.0,
                    veto=False, summary="",
                ),
                overall_confidence=1.5,  # Out of bounds!
            )
