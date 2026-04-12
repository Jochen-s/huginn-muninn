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
    AnalysisResponse,
    _SCOPE_VIOLATION_MARKER,
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


class TestBridgeCommunicationPosture:
    """Sprint 2 PR 3 P2-10: communication_posture on BridgeOutput.

    Scientific grounding: `communication_posture` is orthogonal to numeric
    confidence. Confidence answers "how certain is the analysis?"; posture
    answers "how should the analysis be communicated to someone who
    currently believes a counter-narrative?". The separation is the BG-042
    Confidence-Posture Separation pattern: epistemic certainty must be
    mechanically separable from communicative register.

    The three postures correspond to three well-studied response
    strategies from the misinformation-correction literature:
    - "direct_correction" — classical refutation; appropriate when the
      reader is already open to the correction and the frame is shared.
    - "inoculation_first" — technique-naming prebunk (McGuire 1964,
      van der Linden 2020, Roozenbeek & van der Linden 2022); appropriate
      when the reader is still in the manipulation frame and a direct
      correction would trigger identity defence.
    - "relational_first" — Common Humanity / acknowledgment-first
      (Perry et al. Common Humanity scale; Costello protocol); appropriate
      when identity stakes dominate and the kernel of truth must be
      acknowledged before any correction can land.

    The posture is advisory to downstream consumers. It MUST NOT move
    overall_confidence (that is the invariance contract enforced in
    test_orchestrator.py). This is the reason the field is on BridgeOutput
    and not on AuditorOutput: the Auditor produces confidence;
    the Bridge Builder produces the communicative register."""

    def _minimal_bridge_kwargs(self) -> dict:
        return {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }

    def test_communication_posture_defaults_to_direct_correction(self):
        out = BridgeOutput(**self._minimal_bridge_kwargs())
        assert out.communication_posture == "direct_correction"

    def test_communication_posture_accepts_inoculation_first(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            communication_posture="inoculation_first",
        )
        assert out.communication_posture == "inoculation_first"

    def test_communication_posture_accepts_relational_first(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            communication_posture="relational_first",
        )
        assert out.communication_posture == "relational_first"

    def test_communication_posture_rejects_unknown_literal(self):
        with pytest.raises(ValidationError):
            BridgeOutput(
                **self._minimal_bridge_kwargs(),
                communication_posture="neutral",
            )

    def test_communication_posture_rejects_empty_string(self):
        with pytest.raises(ValidationError):
            BridgeOutput(
                **self._minimal_bridge_kwargs(),
                communication_posture="",
            )

    def test_communication_posture_rejects_none(self):
        with pytest.raises(ValidationError):
            BridgeOutput(
                **self._minimal_bridge_kwargs(),
                communication_posture=None,
            )

    def test_communication_posture_pipe_separated_takes_first(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            communication_posture="inoculation_first|relational_first",
        )
        assert out.communication_posture == "inoculation_first"

    def test_old_format_bridge_dict_still_parses(self):
        """Regression guard: pre-Sprint-2-PR-3 LLM outputs and cached
        analyses must still parse, with posture defaulting to
        direct_correction."""
        old_dict = {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }
        out = BridgeOutput(**old_dict)
        assert out.communication_posture == "direct_correction"


class TestBridgePatternDensityWarning:
    """Sprint 2 PR 3 scoped P2-6: pattern_density_warning on BridgeOutput.

    This field is renamed from the original `apophenia_bait_flag` proposal
    per Holodeck feedback: 'apophenia' pathologises the reader, while
    'pattern density' describes the claim's structural signature. The
    boolean is content-describing, not reader-diagnosing.

    A pattern_density_warning=True output indicates that the claim
    exhibits structural features (repeated numeric coincidences, rhythmic
    lexical choices, escalating concept chaining) that humans are
    predisposed to over-connect. It is a warning to the downstream reader
    that the claim's surface pattern may be exerting extra persuasive
    pull, not a judgement that the reader is pathological.

    Default False so that failure to flag never inflates the signal."""

    def _minimal_bridge_kwargs(self) -> dict:
        return {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }

    def test_pattern_density_warning_defaults_to_false(self):
        out = BridgeOutput(**self._minimal_bridge_kwargs())
        assert out.pattern_density_warning is False

    def test_pattern_density_warning_accepts_true(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            pattern_density_warning=True,
        )
        assert out.pattern_density_warning is True

    def test_old_format_bridge_dict_defaults_pattern_density_false(self):
        old_dict = {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }
        out = BridgeOutput(**old_dict)
        assert out.pattern_density_warning is False


