"""Tests for knowledge graph actor deduplication."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUILD_GRAPH = ROOT / "graph" / "build_graph.py"


class TestActorDeduplication:
    """Actor name normalization reduces duplicate nodes."""

    def test_normalize_strips_the_prefix(self):
        import sys
        sys.path.insert(0, str(ROOT / "graph"))
        from build_graph import _normalize_actor_name
        assert _normalize_actor_name("The WHO") == "WHO"
        assert _normalize_actor_name("the CDC") == "CDC"

    def test_normalize_strips_whitespace(self):
        import sys
        sys.path.insert(0, str(ROOT / "graph"))
        from build_graph import _normalize_actor_name
        assert _normalize_actor_name("  WHO  ") == "WHO"

    def test_normalize_preserves_non_prefixed(self):
        import sys
        sys.path.insert(0, str(ROOT / "graph"))
        from build_graph import _normalize_actor_name
        assert _normalize_actor_name("World Health Organization") == "World Health Organization"

    def test_build_graph_has_normalize_function(self):
        source = BUILD_GRAPH.read_text(encoding="utf-8")
        assert "def _normalize_actor_name" in source

    def test_build_graph_ecf_attributes(self):
        """Scenario nodes should include ECF attributes."""
        source = BUILD_GRAPH.read_text(encoding="utf-8")
        assert "ecf_level" in source
        assert "ecf_composite" in source


class TestGraphPageRendering:
    """build.js graph page has improved controls."""

    def test_category_filter_in_graph_page(self):
        js = (ROOT / "gallery" / "build.js").read_text(encoding="utf-8")
        assert "category-filter" in js

    def test_graph_builds_without_error(self):
        """Gallery build must succeed with graph improvements."""
        import subprocess
        result = subprocess.run(
            ["node", str(ROOT / "gallery" / "build.js")],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, f"Gallery build failed: {result.stderr}"
