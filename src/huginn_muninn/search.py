"""Web search client for evidence enrichment."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

log = logging.getLogger(__name__)


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    published_date: str | None = None


class SearchClient:
    """Client for web search APIs (Brave Search by default)."""

    _BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(
        self,
        api_key: str,
        provider: str = "brave",
        timeout: float = 10.0,
    ):
        self._provider = provider
        self._timeout = timeout
        # Never log the API key
        self._client = httpx.Client(
            timeout=timeout,
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
        )

    def search(self, query: str, count: int = 5) -> list[SearchResult]:
        """Search the web and return results."""
        if self._provider == "brave":
            return self._brave_search(query, count)
        msg = f"Unsupported search provider: {self._provider}"
        raise ValueError(msg)

    def _brave_search(self, query: str, count: int) -> list[SearchResult]:
        resp = self._client.get(
            self._BRAVE_URL,
            params={"q": query, "count": count},
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append(SearchResult(
                url=item.get("url", ""),
                title=item.get("title", ""),
                snippet=item.get("description", ""),
                published_date=item.get("page_age"),
            ))
        return results

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def enrich_evidence(
    evidence_list: list[dict],
    search_client: SearchClient,
    max_items: int = 5,
) -> list[dict]:
    """Replace LLM-guessed URLs with real search results for top evidence items."""
    enriched = []
    for i, ev in enumerate(evidence_list):
        if i < max_items and ev.get("text"):
            try:
                results = search_client.search(ev["text"][:200], count=1)
                if results:
                    best = results[0]
                    ev = dict(ev)
                    ev["source_url"] = best.url
                    if best.published_date:
                        ev["publication_date"] = best.published_date
            except Exception as e:
                log.warning("Search enrichment failed for evidence %d: %s", i, e)
        enriched.append(ev)
    return enriched