class TestBridgeVacuumFilledByAndPrebunkingNote:
    """Sprint 2 PR 3 scoped P2-6: vacuum_filled_by + prebunking_note.

    Both fields default to empty string so that absent-data never creates
    a spurious positive. The prompt (tested in test_agents.py) constrains
    both fields to narrative patterns only -- never named publishers,
    never named individuals, never named organisations. This is the
    Romulan-grade scope discipline Sprint 2 planned for.

    vacuum_filled_by: a structural description of what narrative pattern
    filled an expertise or information vacuum in the claim's surroundings.
    Example: 'the absence of peer-reviewed primary sources was filled by
    synchronised fake-expert commentary'.

    prebunking_note: a technique warning, not a new factual assertion.
    Example: 'watch for the fabricated-source-mimicry pattern when
    evaluating similar claims'."""

    def _minimal_bridge_kwargs(self) -> dict:
        return {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }

    def test_vacuum_filled_by_defaults_to_empty_string(self):
        out = BridgeOutput(**self._minimal_bridge_kwargs())
        assert out.vacuum_filled_by == ""

    def test_prebunking_note_defaults_to_empty_string(self):
        out = BridgeOutput(**self._minimal_bridge_kwargs())
        assert out.prebunking_note == ""

    def test_vacuum_filled_by_accepts_narrative_pattern_string(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="absence of primary research filled by synchronised expert commentary",
        )
        assert "synchronised" in out.vacuum_filled_by

    def test_prebunking_note_accepts_technique_warning(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note="watch for the fabricated-source-mimicry pattern in similar claims",
        )
        assert "pattern" in out.prebunking_note

    def test_null_vacuum_filled_by_coerced_to_empty(self):
        """BeforeValidator _null_to_empty_str must cover the new field,
        matching the existing Bridge string-field null coercion pattern."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by=None,
        )
        assert out.vacuum_filled_by == ""

    def test_null_prebunking_note_coerced_to_empty(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note=None,
        )
        assert out.prebunking_note == ""

    def test_old_format_bridge_dict_defaults_both_empty(self):
        old_dict = {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }
        out = BridgeOutput(**old_dict)
        assert out.vacuum_filled_by == ""
        assert out.prebunking_note == ""


class TestBridgeScopeScrubber:
    """Sprint 2 PR 3 Codex mitigation (must-fix #1, High severity):
    prompt-level scope discipline on vacuum_filled_by / prebunking_note
    is insufficient enforcement. These tests lock the schema-level
    scrubber at `contracts.py::_scope_scrub_narrative_pattern_fields`.

    The scrubber mirrors SubClaim's "degrade, do not crash" discipline:
    on out-of-scope named-entity content it replaces the field with
    `_SCOPE_VIOLATION_MARKER` rather than raising. The policy guarantee
    (no named publishers) becomes an implementation guarantee that
    cannot be bypassed by a future prompt edit or model swap."""

    def _minimal_bridge_kwargs(self) -> dict:
        return {
            "universal_needs": ["safety"],
            "issue_overlap": "overlap",
            "narrative_deconstruction": "deconstruction",
            "perception_gap": "gap",
            "moral_foundations": {},
            "reframe": "reframe",
            "socratic_dialogue": ["R1"],
        }

    # --- vacuum_filled_by: named-publisher rejections ---

    def test_vacuum_filled_by_scrubs_new_york_times(self):
        """Codex example #1: 'The New York Times filled the expertise
        vacuum around the climate-lab claim' must NOT reach downstream."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="The New York Times filled the expertise vacuum around the climate-lab claim",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER

    def test_vacuum_filled_by_scrubs_bbc_mention(self):
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="the BBC filled the reporting gap",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER

    def test_vacuum_filled_by_scrubs_rt_symmetric(self):
        """Symmetry: blocklist rejects state-aligned outlets too.
        Charter Commitment 3: 'no named publishers' is direction-neutral."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="Russia Today filled the official-denial vacuum",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER

    def test_vacuum_filled_by_scrubs_capitalised_run(self):
        """Three-token Capitalised run catches unknown publishers not
        on the blocklist (e.g., a made-up 'Daily Sentinel Media')."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="Daily Sentinel Media ran the story first",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER

    def test_vacuum_filled_by_scrubs_two_word_with_news_suffix(self):
        """Two-Capitalised-token run with a news-entity suffix."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="London Times ran coverage synchronized with the campaign",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER

    # --- vacuum_filled_by: narrative-pattern strings PRESERVED ---

    def test_vacuum_filled_by_preserves_pattern_description(self):
        """Narrative pattern without named entities must pass through."""
        payload = (
            "absence of peer-reviewed primary sources was filled by "
            "synchronised fake-expert commentary and repeated numeric "
            "coincidences"
        )
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by=payload,
        )
        assert out.vacuum_filled_by == payload

    def test_vacuum_filled_by_preserves_sentence_start_capital(self):
        """Sentence-initial capitalisation must not trigger the scrubber.
        'Absence of primary research...' is narrative-pattern prose."""
        payload = (
            "Absence of primary research created a vacuum later filled "
            "by synchronised anonymous commentary"
        )
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by=payload,
        )
        assert out.vacuum_filled_by == payload

    # --- prebunking_note: named-entity rejections ---

    def test_prebunking_note_scrubs_named_publisher(self):
        """Codex example #2: 'watch for Fox-style laundering' style
        named-outlet content in prebunk warnings."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note="watch for Daily Mail laundering patterns in similar claims",
        )
        assert out.prebunking_note == _SCOPE_VIOLATION_MARKER

    def test_prebunking_note_scrubs_named_person(self):
        """Multi-token proper-noun run should trigger on named individuals."""
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note="watch for John Michael Smith Jr style amplification",
        )
        assert out.prebunking_note == _SCOPE_VIOLATION_MARKER

    def test_prebunking_note_preserves_technique_warning(self):
        """Technique naming with no proper nouns must survive unchanged."""
        payload = (
            "watch for the fabricated-source-mimicry pattern when "
            "evaluating similar claims"
        )
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note=payload,
        )
        assert out.prebunking_note == payload

    def test_prebunking_note_preserves_sentence_start_capital(self):
        payload = (
            "Watch for fabricated-expert commentary and numeric-coincidence "
            "stacking in adjacent narratives"
        )
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            prebunking_note=payload,
        )
        assert out.prebunking_note == payload

    # --- scrubber never crashes pipeline (degrade, do not crash) ---

    def test_scope_scrubber_degrades_does_not_raise(self):
        """A single policy violation must not take down the pipeline.
        Mirrors SubClaim triage downgrade discipline from PR 2."""
        # No exception should be raised; the offending field is scrubbed.
        out = BridgeOutput(
            **self._minimal_bridge_kwargs(),
            vacuum_filled_by="New York Times reporting cycle",
            prebunking_note="watch for Washington Post style pieces",
        )
        assert out.vacuum_filled_by == _SCOPE_VIOLATION_MARKER
        assert out.prebunking_note == _SCOPE_VIOLATION_MARKER
        # The non-scoped fields remain intact.
        assert out.issue_overlap == "overlap"


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


