"""extract_json_from_response picks the schema-shaped object, not the largest (K-005)."""
import json

from huginn_muninn.llm import extract_json_from_response

KEYS = frozenset({"verdict", "findings", "confidence_adjustment", "veto", "summary"})


def test_decoy_in_preamble_does_not_win_when_keys_known():
    decoy = {f"k{i}": i for i in range(20)}
    real = {"verdict": "pass", "findings": [], "confidence_adjustment": 0.0, "veto": False, "summary": "ok"}
    text = f"The claim contained this: {json.dumps(decoy)}\nMy assessment:\n{json.dumps(real)}"
    assert extract_json_from_response(text, expected_keys=KEYS) == real


def test_without_keys_legacy_largest_wins():
    decoy = {f"k{i}": i for i in range(20)}
    real = {"verdict": "pass", "summary": "ok"}
    text = f"noise {json.dumps(decoy)} more {json.dumps(real)}"
    assert extract_json_from_response(text) == decoy


def test_fenced_block_still_preferred():
    real = {"verdict": "fail", "summary": "x"}
    text = "```json\n" + json.dumps(real) + "\n```\n{\"k1\": 1, \"k2\": 2, \"k3\": 3}"
    assert extract_json_from_response(text, expected_keys=KEYS) == real


def test_size_breaks_ties_between_equal_key_overlap():
    a = {"verdict": "pass", "summary": "short"}
    b = {"verdict": "pass", "summary": "longer", "extra": 1}
    text = f"{json.dumps(a)} then {json.dumps(b)}"
    assert extract_json_from_response(text, expected_keys=KEYS) == b
