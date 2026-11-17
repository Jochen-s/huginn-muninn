"""Tests for ConvergenceMatrix gallery rendering."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUILD_JS = ROOT / "gallery" / "build.js"
FIXTURES = ROOT / "tests" / "fixtures" / "convergence_matrix_samples.json"


class TestConvergenceMatrixFixtures:
    """Fixture data validates against contracts.py model."""

    def test_fixture_file_exists(self):
        assert FIXTURES.exists()

    def test_fixture_validates_against_contracts(self):
        from huginn_muninn.contracts import ConvergenceMatrix
        data = json.loads(FIXTURES.read_text())
        for sid, scenario in data["scenarios"].items():
            cm = ConvergenceMatrix(**scenario)
            assert cm.convergence_type in ("antagonist", "visionary")
            assert cm.convergence_strength in ("LOW", "MEDIUM", "HIGH")
            assert len(cm.groups) >= 1

    def test_hs01_has_three_groups(self):
        data = json.loads(FIXTURES.read_text())
        assert len(data["scenarios"]["HS-01"]["groups"]) == 3

    def test_gp01_is_visionary_type(self):
        data = json.loads(FIXTURES.read_text())
        assert data["scenarios"]["GP-01"]["convergence_type"] == "visionary"


class TestBuildJsHasConvergenceRendering:
    """build.js must contain ConvergenceMatrix rendering code."""

    def test_render_function_exists(self):
        js = BUILD_JS.read_text(encoding="utf-8")
        assert "function renderConvergenceMatrix(" in js

    def test_called_in_scenario_page(self):
        js = BUILD_JS.read_text(encoding="utf-8")
        assert "renderConvergenceMatrix(data)" in js

    def test_handles_missing_matrix_gracefully(self):
        """The function should return empty string for missing data."""
        js = BUILD_JS.read_text(encoding="utf-8")
        assert "if (!cm || !cm.groups || cm.groups.length === 0) return ''" in js


class TestNoSyntheticMatrixInResults:
    """The fixture matrices are synthetic. Sprint 8 (2026-05-14) injected them
    into SC-01, HS-01 and GP-01, and the gallery printed them as analysis.
    SC-01's was removed on 2026-11-13, HS-01's and GP-01's on 2026-11-17."""

    def test_no_result_carries_a_fixture_matrix(self):
        samples = json.loads(FIXTURES.read_text())["scenarios"].values()
        hits = []
        for p in sorted((ROOT / "tests" / "results").glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            cm = (d.get("intelligence") or {}).get("convergence_matrix") if isinstance(d, dict) else None
            if cm and any(cm == s for s in samples):
                hits.append(p.name)
        assert hits == []

    def test_sc01_has_no_stray_matrix(self):
        f = self._latest_file("SC-01")
        if f is None:
            pytest.skip("SC-01 result not in this checkout")
        d = json.loads(f.read_text(encoding="utf-8"))
        assert "convergence_matrix" not in d.get("intelligence", {})

    def _latest_file(self, prefix):
        import re
        results = ROOT / "tests" / "results"
        pat = re.compile(rf"^{re.escape(prefix)}-opus(?:-v(\d+))?\.json$")
        best = None
        best_v = -1
        for p in results.glob(f"{prefix}-*.json"):
            m = pat.match(p.name)
            if not m:
                continue
            v = int(m.group(1)) if m.group(1) else 1
            if v > best_v:
                best_v = v
                best = p
        return best

    def test_pipeline_matrix_still_present(self):
        """Positive control: the matrices the pipeline made (GP-07 to GP-10)
        stay, so the check above has something real to pass over."""
        f = self._latest_file("GP-07")
        if f is None:
            # The public repo ships only SC-01; the full corpus is private.
            pytest.skip("GP-07 result not in this checkout")
        cm = json.loads(f.read_text(encoding="utf-8")).get("intelligence", {}).get("convergence_matrix")
        assert cm and len(cm.get("groups", [])) >= 2
