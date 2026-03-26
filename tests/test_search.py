"""Tests for SearchClient and evidence enrichment."""
from __future__ import annotations

import pytest

from huginn_muninn.search import SearchClient, SearchResult, enrich_evidence


BRAVE_RESPONSE = {
    "web": {
        "results": [
            {
                "url": "https://example.com/article",
                "title": "Test Article",
                "description": "A test result",
                "page_age": "2024-01-15",
            },
            {
                "url": "https://example.com/article2",
                "title": "Test Article 2",
                "description": "Another result",
            },
        ]
    }
}


class TestSearchClient:
    def test_brave_search_returns_results(self, httpx_mock):
        httpx_mock.add_response(
            url="https://api.search.brave.com/res/v1/web/search?q=test+query&count=5",
            json=BRAVE_RESPONSE,
        )
        client = SearchClient(api_key="test-key")
        results = client.search("test query")
        assert len(results) == 2
        assert results[0].url == "https://example.com/article"
        assert results[0].title == "Test Article"
        assert results[0].published_date == "2024-01-15"
        assert results[1].published_date is None
        client.close()

    def test_api_key_in_header(self, httpx_mock):
        httpx_mock.add_response(
            url="https://api.search.brave.com/res/v1/web/search?q=test&count=5",
            json={"web": {"results": []}},
        )
        client = SearchClient(api_key="sk-brave-123")
        client.search("test")
        request = httpx_mock.get_request()
        assert request.headers["x-subscription-token"] == "sk-brave-123"
        client.close()

    def test_unsupported_provider_raises(self):
        client = SearchClient(api_key="test", provider="google")
        with pytest.raises(ValueError, match="Unsupported search provider"):
            client.search("test")
        client.close()

    def test_http_error_propagates(self, httpx_mock):
        httpx_mock.add_response(
            url="https://api.search.brave.com/res/v1/web/search?q=test&count=5",
            status_code=429,
        )
        client = SearchClient(api_key="test")
        with pytest.raises(Exception):
            client.search("test")
        client.close()

    def test_empty_results(self, httpx_mock):
        httpx_mock.add_response(
            url="https://api.search.brave.com/res/v1/web/search?q=test&count=5",
            json={"web": {"results": []}},
        )
        client = SearchClient(api_key="test")
        results = client.search("test")
        assert results == []
        client.close()

    def test_context_manager(self, httpx_mock):
        httpx_mock.add_response(
            url="https://api.search.brave.com/res/v1/web/search?q=test&count=5",
            json={"web": {"results": []}},
        )
        with SearchClient(api_key="test") as client:
            results = client.search("test")
            assert results == []


class TestEnrichEvidence:
    def test_enriches_top_items(self, httpx_mock):
        httpx_mock.add_response(json=BRAVE_RESPONSE)
        httpx_mock.add_response(json=BRAVE_RESPONSE)
        client = SearchClient(api_key="test")
        evidence = [
            {"text": "First claim evidence", "source_url": "http://fake.url"},
            {"text": "Second claim evidence", "source_url": "http://fake2.url"},
        ]
        result = enrich_evidence(evidence, client, max_items=2)
        assert result[0]["source_url"] == "https://example.com/article"
        assert result[0]["publication_date"] == "2024-01-15"
        client.close()

    def test_respects_max_items(self, httpx_mock):
        httpx_mock.add_response(json=BRAVE_RESPONSE)
        client = SearchClient(api_key="test")
        evidence = [
            {"text": "First", "source_url": "http://a.url"},
            {"text": "Second", "source_url": "http://b.url"},
            {"text": "Third", "source_url": "http://c.url"},
        ]
        result = enrich_evidence(evidence, client, max_items=1)
        assert result[0]["source_url"] == "https://example.com/article"
        # Items beyond max_items keep original URL
        assert result[1]["source_url"] == "http://b.url"
        assert result[2]["source_url"] == "http://c.url"
        client.close()

    def test_graceful_on_search_failure(self, httpx_mock):
        httpx_mock.add_response(status_code=500)
        client = SearchClient(api_key="test")
        evidence = [{"text": "Some evidence", "source_url": "http://orig.url"}]
        result = enrich_evidence(evidence, client)
        # Falls back to original
        assert result[0]["source_url"] == "http://orig.url"
        client.close()

    def test_empty_text_skipped(self, httpx_mock):
        client = SearchClient(api_key="test")
        evidence = [{"text": "", "source_url": "http://orig.url"}]
        result = enrich_evidence(evidence, client)
        assert result[0]["source_url"] == "http://orig.url"
        client.close()
