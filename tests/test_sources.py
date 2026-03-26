"""Tests for source tiering."""
import pytest

from huginn_muninn.sources import get_source_tier, load_disarm_techniques


class TestSourceTier:
    def test_tier1_known_source(self):
        assert get_source_tier("https://who.int/factsheet") == 1

    def test_tier2_news_source(self):
        assert get_source_tier("https://reuters.com/article/test") == 2

    def test_tier4_unknown_source(self):
        assert get_source_tier("https://random-blog-12345.com/post") == 4

    def test_tier4_social_media(self):
        assert get_source_tier("https://twitter.com/user/status/123") == 4

    def test_empty_url_returns_tier4(self):
        assert get_source_tier("") == 4


class TestDisarmTechniques:
    def test_load_techniques(self):
        techniques = load_disarm_techniques()
        assert len(techniques) > 0
        assert any(t["id"] == "T0049" for t in techniques)

    def test_technique_has_required_fields(self):
        techniques = load_disarm_techniques()
        for t in techniques:
            assert "id" in t
            assert "name" in t
            assert "description" in t
