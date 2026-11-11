"""Rating scripts for the Method 1 vs Method 2 comparison (X-10, 2026-10-25)."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PASS1 = {"evidence_for": [], "evidence_against": [], "unknowns": []}
PASS2 = {
    "verdict": "false", "confidence": 0.8,
    "evidence_for": [], "evidence_against": [{"text": "e", "source_url": "https://x.org", "source_tier": 1,
                                              "supports_claim": False}],
    "unknowns": ["u"],
    "common_ground": {"shared_concern": "s", "framing_technique": "none_detected", "technique_explanation": "t",
                      "reflection": "r?"},
    "escalation": {"score": 0.1, "should_escalate": False, "reason": "simple"},
}


class FakeClient:
    def __init__(self):
        self.replies = [json.dumps(PASS1), json.dumps(PASS2)]

    def generate(self, prompt):
        return self.replies.pop(0)


def test_method1_runs_both_passes_and_validates():
    out = _load("rating_generate").run_method1(FakeClient(), "c")
    assert out["verdict"] == "false"


def test_method1_result_renders_without_pipeline_sections():
    text = _load("rating_judge").render_analysis({"result": {**PASS2, "claim": "c"}})
    assert "Overall confidence: 0.80" in text


def test_method1_render_hides_internal_escalation_score():
    text = _load("rating_judge").render_analysis({"result": {**PASS2, "claim": "c"}})
    assert "should_escalate" not in text


def test_methods_rubric_is_format_neutral(tmp_path, monkeypatch):
    judge = _load("rating_judge")
    monkeypatch.setattr(judge, "run_dir", lambda run: tmp_path)
    for label, result in [("m1", {**PASS2, "claim": "c"}), ("m2", {"decomposition": {"x": 1}})]:
        (tmp_path / label).mkdir()
        (tmp_path / label / "S-1.json").write_text(json.dumps({"claim": "c", "result": result}), encoding="utf-8")
    judge.prepare(SimpleNamespace(run="r", models="m1,m2", seed=1, rubric="methods"))
    item = next((tmp_path / "blind" / "items").glob("*.md")).read_text(encoding="utf-8")
    assert "has more sections" in item


def test_weighted_kappa_is_one_for_identical_ratings():
    assert _load("ecf_agreement").weighted_kappa([0, 2, 4, 1], [0, 2, 4, 1]) == 1.0


def test_weighted_kappa_is_negative_for_reversed_ratings():
    assert _load("ecf_agreement").weighted_kappa([0, 1, 3, 4], [4, 3, 1, 0]) < 0


def test_spearman_handles_ties():
    rho = _load("ecf_agreement").spearman([0.5, 0.5, 1.0, 0.0], [0.4, 0.6, 0.9, 0.1])
    assert 0.9 < rho <= 1.0


def test_scores_snap_to_the_five_steps():
    assert _load("ecf_agreement").to_step(0.62) == 2


PROFILE = {"evidence_quality": 0.1, "source_reliability": 0.2, "claim_testability": 0.8,
           "expert_consensus": 0.05, "internal_coherence": 0.3}


class ProfileClient:
    def generate(self, prompt):
        assert "Rate the claim as stated" in prompt
        return json.dumps({"verdict": "pass", "findings": [], "confidence_profile": PROFILE})


def _gallery_result(tmp_path, name, profile=True):
    r = {"claim": "c", "audit": {"verdict": "pass_with_warnings", "findings": [{"x": 1}]},
         **{k: {"k": 1} for k in ("decomposition", "origins", "intelligence", "ttps", "bridge")}}
    if profile:
        r["confidence_profile"] = {"evidence_quality": 0.8}
    (tmp_path / name).write_text(json.dumps(r), encoding="utf-8")
    return tmp_path / name


def test_regen_picks_only_the_latest_version_with_a_profile(tmp_path):
    _gallery_result(tmp_path, "GP-07-opus-v1.json")
    _gallery_result(tmp_path, "GP-07-opus-v3.json")
    _gallery_result(tmp_path, "HS-01-opus-v2.json", profile=False)
    found = _load("regen_ecf_profiles").latest_with_profile(tmp_path)
    assert {k: v.name for k, v in found.items()} == {"GP-07": "GP-07-opus-v3.json"}


def test_regen_replaces_the_profile_with_the_new_scores(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    _load("regen_ecf_profiles").rescore(ProfileClient(), f, "m", "medium")
    assert json.loads(f.read_text(encoding="utf-8"))["confidence_profile"]["expert_consensus"] == 0.05


def test_regen_keeps_the_published_audit_findings(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    _load("regen_ecf_profiles").rescore(ProfileClient(), f, "m", "medium")
    assert json.loads(f.read_text(encoding="utf-8"))["audit"]["findings"] == [{"x": 1}]


def test_regen_records_provenance(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    _load("regen_ecf_profiles").rescore(ProfileClient(), f, "m", "medium")
    assert json.loads(f.read_text(encoding="utf-8"))["confidence_profile_provenance"]["model"] == "m"


class PartialClient:
    def generate(self, prompt):
        return json.dumps({"confidence_profile": {"evidence_quality": 0.1}})


def test_regen_refuses_a_partial_profile(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    with pytest.raises(ValueError):
        _load("regen_ecf_profiles").rescore(PartialClient(), f, "m", "medium")


def test_regen_leaves_the_file_untouched_on_a_partial_profile(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    before = f.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        _load("regen_ecf_profiles").rescore(PartialClient(), f, "m", "medium")
    assert f.read_text(encoding="utf-8") == before


def test_regen_stores_only_the_five_scores(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    _load("regen_ecf_profiles").rescore(ProfileClient(), f, "m", "medium")
    assert set(json.loads(f.read_text(encoding="utf-8"))["confidence_profile"]) == set(PROFILE)


def test_regen_keeps_the_original_profile_across_reruns(tmp_path):
    f = _gallery_result(tmp_path, "GP-07-opus-v3.json")
    mod = _load("regen_ecf_profiles")
    mod.rescore(ProfileClient(), f, "m", "medium")
    mod.rescore(ProfileClient(), f, "m", "medium")
    prov = json.loads(f.read_text(encoding="utf-8"))["confidence_profile_provenance"]
    assert prov["replaced"] == {"evidence_quality": 0.8}


def test_regen_refuses_a_result_without_upstream_outputs(tmp_path):
    f = tmp_path / "GP-07-opus-v3.json"
    f.write_text(json.dumps({"claim": "c", "confidence_profile": {}}), encoding="utf-8")
    with pytest.raises(ValueError):
        _load("regen_ecf_profiles").rescore(ProfileClient(), f, "m", "medium")


def _located_result(veto=False, reframe="Round one says the data was faked."):
    return {"result": {
        "claim": "c", "overall_confidence": 0.5, "bridge_withheld": veto,
        "decomposition": {"sub_claims": [{"text": "X"}]},
        "bridge": {"reframe": reframe},
        "audit": {"verdict": "pass_with_warnings", "veto": veto, "findings": [
            {"severity": "medium", "description": "Overstated.",
             "locations": [{"section": "bridge", "quote": "the data was faked", "paths": ["bridge.reframe"]}],
             "located": True}]},
    }}


def test_judge_view_prints_finding_under_its_passage():
    lines = _load("rating_judge").render_analysis(_located_result()).splitlines()
    i = next(n for n, line in enumerate(lines) if "reframe: Round one" in line)
    assert "Auditor finding (medium) about this passage: Overstated." in lines[i + 1]


def test_judge_view_hides_derived_location_fields():
    text = _load("rating_judge").render_analysis(_located_result())
    assert "paths:" not in text and "located:" not in text


def test_judge_view_rechecks_the_passage():
    text = _load("rating_judge").render_analysis(_located_result(reframe="Something else entirely here."))
    assert "about this passage" not in text


def test_judge_view_drops_bridge_notes_on_veto():
    text = _load("rating_judge").render_analysis(_located_result(veto=True))
    assert "about this passage" not in text


def test_judge_view_never_prints_raw_quotes():
    rec = _located_result()
    rec["result"]["audit"]["findings"][0]["locations"].append(
        {"section": "bridge", "quote": "a sentence the report never contained", "paths": []})
    text = _load("rating_judge").render_analysis(rec)
    assert "never contained" not in text and "quote:" not in text


def test_judge_view_without_notes_matches_a_result_without_locations():
    judge = _load("rating_judge")
    plain = _located_result()
    del plain["result"]["audit"]["findings"][0]["locations"]
    del plain["result"]["audit"]["findings"][0]["located"]
    assert judge.render_analysis(_located_result(), notes=False) == judge.render_analysis(plain)
