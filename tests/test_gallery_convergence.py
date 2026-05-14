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


class TestScenarioJsonsHaveFixtureData:
    """Injected scenarios should have convergence_matrix in intelligence."""

    SCENARIOS = ["HS-01", "GP-01", "SC-01"]

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

    def test_injected_scenarios_have_convergence_matrix(self):
        for sid in self.SCENARIOS:
            f = self._latest_file(sid)
            assert f is not None, f"No result file for {sid}"
            d = json.loads(f.read_text())
            cm = d.get("intelligence", {}).get("convergence_matrix")
            assert cm is not None, f"{sid} missing convergence_matrix in intelligence"
            assert len(cm.get("groups", [])) >= 1, f"{sid} has no groups"
