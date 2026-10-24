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


class TestKnownSourceTier:
    def test_listed_low_trust_platform_is_known_tier_4(self):
        from huginn_muninn.sources import known_source_tier
        assert known_source_tier("https://t.me/channel/1") == 4
        assert get_source_tier("https://t.me/channel/1") == 4

    def test_unknown_domain_is_none_but_scores_4(self):
        from huginn_muninn.sources import known_source_tier
        assert known_source_tier("https://example-unknown.invalid/x") is None
        assert get_source_tier("https://example-unknown.invalid/x") == 4

    def test_empty_and_garbage_are_none(self):
        from huginn_muninn.sources import known_source_tier
        assert known_source_tier("") is None
        assert known_source_tier("not a url") is None