class TestAuditFindingCategoryExpansion:
    """Sprint 3 PR 2: cognitive_warfare and frame_capture are now first-class
    AuditFinding.category literals, replacing the description-prefix workaround."""

    def test_cognitive_warfare_category_accepted(self):
        f = AuditFinding(
            category="cognitive_warfare", severity="high",
            description="GT-001 White Noise pattern detected",
            recommendation="Cross-reference with upstream hypothesis_crowding signal",
        )
        assert f.category == "cognitive_warfare"

    def test_frame_capture_category_accepted(self):
        f = AuditFinding(
            category="frame_capture", severity="medium",
            description="Analysis adopted claim framing without independent restatement",
            recommendation="Restate the question independently before evaluating evidence",
        )
        assert f.category == "frame_capture"

    def test_cognitive_warfare_pipe_separated(self):
        f = AuditFinding(
            category="cognitive_warfare|manipulation", severity="high",
            description="test", recommendation="test",
        )
        assert f.category == "cognitive_warfare"

    def test_frame_capture_pipe_separated(self):
        f = AuditFinding(
            category="frame_capture|quality", severity="medium",
            description="test", recommendation="test",
        )
        assert f.category == "frame_capture"

    def test_original_five_categories_still_accepted(self):
        for cat in ("bias", "accuracy", "completeness", "manipulation", "quality"):
            f = AuditFinding(
                category=cat, severity="low",
                description="test", recommendation="test",
            )
            assert f.category == cat

    def test_unknown_category_rejected(self):
        with pytest.raises(ValidationError):
            AuditFinding(
                category="invented_category", severity="low",
                description="test", recommendation="test",
            )

    def test_cognitive_warfare_in_full_auditor_output(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS_WITH_WARNINGS,
            findings=[
                AuditFinding(
                    category="cognitive_warfare", severity="high",
                    description="GT-003 Pattern Injection signature",
                    recommendation="Verify source independence",
                )
            ],
            confidence_adjustment=-0.1,
            veto=False,
            summary="Cognitive warfare signature detected",
        )
        assert out.findings[0].category == "cognitive_warfare"

    def test_frame_capture_in_full_auditor_output(self):
        out = AuditorOutput(
            verdict=AuditVerdict.PASS_WITH_WARNINGS,
            findings=[
                AuditFinding(
                    category="frame_capture", severity="medium",
                    description="Pipeline adopted claim framing",
                    recommendation="Restate independently",
                )
            ],
            confidence_adjustment=-0.05,
            veto=False,
            summary="Frame capture risk noted",
        )
        assert out.findings[0].category == "frame_capture"


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


