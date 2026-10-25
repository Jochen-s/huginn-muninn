"""Local models drift from the requested JSON shape in small ways. One stray
value must not fail a whole agent (rating runs, 2026-10-25: 9b's Origin Tracer
failed on an out-of-list mutation_type; its Bridge Builder once omitted
socratic_dialogue)."""
from huginn_muninn.contracts import BridgeOutput, TracerOutput

ORIGIN = {"sub_claim": "s", "earliest_source": "unknown", "source_tier": 4}


def _mutation(kind):
    return {"original": "o", "mutated": "m", "mutation_type": kind, "source": "x"}


def _bridge(**overrides):
    data = dict(
        universal_needs=["safety"],
        issue_overlap="overlap",
        narrative_deconstruction="deconstruction",
        perception_gap="gap",
        reframe="reframe",
    )
    data.update(overrides)
    return data


class TestMutationTypeDrift:
    def test_capitalised_type_is_normalised(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation("Amplification")])
        assert out.mutations[0].mutation_type == "amplification"

    def test_spaced_type_is_normalised(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation("ideological migration")])
        assert out.mutations[0].mutation_type == "ideological_migration"

    def test_hyphenated_type_is_normalised(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation("Ideological-Migration")])
        assert out.mutations[0].mutation_type == "ideological_migration"

    def test_unknown_type_drops_only_that_mutation(self):
        out = TracerOutput(
            origins=[ORIGIN],
            mutations=[_mutation("exaggeration"), _mutation("distortion")],
        )
        assert [m.mutation_type for m in out.mutations] == ["distortion"]

    def test_null_type_drops_that_mutation(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation(None)])
        assert out.mutations == []

    def test_null_mutations_list_reads_as_empty(self):
        out = TracerOutput(origins=[ORIGIN], mutations=None)
        assert out.mutations == []


class TestSocraticDialogueDrift:
    def test_missing_dialogue_keeps_the_bridge(self):
        assert BridgeOutput(**_bridge()).socratic_dialogue == []

    def test_null_dialogue_keeps_the_bridge(self):
        assert BridgeOutput(**_bridge(socratic_dialogue=None)).socratic_dialogue == []

    def test_dialogue_is_still_capped_at_three(self):
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            BridgeOutput(**_bridge(socratic_dialogue=["1", "2", "3", "4"]))

    def test_agent_parse_accepts_null_dialogue(self):
        from unittest.mock import MagicMock

        from huginn_muninn.agents.bridge import BridgeAgent

        out = BridgeAgent(MagicMock()).parse_output(_bridge(socratic_dialogue=None))
        assert out["socratic_dialogue"] == []


class TestReviewFindings:
    """Independent review of the drift change, 2026-10-25."""

    def test_non_dict_mutation_is_dropped(self):
        out = TracerOutput(origins=[ORIGIN], mutations=["stray text", _mutation("distortion")])
        assert len(out.mutations) == 1

    def test_list_valued_type_is_dropped_not_crashing(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation(["a", "b"])])
        assert out.mutations == []

    def test_drops_are_counted_in_the_output(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation("exaggeration"), _mutation("Distortion")])
        assert out.dropped_mutations == 1

    def test_spaced_hyphen_runs_collapse(self):
        out = TracerOutput(origins=[ORIGIN], mutations=[_mutation("Ideological - Migration")])
        assert out.mutations[0].mutation_type == "ideological_migration"


class TestFrameCaptureDrift:
    def _audit(self, risk):
        from huginn_muninn.contracts import AuditorOutput

        return AuditorOutput(verdict="pass", findings=[], frame_capture_risk=risk, confidence_adjustment=0.0,
                             summary="s")

    def test_low_reads_as_possible(self):
        assert self._audit("low").frame_capture_risk == "possible"

    def test_critical_reads_as_high(self):
        assert self._audit("Critical").frame_capture_risk == "high"

    def test_unrecognised_word_falls_back_to_none(self):
        assert self._audit("perhaps").frame_capture_risk == "none"


class TestMapperTemplateQuoting:
    def test_template_lines_have_balanced_quotes(self):
        from unittest.mock import MagicMock

        from huginn_muninn.agents.mapper import MapperAgent

        prompt = MapperAgent(MagicMock()).build_prompt(
            {"original_claim": "c", "sub_claims": [], "origins": {}})
        template = prompt[prompt.index("{\n"):prompt.index("Guidelines:")]
        for line in template.splitlines():
            assert line.count('"') in (0, 2, 4), line


class TestSourceTierDrift:
    def test_missing_tier_reads_as_four(self):
        out = TracerOutput(origins=[{"sub_claim": "s", "earliest_source": "unknown"}])
        assert out.origins[0].source_tier == 4

    def test_null_tier_reads_as_four(self):
        out = TracerOutput(origins=[{**ORIGIN, "source_tier": None}])
        assert out.origins[0].source_tier == 4
