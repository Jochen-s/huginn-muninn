"""S2 symmetric actor extension plan -- pairwise invariance tests.

Charter Commitment 7 (anti-bias vigilance, operationalised here as
actor-category symmetry) requires that GT-001, GT-002 and GT-003 trigger on
the same structural signatures regardless of which actor category is behind
them. If the pipeline classifies a narrative pattern as White Noise when
the actor is Russian-Federation-aligned, the same pattern must classify
identically when the actor is Five Eyes-aligned, commercial-PR-driven, or
an engineered-grassroots-coordination campaign.

These tests are deterministic and do not call live LLMs. They validate that
the test fixture and the extension-plan research note satisfy the symmetry
discipline that Sprint 1 shipped as a release-gate debt per Romulan R-003.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "gorgon_symmetry_cases.json"
EXTENSION_PLAN_PATH = (
    REPO_ROOT / "research" / "gorgon-trap-symmetric-actor-extension.md"
)

# Actor categories recognised by the symmetric extension plan. The labels
# here are the authoritative set; any fixture scenario that uses an unknown
# label fails the structural-recognition test below.
REQUIRED_ACTOR_CATEGORIES = {
    "five_eyes",
    "russian_federation",
    "pla_ufwd",
    "gulf_state_aligned",
    "iranian",
    "israeli_strategic_communications",
    "commercial_pr",
    "influencer_network",
    "engineered_grassroots_coordination",
    "non_state_media_operation",
}

STATE_ACTOR_CATEGORIES = {
    "five_eyes",
    "russian_federation",
    "pla_ufwd",
    "gulf_state_aligned",
    "iranian",
    "israeli_strategic_communications",
}

NON_STATE_CATEGORIES = {
    "commercial_pr",
    "influencer_network",
    "engineered_grassroots_coordination",
    "non_state_media_operation",
}

# Disjoint-and-complete invariant (Klingon finding): the state and
# non-state sets must be disjoint and together must equal the required
# category set. This prevents a future contributor from laundering a
# state actor into the non-state set without the review being alerted.
assert STATE_ACTOR_CATEGORIES.isdisjoint(NON_STATE_CATEGORIES), (
    "STATE_ACTOR_CATEGORIES and NON_STATE_CATEGORIES must be disjoint"
)
assert STATE_ACTOR_CATEGORIES | NON_STATE_CATEGORIES == REQUIRED_ACTOR_CATEGORIES, (
    "STATE and NON_STATE sets together must equal REQUIRED_ACTOR_CATEGORIES"
)


@pytest.fixture(scope="module")
def fixture_data():
    if not FIXTURE_PATH.exists():
        pytest.fail(f"Fixture file missing: {FIXTURE_PATH}")
    with FIXTURE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class TestGorgonSymmetryFixtureStructure:
    """The fixture must exist and conform to the symmetric-corpus schema."""

    def test_fixture_has_at_least_five_pairs(self, fixture_data):
        pairs = fixture_data.get("pairs", [])
        assert len(pairs) >= 5, (
            f"Expected >= 5 adversarial pairs, got {len(pairs)}. "
            "Sprint 2 plan requires at least 5 pairs for charter compliance."
        )

    def test_each_pair_has_exactly_two_scenarios(self, fixture_data):
        for idx, pair in enumerate(fixture_data.get("pairs", [])):
            scenarios = pair.get("scenarios", [])
            assert len(scenarios) == 2, (
                f"Pair {idx} '{pair.get('pair_id', '?')}': expected 2 "
                f"scenarios, got {len(scenarios)}"
            )

    def test_each_scenario_has_required_fields(self, fixture_data):
        required_fields = {
            "actor_category",
            "expected_ttps",
            "expected_severity_counts",
            "narrative_pattern",
        }
        for idx, pair in enumerate(fixture_data.get("pairs", [])):
            for sc_idx, scenario in enumerate(pair["scenarios"]):
                missing = required_fields - set(scenario.keys())
                assert not missing, (
                    f"Pair {idx} scenario {sc_idx} missing fields: {missing}"
                )

    def test_actor_categories_are_recognised(self, fixture_data):
        unknown = []
        for pair in fixture_data.get("pairs", []):
            for scenario in pair["scenarios"]:
                cat = scenario["actor_category"]
                if cat not in REQUIRED_ACTOR_CATEGORIES:
                    unknown.append(cat)
        assert not unknown, (
            f"Unknown actor categories: {sorted(set(unknown))}. "
            f"Must be one of: {sorted(REQUIRED_ACTOR_CATEGORIES)}"
        )


class TestGorgonSymmetryInvariance:
    """The load-bearing invariance tests: TTP IDs and severity counts must
    match within each pair, regardless of actor category."""

    def test_each_pair_has_identical_expected_ttps(self, fixture_data):
        for idx, pair in enumerate(fixture_data.get("pairs", [])):
            ttps_a = sorted(pair["scenarios"][0]["expected_ttps"])
            ttps_b = sorted(pair["scenarios"][1]["expected_ttps"])
            assert ttps_a == ttps_b, (
                f"Pair {idx} '{pair.get('pair_id', '?')}' TTPs differ: "
                f"{ttps_a} vs {ttps_b}. Symmetric pairs must classify to "
                f"identical TTP sets."
            )

    def test_each_pair_has_identical_severity_counts(self, fixture_data):
        for idx, pair in enumerate(fixture_data.get("pairs", [])):
            sev_a = pair["scenarios"][0]["expected_severity_counts"]
            sev_b = pair["scenarios"][1]["expected_severity_counts"]
            assert sev_a == sev_b, (
                f"Pair {idx} '{pair.get('pair_id', '?')}' severity counts "
                f"differ: {sev_a} vs {sev_b}"
            )

    def test_each_pair_contrasts_different_actor_categories(self, fixture_data):
        for idx, pair in enumerate(fixture_data.get("pairs", [])):
            cat_a = pair["scenarios"][0]["actor_category"]
            cat_b = pair["scenarios"][1]["actor_category"]
            assert cat_a != cat_b, (
                f"Pair {idx} uses the same actor_category on both sides: "
                f"{cat_a}. Symmetric pairs must contrast different categories."
            )


class TestGorgonSymmetryCharterCompliance:
    """Charter Commitment 7: symmetric actor detection. The fixture must
    contain non-state and multiple state actor categories to prevent the
    corpus from implicitly equating 'adversarial' with 'Russia/PLA'."""

    def _collect_categories(self, fixture_data):
        categories = set()
        for pair in fixture_data.get("pairs", []):
            for scenario in pair["scenarios"]:
                categories.add(scenario["actor_category"])
        return categories

    def test_corpus_includes_non_state_categories(self, fixture_data):
        categories = self._collect_categories(fixture_data)
        non_state_present = categories & NON_STATE_CATEGORIES
        assert len(non_state_present) >= 2, (
            f"Corpus must include >= 2 non-state actor categories for "
            f"Charter Commitment 7. Found: {sorted(non_state_present)}. "
            f"All categories: {sorted(categories)}"
        )

    def test_corpus_includes_multiple_state_categories(self, fixture_data):
        categories = self._collect_categories(fixture_data)
        state_present = categories & STATE_ACTOR_CATEGORIES
        assert len(state_present) >= 2, (
            f"Corpus must include >= 2 state-actor categories (not just "
            f"Russia/PLA). Found: {sorted(state_present)}"
        )

    def test_corpus_not_russia_pla_only(self, fixture_data):
        """Explicit blocklist: the corpus must NOT consist exclusively of
        Russian Federation and PLA/UFWD actor categories."""
        categories = self._collect_categories(fixture_data)
        russia_pla_only = {"russian_federation", "pla_ufwd"}
        assert not categories.issubset(russia_pla_only) or not categories, (
            "Corpus uses only Russian Federation / PLA categories -- "
            "Charter Commitment 7 violation."
        )


class TestGorgonSymmetricExtensionPlan:
    """The extension plan research note must exist, enumerate required
    actor categories at category level, state the symmetry principle, and
    fit the word-count window."""

    def test_extension_plan_exists(self):
        assert EXTENSION_PLAN_PATH.exists(), (
            f"Symmetric extension plan missing at {EXTENSION_PLAN_PATH}. "
            "Sprint 2 PR 1 must ship this as a Sprint 1 release-gate debt."
        )

    def test_extension_plan_enumerates_required_categories(self):
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        import re

        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        # Word-bounded markers: Klingon flagged that substring "pla" matches
        # "plan" and "gulf" matches "engulf". Each marker below must match
        # as a whole word (or whole phrase) to count.
        expected_markers = [
            r"\bfive eyes\b",
            r"\brussian federation\b",
            r"\bpla\b",
            r"\bgulf\b",
            r"\biranian\b",
            r"\bisraeli\b",
            r"\bcommercial pr\b",
            r"\binfluencer\b",
            r"\bengineered grassroots\b",
            r"\bnon-state\b",
        ]
        missing = [m for m in expected_markers if not re.search(m, text)]
        assert missing == [], (
            f"Extension plan missing required category markers: {missing}"
        )

    def test_extension_plan_states_symmetry_principle(self):
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        assert "symmetr" in text, (
            "Extension plan must state the symmetry principle explicitly"
        )
        # Charter Commitment 7 is 'Anti-bias vigilance' in the charter text.
        # The extension plan operationalises it as actor-category symmetry.
        # Accept either citation style (direct number or operationalisation
        # phrase) so the test is robust to charter wording tweaks.
        assert (
            "commitment 7" in text
            or "anti-bias vigilance" in text
        ), (
            "Extension plan must reference Charter Commitment 7 "
            "(anti-bias vigilance, operationalised as actor-category symmetry)"
        )

    def test_extension_plan_has_falsification_cases(self):
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        assert "falsification" in text or "falsifying" in text, (
            "Extension plan must include falsification cases per category "
            "(Codex Q6 requirement)"
        )

    def test_extension_plan_word_count_in_range(self):
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8")
        words = len(text.split())
        # Codex specified 1,500-2,500 words. Tightened from a looser 3,500
        # ceiling per Federation finding: gratuitous word budget lets the
        # plan drift into attribution-heavy territory.
        assert 1500 <= words <= 2500, (
            f"Extension plan should be 1,500-2,500 words. "
            f"Got {words} words."
        )

    def test_extension_plan_does_not_name_current_operations(self):
        """Romulan R2-007 precondition: the plan enumerates actor categories
        but must NOT name current operations or specific public attributions.
        This is the 'symmetric without current-operational liability' rule."""
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        # Operation names that would create current-operational attribution.
        # Holodeck Col. Legal L2-007 added Doppelganger and Ghostwriter to
        # the list. The list is not exhaustive but pins known high-profile
        # operation names that would draw attribution risk.
        forbidden_operation_names = [
            "operation ghost stories",
            "operation aurora",
            "operation olympic games",
            "operation newscaster",
            "operation denver",
            "cambridge analytica",
            "doppelganger",
            "ghostwriter",
            "secondary infektion",
        ]
        found = [name for name in forbidden_operation_names if name in text]
        assert found == [], (
            f"Extension plan names current operations (R2-007 violation): "
            f"{found}. Stay at category level."
        )

    def test_extension_plan_has_structural_not_current_operations_disclaimer(self):
        """Romulan R2-007 blocker mitigation: Section 3.1 must explicitly
        state that the category descriptions exist for symmetry testing
        rather than as current operational attributions. This guards against
        future contributors adding attribution in Section 3.1."""
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        assert "symmetry-testing coverage only" in text or (
            "structural labels" in text and "current-operational" in text
        ), (
            "Section 3.1 must explicitly disclaim current-operational "
            "attribution (Romulan R2-007 blocker mitigation)."
        )

    def test_extension_plan_section_4_has_template_disclaimer(self):
        """Holodeck Prof. Evidence Discipline P2-013: Section 4 falsification
        cases are hypothetical templates, not historical attributions. The
        disclaimer must be present so contributors understand the evidence
        status of Section 4 and do not mistake templates for attributions."""
        if not EXTENSION_PLAN_PATH.exists():
            pytest.skip("extension plan missing")
        text = EXTENSION_PLAN_PATH.read_text(encoding="utf-8").lower()
        assert "templates" in text and (
            "not themselves historical attributions" in text
            or "not historical attributions" in text
        ), (
            "Section 4 must include a templates disclaimer (Holodeck P2-013)."
        )
