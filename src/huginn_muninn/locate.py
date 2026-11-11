"""Place Auditor findings on the passages they are about (design C, 2026-11-10).

The Auditor quotes each passage a finding concerns and names its section.
This step checks, without any model call, that the quote occurs in that
section and records the path of every string that contains it. A quote that
is too short, names an unknown section or is not found gets no path, and the
finding stays unlocated: a location is never guessed.
"""
from __future__ import annotations

import json
import re
import unicodedata

SECTIONS = ("decomposition", "origins", "intelligence", "ttps", "bridge")
MIN_QUOTE_CHARS = 12
MIN_QUOTE_WORDS = 4  # the prompt asks for 5 to 25; a shorter fragment pins a finding to stock phrases

_TYPOGRAPHIC = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})
_SPACE = re.compile(r"\s+")
_BARE_QUOTE = re.compile(r'(?<!\\)"')


def _norm(s: str) -> str:
    return _SPACE.sub(" ", unicodedata.normalize("NFKC", s).translate(_TYPOGRAPHIC)).strip()


def _undo_prompt_encoding(quote: str) -> str:
    r"""The Auditor reads the analysis as json.dumps output passed through
    sanitize_for_prompt, so a quote can carry &quot;, \u00e8 or \" where the
    text has the plain character. Undo both steps; keep the quote as given if
    the JSON escapes do not decode."""
    q = quote.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
    if "\\" not in q:
        return q
    try:
        return json.loads('"' + _BARE_QUOTE.sub(r'\\"', q) + '"')
    except ValueError:
        return q


def _strings(value, path: str):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _strings(v, f"{path}[{i}]")


def normalise_section(section) -> str:
    """'Bridge', ' bridge ', 'bridge.reframe' and 'bridge|ttps' all name
    bridge; anything that is not one of SECTIONS gives ''."""
    if not isinstance(section, str):
        return ""
    s = re.split(r"[.|\[]", section.strip().lower(), maxsplit=1)[0].strip()
    return s if s in SECTIONS else ""


def locate_quote(sections: dict, section, quote) -> list[str]:
    """Paths of the strings in `section` that contain `quote`, or [].

    The quote is tried as given and with the prompt encoding undone, so text
    that really holds a backslash or an HTML entity is found too."""
    name = normalise_section(section)
    if not name or not isinstance(quote, str):
        return []
    forms = {_norm(quote), _norm(_undo_prompt_encoding(quote))}
    forms = {q for q in forms if len(q) >= MIN_QUOTE_CHARS and len(q.split()) >= MIN_QUOTE_WORDS}
    if not forms:
        return []
    return [p for p, s in _strings(sections.get(name), name)
            if any(q in _norm(s) for q in forms)]


def locate_findings(audit: dict, sections: dict) -> dict:
    """Fill `paths` and `located` on every finding in place; return counts."""
    stats = {"findings": 0, "located": 0, "quotes": 0, "quotes_found": 0}
    for f in audit.get("findings") or []:
        if not isinstance(f, dict):
            continue
        stats["findings"] += 1
        locs = [loc for loc in (f.get("locations") or []) if isinstance(loc, dict)]
        for loc in locs:
            quote = loc.get("quote") if isinstance(loc.get("quote"), str) else ""
            loc["paths"] = locate_quote(sections, loc.get("section"), quote)
            if quote.strip():
                stats["quotes"] += 1
                stats["quotes_found"] += bool(loc["paths"])
        f["locations"] = locs
        f["located"] = any(loc["paths"] for loc in locs)
        stats["located"] += f["located"]
    return stats