class TestAnalysisResponse:
    """Sprint 3 PR 1 C1: AnalysisResponse envelope model."""

    def _make_report_dict(self) -> dict:
        return {
            "claim": "Test claim",
            "decomposition": {
                "sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
                "original_claim": "Test claim",
                "complexity": "simple",
            },
            "origins": {"origins": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["safety"],
                "issue_overlap": "o",
                "narrative_deconstruction": "d",
                "perception_gap": "g",
                "moral_foundations": {},
                "reframe": "r",
                "socratic_dialogue": ["R1"],
                "communication_posture": "inoculation_first",
                "pattern_density_warning": True,
                "vacuum_filled_by": "absence of primary research filled by anonymous commentary",
                "prebunking_note": "watch for fabricated-source-mimicry pattern",
            },
            "audit": {
                "verdict": "pass",
                "findings": [],
                "confidence_adjustment": 0.0,
                "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.72,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

    def test_from_report_unsuppressed_preserves_all_fields(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        assert response.data["bridge"]["communication_posture"] == "inoculation_first"
        assert response.data["bridge"]["vacuum_filled_by"] != ""
        assert response.suppressed_fields == []

    def test_from_report_suppresses_vacuum_filled_by(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(
            report, suppressed=frozenset({"vacuum_filled_by"})
        )
        assert response.data["bridge"]["vacuum_filled_by"] == ""
        assert response.suppressed_fields == ["vacuum_filled_by"]

    def test_from_report_suppresses_multiple_fields(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(
            report,
            suppressed=frozenset({"vacuum_filled_by", "prebunking_note", "pattern_density_warning"}),
        )
        assert response.data["bridge"]["vacuum_filled_by"] == ""
        assert response.data["bridge"]["prebunking_note"] == ""
        assert response.data["bridge"]["pattern_density_warning"] is False
        assert sorted(response.suppressed_fields) == [
            "pattern_density_warning", "prebunking_note", "vacuum_filled_by"
        ]

    def test_suppression_does_not_move_confidence(self):
        report = AnalysisReport(**self._make_report_dict())
        unsup = AnalysisResponse.from_report(report, suppressed=frozenset())
        sup = AnalysisResponse.from_report(
            report, suppressed=frozenset({"vacuum_filled_by", "prebunking_note"})
        )
        assert unsup.data["overall_confidence"] == sup.data["overall_confidence"]

    def test_data_is_strict_subset_of_analysis_report(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        assert set(response.data.keys()).issubset(
            set(AnalysisReport.model_fields.keys())
        )

    def test_bidirectional_completeness(self):
        """Zero-regression constraint #15: every Report field appears in
        data or in the documented exclusion list."""
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        report_keys = set(AnalysisReport.model_fields.keys())
        data_keys = set(response.data.keys())
        missing = report_keys - data_keys
        assert missing == set(), (
            f"AnalysisReport fields missing from AnalysisResponse.data "
            f"without documented exclusion: {missing}"
        )

    def test_envelope_has_suppressed_fields_and_api_version(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        d = response.model_dump(mode="json")
        assert "data" in d
        assert "suppressed_fields" in d
        assert "api_version" in d

    def test_unsuppressed_default_is_backward_compatible(self):
        """With suppressed=frozenset(), AnalysisResponse.data must be
        shape-identical to AnalysisReport.model_dump()."""
        raw = self._make_report_dict()
        report = AnalysisReport(**raw)
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        report_dump = report.model_dump(mode="json")
        assert response.data == report_dump
