"""Tests that docs/confidence-methodology.md and gallery/build.js stay in sync.

Both files render the same scoring methodology in different formats. The
markdown doc is the human-readable source of truth; ``buildMethodologyPage()``
in ``gallery/build.js`` is the HTML view shipped to readers. Drift between
the two is a charter-relevant problem because the live gallery would then
publish a methodology that does not match the documented one.

This module also pins the ECF dimension weights against the canonical
``ConfidenceProfile._WEIGHTS`` mapping in ``src/huginn_muninn/contracts.py``.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "confidence-methodology.md"
JS_PATH = ROOT / "gallery" / "build.js"
CONTRACTS_PATH = ROOT / "src" / "huginn_muninn" / "contracts.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_methodology_js() -> str:
    """Return the body of ``buildMethodologyPage()`` from ``gallery/build.js``.

    We walk the brace depth starting at the opening ``{`` of the function so
    that later string-literal braces in subsequent functions do not bleed
    into our search target.
    """

    source = _read(JS_PATH)
    marker = "function buildMethodologyPage()"
    start = source.find(marker)
    assert start != -1, "buildMethodologyPage() not found in gallery/build.js"

    brace_open = source.find("{", start)
    assert brace_open != -1, "Could not find opening brace of buildMethodologyPage"

    depth = 0
    end = -1
    for i in range(brace_open, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    assert end != -1, "Could not find closing brace of buildMethodologyPage"
    return source[brace_open : end + 1]


@pytest.fixture(scope="module")
def md_text() -> str:
    return _read(MD_PATH)


@pytest.fixture(scope="module")
def js_text() -> str:
    return _extract_methodology_js()


@pytest.fixture(scope="module")
def contracts_text() -> str:
    return _read(CONTRACTS_PATH)


class TestECFWeightsSync:
    """ECF dimension weights must agree across md, JS, and contracts.py."""

    EXPECTED = [
        ("Evidence Quality", "30%", "evidence_quality", 0.30),
        ("Source Reliability", "20%", "source_reliability", 0.20),
        ("Claim Testability", "15%", "claim_testability", 0.15),
        ("Expert Consensus", "20%", "expert_consensus", 0.20),
        ("Internal Coherence", "15%", "internal_coherence", 0.15),
    ]

    def test_md_contains_all_dimension_weight_pairs(self, md_text: str) -> None:
        for label, pct, _key, _val in self.EXPECTED:
            pattern = rf"\|\s*{re.escape(label)}\s*\|\s*{re.escape(pct)}\s*\|"
            assert re.search(pattern, md_text), (
                f"Missing or mis-weighted row in markdown: {label} -> {pct}"
            )

    def test_js_contains_all_dimension_weight_pairs(self, js_text: str) -> None:
        for label, pct, _key, _val in self.EXPECTED:
            pattern = (
                rf"<td>\s*{re.escape(label)}\s*</td>\s*"
                rf"<td>\s*{re.escape(pct)}\s*</td>"
            )
            assert re.search(pattern, js_text), (
                f"Missing or mis-weighted row in build.js: {label} -> {pct}"
            )

    def test_contracts_weights_match_documented_values(
        self, contracts_text: str
    ) -> None:
        weights_start = contracts_text.find("_WEIGHTS")
        assert weights_start != -1, "_WEIGHTS dict not found in contracts.py"
        weights_end = contracts_text.find("}", weights_start)
        weights_block = contracts_text[weights_start : weights_end + 1]
        for _label, _pct, key, val in self.EXPECTED:
            pattern = rf'"{re.escape(key)}"\s*:\s*([0-9]*\.?[0-9]+)'
            match = re.search(pattern, weights_block)
            assert match is not None, (
                f"Expected key '{key}' not found in contracts.py _WEIGHTS dict"
            )
            actual = float(match.group(1))
            assert actual == pytest.approx(val), (
                f"contracts.py weight for '{key}' is {actual}, "
                f"docs claim {val}"
            )


class TestECFLevelsSync:
    """ECF level thresholds must agree between md and JS."""

    EXPECTED_LEVELS = [
        ("HIGH", "0.75 or above"),
        ("MODERATE", "0.50 to 0.74"),
        ("LOW", "0.25 to 0.49"),
        ("VERY LOW", "Below 0.25"),
    ]

    CONTRACTS_LEVELS = ["HIGH", "MODERATE", "LOW", "VERY_LOW"]

    def test_md_lists_all_ecf_levels_with_thresholds(self, md_text: str) -> None:
        for level, threshold in self.EXPECTED_LEVELS:
            pattern = rf"\|\s*{re.escape(level)}\s*\|\s*{re.escape(threshold)}\s*\|"
            assert re.search(pattern, md_text), (
                f"Missing ECF level row in markdown: {level} -> {threshold}"
            )

    def test_js_lists_all_ecf_levels_with_thresholds(self, js_text: str) -> None:
        for level, threshold in self.EXPECTED_LEVELS:
            pattern = (
                rf"<td>\s*{re.escape(level)}\s*</td>\s*"
                rf"<td>\s*{re.escape(threshold)}\s*</td>"
            )
            assert re.search(pattern, js_text), (
                f"Missing ECF level row in build.js: {level} -> {threshold}"
            )

    def test_contracts_encodes_all_ecf_levels(self, contracts_text: str) -> None:
        for level in self.CONTRACTS_LEVELS:
            assert f'"{level}"' in contracts_text, (
                f"contracts.py missing ECF level literal: {level}"
            )


class TestSourceTierSync:
    """Source tier labels and per-tier weight contributions must agree."""

    TIER_LABELS = [
        ("1", "Primary/Institutional"),
        ("2", "Quality Journalism"),
        ("3", "Secondary/Commentary"),
        ("4", "Unverified/Social"),
    ]

    TIER_CONTRIBUTIONS = [
        ("Tier 1", "0.9"),
        ("Tier 2", "0.7"),
        ("Tier 3", "0.5"),
        ("Tier 4", "0.3"),
    ]

    def test_md_contains_all_tier_labels(self, md_text: str) -> None:
        for tier, label in self.TIER_LABELS:
            pattern = rf"\|\s*{re.escape(tier)}\s*\|\s*{re.escape(label)}\s*\|"
            assert re.search(pattern, md_text), (
                f"Missing tier row in markdown: tier {tier} -> {label}"
            )

    def test_js_contains_all_tier_labels(self, js_text: str) -> None:
        for tier, label in self.TIER_LABELS:
            pattern = (
                rf"<td>\s*{re.escape(tier)}\s*</td>\s*"
                rf"<td>\s*{re.escape(label)}\s*</td>"
            )
            assert re.search(pattern, js_text), (
                f"Missing tier row in build.js: tier {tier} -> {label}"
            )

    def test_md_states_tier_weight_contributions(self, md_text: str) -> None:
        for tier, weight in self.TIER_CONTRIBUTIONS:
            pattern = rf"{re.escape(tier)}\s+(?:sources\s+)?contributes?\s+{re.escape(weight)}"
            assert re.search(pattern, md_text), (
                f"Markdown missing tier weight contribution: {tier} -> {weight}"
            )

    def test_js_states_tier_weight_contributions(self, js_text: str) -> None:
        for tier, weight in self.TIER_CONTRIBUTIONS:
            pattern = rf"{re.escape(tier)}\s+(?:sources\s+)?contributes?\s+{re.escape(weight)}"
            assert re.search(pattern, js_text), (
                f"build.js missing tier weight contribution: {tier} -> {weight}"
            )


class TestCNQSSync:
    """CNQS dimensions and the critical-failure rule must agree."""

    CNQS_DIMENSIONS = [
        "Respect for Audience",
        "Acknowledgment of Uncertainty",
        "Proportionality of Response",
        "Institutional Interest Transparency",
        "Alternative Explanation Quality",
        "Factual Accuracy",
        "Tone Calibration",
        "Cognitive Load Management",
    ]

    def test_md_contains_all_cnqs_dimensions(self, md_text: str) -> None:
        missing = [d for d in self.CNQS_DIMENSIONS if d not in md_text]
        assert not missing, f"Markdown missing CNQS dimensions: {missing}"

    def test_js_contains_all_cnqs_dimensions(self, js_text: str) -> None:
        missing = [d for d in self.CNQS_DIMENSIONS if d not in js_text]
        assert not missing, f"build.js missing CNQS dimensions: {missing}"

    def test_md_mentions_critical_failure_rule(self, md_text: str) -> None:
        assert "critical failure" in md_text, (
            "Markdown must describe the score-of-1 critical failure rule"
        )
        assert re.search(r"score of 1", md_text, re.IGNORECASE), (
            "Markdown must describe the score-of-1 critical failure trigger"
        )

    def test_js_mentions_critical_failure_rule(self, js_text: str) -> None:
        assert "critical failure" in js_text, (
            "build.js must describe the score-of-1 critical failure rule"
        )
        assert re.search(r"score of 1", js_text, re.IGNORECASE), (
            "build.js must describe the score-of-1 critical failure trigger"
        )


class TestSyncWarningPresent:
    """Both files must keep their SYNC WARNING comment so future editors notice."""

    def test_md_has_sync_warning(self, md_text: str) -> None:
        assert "SYNC WARNING" in md_text, (
            "docs/confidence-methodology.md must keep the SYNC WARNING comment"
        )
        assert "build.js" in md_text, (
            "Markdown SYNC WARNING must reference gallery/build.js"
        )

    def test_js_has_sync_warning(self) -> None:
        # Reads full file (not js_text fixture) because the warning lives
        # in the preamble above the function, outside the function body.
        source = _read(JS_PATH)
        marker = "function buildMethodologyPage()"
        start = source.find(marker)
        assert start != -1
        preamble = source[max(0, start - 400) : start]
        assert "SYNC WARNING" in preamble, (
            "gallery/build.js must keep the SYNC WARNING comment above "
            "buildMethodologyPage()"
        )
        assert "confidence-methodology.md" in preamble, (
            "build.js SYNC WARNING must reference docs/confidence-methodology.md"
        )
