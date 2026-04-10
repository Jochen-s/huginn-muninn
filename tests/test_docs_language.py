"""P2-12 lint guard: core documentation must not use the pathologising
'victim of cognitive warfare' framing as an unquoted declarative claim.

Research notes may mention the phrase only under a strict allowlist: the
phrase must sit inside a recognised quote pair AND a word-bounded strong
rejection cue must appear within MAX_CONTEXT_DISTANCE characters of it.
This blocks both the weak-marker sieve (e.g., "instead", "we use" leaking
through) and the quote-only affirmative bypass (e.g., `We describe audiences
as "victims of cognitive warfare" because that is the most accurate term.`).

Section headings of the form `### The "..." framing` are allowed on the
narrow quote-only exception so that the rejection-record heading survives.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Pathologising phrases that remove user agency
PATHOLOGISING_PHRASES = [
    "victim of cognitive warfare",
    "victims of cognitive warfare",
]

# Core documentation files scanned for any occurrence (quoted or not).
# These files must not contain the pathologising framing at all.
CORE_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "ANTI-WEAPONIZATION-CHARTER.md",
]

# Research notes are scanned with a tighter rule: quoted references in a
# rejection record are allowed, but only with a nearby strong rejection cue.
RESEARCH_DIR = REPO_ROOT / "research"
RESEARCH_DOCS = (
    sorted(p for p in RESEARCH_DIR.glob("*.md")) if RESEARCH_DIR.exists() else []
)

# Quote characters recognised by the allowlist. Only straight and curly
# double-quotes -- single quotes are too common as apostrophes to be safe.
QUOTE_PAIRS = [
    ('"', '"'),
    ("\u201c", "\u201d"),  # curly double
]

# Word-bounded strong rejection cues. Substrings like "instead", "framing",
# "we use" are intentionally NOT included -- they are common English glue
# that would let affirmative declarative sentences slip through. Each pattern
# below is specific enough that its presence is reliable evidence of
# rejection context.
STRONG_REJECTION_PATTERNS = [
    re.compile(r"\b(?:reject|rejected|rejection)\b", re.IGNORECASE),
    re.compile(r"\bdid not integrate\b", re.IGNORECASE),
    re.compile(r"\b(?:do|does) not (?:use|adopt|integrate|implement)\b", re.IGNORECASE),
    re.compile(r"\b(?:declined|excluded|ruled out)\b", re.IGNORECASE),
    re.compile(r"\bremoves agency\b", re.IGNORECASE),
    re.compile(r"\brescuer-victim dynamic\b", re.IGNORECASE),
    re.compile(r"\binconsistent with\b", re.IGNORECASE),
]

# Maximum characters between the phrase and a strong rejection cue. Tight
# enough that a stray "rejected" elsewhere in a long line cannot launder
# an affirmative use of the phrase.
MAX_CONTEXT_DISTANCE = 60


def _iter_pathologising_lines(path: Path):
    """Yield (line_num, line, phrase) for every occurrence of a pathologising
    phrase on the given path."""
    text = path.read_text(encoding="utf-8")
    for idx, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in lower:
                yield idx, line, phrase


def _has_exact_quoted_phrase(lower_line: str, phrase: str) -> bool:
    return any(
        f"{q_open}{phrase}{q_close}" in lower_line
        for q_open, q_close in QUOTE_PAIRS
    )


def _has_strong_rejection_cue_near_phrase(lower_line: str, phrase: str) -> bool:
    phrase_idx = lower_line.find(phrase)
    if phrase_idx == -1:
        return False
    for pattern in STRONG_REJECTION_PATTERNS:
        for match in pattern.finditer(lower_line):
            if abs(match.start() - phrase_idx) <= MAX_CONTEXT_DISTANCE:
                return True
    return False


def _is_quoted_or_rejection_context(line: str, phrase: str) -> bool:
    """Allow the phrase in research docs only if BOTH: (a) it is inside a
    recognised quote pair, AND (b) a strong rejection cue is within
    MAX_CONTEXT_DISTANCE characters. Markdown headings of the form
    `### The "..." framing` are allowed as a narrow quote-only exception."""
    lower = line.lower()
    stripped = lower.lstrip()

    # Narrow exception: markdown heading for the rejection-record section
    # (e.g., `### The "victim of cognitive warfare" framing`).
    if stripped.startswith("###") and _has_exact_quoted_phrase(stripped, phrase):
        return True

    # Everywhere else, require BOTH an exact quoted phrase AND a nearby
    # strong rejection cue. This blocks the quote-only affirmative bypass:
    # `We describe audiences as "victims of cognitive warfare" because ...`
    return (
        _has_exact_quoted_phrase(lower, phrase)
        and _has_strong_rejection_cue_near_phrase(lower, phrase)
    )


class TestDocsLanguageCoreDocs:
    """README and Charter must not contain the pathologising framing at all,
    quoted or unquoted. These are user-facing defining documents."""

    def test_core_docs_have_no_pathologising_phrases(self):
        violations = []
        for doc in CORE_DOCS:
            if not doc.exists():
                continue
            for line_num, line, phrase in _iter_pathologising_lines(doc):
                violations.append(
                    f"{doc.name}:{line_num}: '{phrase}' in: {line.strip()[:120]}"
                )
        assert violations == [], (
            "Pathologising phrases found in core docs:\n" + "\n".join(violations)
        )


class TestDocsLanguageResearchDocs:
    """Research notes may use the phrase in quoted rejection records but must
    not use it as an unquoted declarative claim."""

    def test_research_docs_allow_quoted_rejection_references(self):
        violations = []
        for doc in RESEARCH_DOCS:
            for line_num, line, phrase in _iter_pathologising_lines(doc):
                if not _is_quoted_or_rejection_context(line, phrase):
                    rel = doc.relative_to(REPO_ROOT)
                    violations.append(
                        f"{rel}:{line_num}: unquoted use of '{phrase}': "
                        f"{line.strip()[:120]}"
                    )
        assert violations == [], (
            "Pathologising phrases used as unquoted claims in research docs:\n"
            + "\n".join(violations)
        )


class TestDocsLanguageReplacementIsDocumented:
    """The Gorgon Trap rejection record must document the replacement language
    so future contributors can find the agreed vocabulary."""

    def test_replacement_language_present_in_rejection_record(self):
        research_note = REPO_ROOT / "research" / "gorgon-trap-integration.md"
        if not research_note.exists():
            pytest.skip("gorgon-trap-integration.md not present")
        text = research_note.read_text(encoding="utf-8").lower()
        assert (
            "people navigating information environments designed to exploit trust"
            in text
        ), (
            "Research note must document the replacement language for "
            "'victim of cognitive warfare' (Sprint 1 decision, P2-12 lint guard)."
        )


class TestDocsLanguageAllowlistAdversarial:
    """Adversarial regression tests that pin the lint against specific attack
    patterns the fleet and Codex reviewers identified during PR 1 review."""

    def test_holodeck_pass_through_is_blocked(self):
        """Dr. Community Repair L2-002 pass-through attack: weak markers
        'we use', 'framing' appear together in an affirmative sentence that
        declares the pathologising framing as the pipeline's own stance."""
        attack = (
            'The pipeline treats the user as a victim of cognitive '
            'warfare -- that framing is what we use in our MVP.'
        )
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in attack.lower():
                assert not _is_quoted_or_rejection_context(attack, phrase), (
                    "Holodeck pass-through must be blocked by the hardened "
                    "allowlist, but it was accepted."
                )
                return
        pytest.fail("adversarial line did not contain a pathologising phrase")

    def test_quote_only_affirmative_bypass_is_blocked(self):
        """Codex Q8 blind spot: an affirmative sentence that uses the phrase
        inside quotes but without any rejection cue must not slip through."""
        attack = (
            'We describe audiences as "victims of cognitive warfare" '
            'because that is the most accurate term.'
        )
        blocked = False
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in attack.lower():
                if not _is_quoted_or_rejection_context(attack, phrase):
                    blocked = True
                    break
        assert blocked, (
            "Quote-only affirmative bypass must be blocked by the hardened "
            "allowlist, but it was accepted."
        )

    def test_substring_marker_leak_is_blocked(self):
        """Klingon K-PR1-01: substrings 'instead', 'framing', 'we use' must
        not be honoured as rejection cues in isolation. A line that contains
        the quoted phrase plus 'framing' without a strong rejection cue
        nearby must be rejected."""
        attack = (
            'Our MVP framing treats the user as a "victim of cognitive '
            'warfare" rather than as an autonomous adult.'
        )
        blocked = False
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in attack.lower():
                if not _is_quoted_or_rejection_context(attack, phrase):
                    blocked = True
                    break
        assert blocked, (
            "Substring marker leak must be blocked, but the allowlist "
            "accepted the line."
        )

    def test_genuine_rejection_record_still_accepted(self):
        """The live rejection record in research/gorgon-trap-integration.md
        must continue to pass after the lint is tightened. Guard against
        over-correcting."""
        legitimate = (
            'The paper consistently refers to audiences of disinformation '
            'as "victims of cognitive warfare". This framing removes agency, '
            'creates a rescuer-victim dynamic, and is inconsistent with the '
            'deep-canvassing evidence base.'
        )
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in legitimate.lower():
                assert _is_quoted_or_rejection_context(legitimate, phrase), (
                    "The genuine rejection-record sentence must still be "
                    "allowed by the tightened lint."
                )
                return
        pytest.fail("rejection-record line did not contain a pathologising phrase")

    def test_markdown_heading_exception_accepted(self):
        """Section headings for the rejection record are allowed on the
        narrow quote-only exception so the heading survives."""
        heading = '### The "victim of cognitive warfare" framing'
        for phrase in PATHOLOGISING_PHRASES:
            if phrase in heading.lower():
                assert _is_quoted_or_rejection_context(heading, phrase), (
                    "The rejection-record heading must be allowed by the "
                    "narrow heading exception."
                )
                return
        pytest.fail("heading did not contain a pathologising phrase")
