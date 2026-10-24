"""Source tiering and DISARM technique reference."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Known source domains by tier (seed data -- not exhaustive)
_TIER_DOMAINS: dict[int, set[str]] = {
    1: {
        "who.int", "cdc.gov", "nih.gov", "nature.com", "science.org",
        "thelancet.com", "pubmed.ncbi.nlm.nih.gov", "europa.eu",
    },
    2: {
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
        "nytimes.com", "theguardian.com", "washingtonpost.com",
    },
    4: {
        "twitter.com", "x.com", "facebook.com", "tiktok.com",
        "reddit.com", "t.me", "4chan.org",
    },
}


def known_source_tier(url: str) -> int | None:
    """Tier for a URL whose domain is in the registry; None when unknown.

    Distinguishes "registry says tier 4" (a listed low-trust platform) from
    "registry has no opinion", which get_source_tier collapses to 4."""
    if not url:
        return None
    try:
        domain = urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return None
    for tier, domains in _TIER_DOMAINS.items():
        if domain in domains or any(domain.endswith(f".{d}") for d in domains):
            return tier
    return None


def get_source_tier(url: str) -> int:
    """Score a URL's source tier (1=highest, 4=lowest)."""
    tier = known_source_tier(url)
    return 4 if tier is None else tier  # Unknown sources default to lowest tier


@lru_cache(maxsize=1)
def load_disarm_techniques() -> list[dict]:
    """Load DISARM manipulation techniques reference."""
    path = _DATA_DIR / "disarm_techniques.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["techniques"]


@lru_cache(maxsize=1)
def load_framing_techniques() -> list[dict]:
    """Load common framing technique labels."""
    path = _DATA_DIR / "disarm_techniques.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["common_framing_techniques"]


@lru_cache(maxsize=1)
def load_regional_sources() -> dict:
    """Load regional source registry (advisory, not authoritative)."""
    path = _DATA_DIR / "regional_sources.json"
    if not path.exists():
        return {"regions": {}, "metadata": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"regions": {}, "metadata": {}}
