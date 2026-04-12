# Sprint 3 PR 1 "Response Projection + CLI Wiring" Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the compound defamation-surface blocker by projecting AnalysisReport through a new AnalysisResponse envelope at all 10 external serialization boundaries, wire Sprint 2 Bridge fields into the CLI, and add operator field-suppression configuration.

**Architecture:** An `AnalysisResponse` Pydantic envelope wraps the projected `AnalysisReport` in a `data` field with `suppressed_fields` disclosure metadata. Projection happens at READ boundaries only (never at write). A `Settings.suppressed_fields: tuple[str, ...]` field parsed from `HUGINN_SUPPRESS_FIELDS` env var controls which Bridge fields are suppressed. The internal job store and DB retain the full AnalysisReport.

**Tech Stack:** Python 3.14, Pydantic v2, FastAPI, Click (CLI), pytest

**Baseline:** v0.8.0 "Scoped Diagnostics", 209/209 tests passing on public repo, 244/244 on monorepo

**Zero-Regression Constraints:** 16 constraints (see `.fleet/reports/2026-04-12-sprint3-plan.md` section 12). Key: strict-subset applies to `data` field only; envelope metadata exempt; projection at READ boundaries only; suppressed_fields disclosure in API + webhook + callback; bidirectional completeness test.

---

### Task 1: Install pytest-httpx and establish true test baseline

**Files:**
- Modify: `pyproject.toml` (add dev dependency)
- Verify: `tests/test_llm_openai.py`, `tests/test_search.py`, `tests/test_integration_phase6.py`

**Step 1: Add pytest-httpx to dev dependencies**

In `pyproject.toml`, add `pytest-httpx` to the dev/test dependencies section.

**Step 2: Run full test suite and verify the 22 previously-erroring tests now pass**

Run: `python -m pytest -q -m "not e2e" --tb=short`
Expected: 0 errors. Note the new total test count (should be 209 + 22 = ~231 on public repo scope, plus monorepo-only tests).

If `pytest-httpx` causes version conflicts with the existing `httpx` pin, fall back to `pytest.importorskip("pytest_httpx")` at the top of each affected test file.

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pytest-httpx to resolve 22 erroring test fixtures"
```

---

### Task 2: Add suppressed_fields config to Settings

**Files:**
- Modify: `src/huginn_muninn/config.py:10-49` (Settings dataclass)
- Create: `tests/test_config.py` (new file)

**Step 1: Write failing tests for suppressed_fields config**

```python
# tests/test_config.py
"""Tests for operator configuration, especially field suppression."""
import os
import pytest
from huginn_muninn.config import Settings, get_settings, _reset_settings

# Valid suppressible field names (BridgeOutput fields that operators can hide)
VALID_SUPPRESSIBLE = {
    "communication_posture", "pattern_density_warning",
    "vacuum_filled_by", "prebunking_note",
}


class TestSuppressedFieldsConfig:
    """Sprint 3 PR 1 C3: operator field-suppression configuration."""

    def setup_method(self):
        _reset_settings()

    def teardown_method(self):
        _reset_settings()
        # Clean env
        os.environ.pop("HUGINN_SUPPRESS_FIELDS", None)

    def test_default_suppressed_fields_is_empty_tuple(self):
        settings = Settings()
        assert settings.suppressed_fields == ()

    def test_suppressed_fields_parsed_from_env(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by,prebunking_note")
        settings = Settings()
        assert settings.suppressed_fields == ("vacuum_filled_by", "prebunking_note")

    def test_suppressed_fields_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", " vacuum_filled_by , prebunking_note ")
        settings = Settings()
        assert settings.suppressed_fields == ("vacuum_filled_by", "prebunking_note")

    def test_empty_env_var_produces_empty_tuple(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "")
        settings = Settings()
        assert settings.suppressed_fields == ()

    def test_unknown_field_name_raises_at_init(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vaccum_filled_by")
        with pytest.raises(ValueError, match="vaccum_filled_by"):
            Settings()

    def test_overall_confidence_cannot_be_suppressed(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "overall_confidence")
        with pytest.raises(ValueError, match="overall_confidence"):
            Settings()

    def test_singleton_caches_settings(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by")
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_reset_clears_singleton(self, monkeypatch):
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "vacuum_filled_by")
        s1 = get_settings()
        _reset_settings()
        monkeypatch.setenv("HUGINN_SUPPRESS_FIELDS", "")
        s2 = get_settings()
        assert s1 is not s2
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL (suppressed_fields field does not exist)

**Step 3: Implement suppressed_fields on Settings**

In `config.py`, add the field and validation:

```python
# At top of file, add:
_SUPPRESSIBLE_FIELDS = frozenset({
    "communication_posture", "pattern_density_warning",
    "vacuum_filled_by", "prebunking_note",
})


def _parse_suppress_fields() -> tuple[str, ...]:
    raw = os.environ.get("HUGINN_SUPPRESS_FIELDS", "")
    if not raw.strip():
        return ()
    fields = tuple(f.strip() for f in raw.split(",") if f.strip())
    for f in fields:
        if f not in _SUPPRESSIBLE_FIELDS:
            raise ValueError(
                f"Unknown suppressed field: {f!r}. "
                f"Valid fields: {sorted(_SUPPRESSIBLE_FIELDS)}"
            )
    return fields

# In Settings class, add field:
    suppressed_fields: tuple[str, ...] = field(
        default_factory=_parse_suppress_fields
    )
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_config.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/huginn_muninn/config.py tests/test_config.py
git commit -m "feat(config): add HUGINN_SUPPRESS_FIELDS with startup validation"
```

---

### Task 3: Create AnalysisResponse envelope model

**Files:**
- Modify: `src/huginn_muninn/contracts.py` (add AnalysisResponse after AnalysisReport)
- Modify: `tests/test_contracts.py` (add TestAnalysisResponse class)

**Step 1: Write failing tests**

```python
# In tests/test_contracts.py, add at the end (before any existing final class):

from huginn_muninn.contracts import AnalysisResponse


class TestAnalysisResponse:
    """Sprint 3 PR 1 C1: AnalysisResponse envelope model."""

    def _make_report_dict(self) -> dict:
        """Minimal valid AnalysisReport dict for projection tests."""
        return {
            "claim": "Test claim",
            "decomposition": {
                "sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
                "original_claim": "Test claim",
                "complexity": "simple",
            },
            "origins": {"origins": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["safety"],
                "issue_overlap": "overlap",
                "narrative_deconstruction": "decon",
                "perception_gap": "gap",
                "moral_foundations": {},
                "reframe": "reframe",
                "socratic_dialogue": ["R1"],
                "communication_posture": "inoculation_first",
                "pattern_density_warning": True,
                "vacuum_filled_by": "absence of primary research filled by anonymous commentary",
                "prebunking_note": "watch for fabricated-source-mimicry pattern",
            },
            "audit": {
                "verdict": "pass",
                "findings": [],
                "confidence_adjustment": 0.0,
                "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.72,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

    def test_from_report_unsuppressed_preserves_all_fields(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        assert response.data["bridge"]["communication_posture"] == "inoculation_first"
        assert response.data["bridge"]["vacuum_filled_by"] != ""
        assert response.suppressed_fields == []

    def test_from_report_suppresses_vacuum_filled_by(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(
            report, suppressed=frozenset({"vacuum_filled_by"})
        )
        assert response.data["bridge"]["vacuum_filled_by"] == ""
        assert response.suppressed_fields == ["vacuum_filled_by"]

    def test_from_report_suppresses_multiple_fields(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(
            report, suppressed=frozenset({"vacuum_filled_by", "prebunking_note", "pattern_density_warning"})
        )
        assert response.data["bridge"]["vacuum_filled_by"] == ""
        assert response.data["bridge"]["prebunking_note"] == ""
        assert response.data["bridge"]["pattern_density_warning"] is False
        assert sorted(response.suppressed_fields) == [
            "pattern_density_warning", "prebunking_note", "vacuum_filled_by"
        ]

    def test_suppression_does_not_move_confidence(self):
        report = AnalysisReport(**self._make_report_dict())
        unsup = AnalysisResponse.from_report(report, suppressed=frozenset())
        sup = AnalysisResponse.from_report(
            report, suppressed=frozenset({"vacuum_filled_by", "prebunking_note"})
        )
        assert unsup.data["overall_confidence"] == sup.data["overall_confidence"]

    def test_data_is_strict_subset_of_analysis_report(self):
        """Zero-regression constraint #3: data keys are subset of Report."""
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        assert set(response.data.keys()).issubset(
            set(AnalysisReport.model_fields.keys())
        )

    def test_bidirectional_completeness(self):
        """Zero-regression constraint #15: every Report field appears in
        data or in the documented exclusion list."""
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        report_keys = set(AnalysisReport.model_fields.keys())
        data_keys = set(response.data.keys())
        missing = report_keys - data_keys
        assert missing == set(), (
            f"AnalysisReport fields missing from AnalysisResponse.data "
            f"without documented exclusion: {missing}"
        )

    def test_envelope_has_suppressed_fields_and_api_version(self):
        report = AnalysisReport(**self._make_report_dict())
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        d = response.model_dump(mode="json")
        assert "data" in d
        assert "suppressed_fields" in d
        assert "api_version" in d

    def test_unsuppressed_default_is_backward_compatible(self):
        """With suppressed=frozenset(), AnalysisResponse.data must be
        shape-identical to AnalysisReport.model_dump()."""
        raw = self._make_report_dict()
        report = AnalysisReport(**raw)
        response = AnalysisResponse.from_report(report, suppressed=frozenset())
        report_dump = report.model_dump(mode="json")
        assert response.data == report_dump
```

**Step 2: Run to verify failure**

Run: `python -m pytest tests/test_contracts.py::TestAnalysisResponse -v`
Expected: FAIL (AnalysisResponse not defined)

**Step 3: Implement AnalysisResponse**

In `contracts.py`, after the `AnalysisReport` class, add:

```python
class AnalysisResponse(BaseModel):
    """Sprint 3 PR 1: API response envelope.

    Wraps a projected AnalysisReport in a `data` field with envelope
    metadata. The `data` field is a strict subset of AnalysisReport
    (zero-regression constraint #3). Envelope metadata (suppressed_fields,
    api_version) is not subject to the strict-subset constraint.

    Projection happens at READ boundaries only. The internal job store
    and DB retain the full AnalysisReport. This model is constructed
    via the `from_report()` classmethod, never from a raw dict."""

    data: dict
    suppressed_fields: list[str] = Field(default_factory=list)
    api_version: str = "0.9.0"

    # Safe defaults for suppressible fields, keyed by field name.
    # Used to replace suppressed field values without removing them
    # from the schema (shape preservation).
    _FIELD_DEFAULTS: ClassVar[dict[str, object]] = {
        "communication_posture": "direct_correction",
        "pattern_density_warning": False,
        "vacuum_filled_by": "",
        "prebunking_note": "",
    }

    @classmethod
    def from_report(
        cls,
        report: "AnalysisReport",
        suppressed: frozenset[str],
    ) -> "AnalysisResponse":
        """Project an AnalysisReport for external consumption.

        Args:
            report: A validated AnalysisReport instance.
            suppressed: Field names to replace with safe defaults.

        Returns:
            AnalysisResponse envelope with projected data.
        """
        data = report.model_dump(mode="json")
        suppressed_list = []
        if suppressed and "bridge" in data:
            bridge = data["bridge"]
            for field_name in sorted(suppressed):
                if field_name in bridge and field_name in cls._FIELD_DEFAULTS:
                    bridge[field_name] = cls._FIELD_DEFAULTS[field_name]
                    suppressed_list.append(field_name)
        return cls(data=data, suppressed_fields=suppressed_list)
```

Add `ClassVar` to imports at the top of contracts.py:

```python
from typing import Annotated, ClassVar, Literal
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_contracts.py::TestAnalysisResponse -v`
Expected: ALL PASS

**Step 5: Run full suite for zero-regression**

Run: `python -m pytest -q tests/test_contracts.py tests/test_agents.py tests/test_orchestrator.py tests/test_integration_m2.py`
Expected: All pass (179+ existing + new TestAnalysisResponse tests)

**Step 6: Commit**

```bash
git add src/huginn_muninn/contracts.py tests/test_contracts.py
git commit -m "feat(contracts): add AnalysisResponse envelope with from_report() projection"
```

---

### Task 4: Normalize orchestrator return + add projection helper

**Files:**
- Modify: `src/huginn_muninn/orchestrator.py:192-204` (normalize return)
- Create: `src/huginn_muninn/projection.py` (projection helper function)
- Create: `tests/test_projection.py`

**Step 1: Write failing test for projection helper**

```python
# tests/test_projection.py
"""Tests for the AnalysisResponse projection helper."""
from huginn_muninn.projection import project_analysis


class TestProjectAnalysis:
    """Sprint 3 PR 1: projection helper used at all 10 boundaries."""

    def _make_raw_analysis(self) -> dict:
        return {
            "claim": "X",
            "decomposition": {
                "sub_claims": [{"text": "X", "type": "factual", "verifiable": True}],
                "original_claim": "X",
                "complexity": "simple",
            },
            "origins": {"origins": []},
            "intelligence": {"actors": [], "relations": [], "narrative_summary": ""},
            "ttps": {"ttp_matches": [], "primary_tactic": "Assess"},
            "bridge": {
                "universal_needs": ["safety"],
                "issue_overlap": "o", "narrative_deconstruction": "d",
                "perception_gap": "g", "moral_foundations": {},
                "reframe": "r", "socratic_dialogue": ["R1"],
                "communication_posture": "inoculation_first",
                "vacuum_filled_by": "pattern description",
                "prebunking_note": "technique warning",
                "pattern_density_warning": True,
            },
            "audit": {
                "verdict": "pass", "findings": [],
                "confidence_adjustment": 0.0, "veto": False,
                "summary": "OK",
            },
            "overall_confidence": 0.7,
            "method": "method_2",
            "degraded": False,
            "degraded_reason": None,
        }

    def test_project_with_no_suppression(self):
        result = project_analysis(self._make_raw_analysis())
        assert result["data"]["bridge"]["vacuum_filled_by"] == "pattern description"
        assert result["suppressed_fields"] == []

    def test_project_with_suppression(self):
        result = project_analysis(
            self._make_raw_analysis(),
            suppressed=frozenset({"vacuum_filled_by"}),
        )
        assert result["data"]["bridge"]["vacuum_filled_by"] == ""
        assert result["suppressed_fields"] == ["vacuum_filled_by"]

    def test_project_normalizes_legacy_cache_hit(self):
        """BG-050: legacy dict missing Sprint 2 fields gets defaults."""
        raw = self._make_raw_analysis()
        del raw["bridge"]["communication_posture"]
        del raw["bridge"]["vacuum_filled_by"]
        del raw["bridge"]["prebunking_note"]
        del raw["bridge"]["pattern_density_warning"]
        result = project_analysis(raw)
        assert result["data"]["bridge"]["communication_posture"] == "direct_correction"

    def test_project_returns_envelope_shape(self):
        result = project_analysis(self._make_raw_analysis())
        assert "data" in result
        assert "suppressed_fields" in result
        assert "api_version" in result

    def test_project_non_method2_returns_as_is(self):
        """Method 1 verdicts should not be wrapped in an envelope."""
        verdict = {"claim": "X", "verdict": "likely_true", "confidence": 0.9}
        result = project_analysis(verdict, is_method2=False)
        assert result == verdict  # passthrough, no envelope
```

**Step 2: Implement projection.py**

```python
# src/huginn_muninn/projection.py
"""Sprint 3 PR 1: AnalysisResponse projection helper.

Single entry point for projecting analysis results at all 10 external
serialization boundaries. Handles BG-050 normalization (for legacy
cache hits) followed by AnalysisResponse envelope construction.

Used by: api.py, worker.py, cli.py (JSON output path)."""
from __future__ import annotations

import logging
from pydantic import ValidationError

from huginn_muninn.config import get_settings
from huginn_muninn.contracts import AnalysisReport, AnalysisResponse

log = logging.getLogger(__name__)


def project_analysis(
    raw: dict,
    *,
    suppressed: frozenset[str] | None = None,
    is_method2: bool = True,
) -> dict:
    """Normalize and project an analysis result for external consumption.

    Args:
        raw: Raw analysis dict (from orchestrator, job store, or DB cache).
        suppressed: Field names to suppress. If None, reads from Settings.
        is_method2: If False, returns the dict unchanged (Method 1 passthrough).

    Returns:
        AnalysisResponse envelope dict (if Method 2) or raw dict (if Method 1).
    """
    if not is_method2:
        return raw

    if suppressed is None:
        suppressed = frozenset(get_settings().suppressed_fields)

    # BG-050: normalize through the contract to populate any missing
    # defaults from schema evolution (legacy cache hits).
    try:
        report = AnalysisReport.model_validate(raw)
    except ValidationError:
        log.warning("Failed to validate analysis for projection; returning raw")
        return raw

    response = AnalysisResponse.from_report(report, suppressed=suppressed)
    return response.model_dump(mode="json")
```

**Step 3: Normalize orchestrator return**

In `orchestrator.py:192-204`, change:

```python
        # OLD:
        return result
```

to:

```python
        # Borg AP-1 fix: return normalized dict so downstream consumers
        # always receive schema-valid data with computed defaults populated.
        return AnalysisReport(**result).model_dump(mode="json")
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_projection.py tests/test_orchestrator.py tests/test_integration_m2.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/huginn_muninn/projection.py src/huginn_muninn/orchestrator.py tests/test_projection.py
git commit -m "feat(projection): add project_analysis helper + normalize orchestrator return"
```

---

### Task 5: Apply projection at all 10 API serialization boundaries

**Files:**
- Modify: `src/huginn_muninn/api.py` (6 endpoints)
- Modify: `src/huginn_muninn/worker.py` (webhook, callback, check-and-escalate dispatch)
- Create: `tests/test_api_projection.py`

**Step 1: Write integration tests for API projection**

Tests should use FastAPI's `TestClient` and mock the orchestrator/worker to verify that every endpoint returning Method 2 results wraps them in the AnalysisResponse envelope.

Key tests:
- `test_analyze_returns_envelope_shape` -- `/api/analyze` returns `{data: {...}, suppressed_fields: [], api_version: "0.9.0"}`
- `test_analyze_suppresses_configured_field` -- with `HUGINN_SUPPRESS_FIELDS=vacuum_filled_by`, the `data.bridge.vacuum_filled_by` is `""` and `suppressed_fields` is `["vacuum_filled_by"]`
- `test_check_and_escalate_projects_method2_key` -- the `method_2` value in the composite response is an AnalysisResponse envelope
- `test_history_projects_analyses` -- each analysis in `/api/history` `analyses` array is an AnalysisResponse envelope
- `test_job_result_projected_at_read_time` -- `GET /api/jobs/{id}` returns projected result even though full report is stored
- `test_batch_results_projected` -- `GET /api/batch/{id}` results are projected
- `test_compare_analyze_projected` -- `/api/compare` with `method=analyze` returns projected results
- `test_webhook_payload_includes_suppressed_fields_disclosure` -- webhook `result` is an AnalysisResponse envelope
- `test_callback_payload_includes_suppressed_fields_disclosure` -- callback `result` is an AnalysisResponse envelope
- `test_unsuppressed_response_is_backward_compatible` -- with no suppression, `data` is shape-identical to pre-Sprint-3 response

**Step 2: Apply projection in api.py**

Add `from huginn_muninn.projection import project_analysis` at the top.

For each endpoint that returns Method 2 results, wrap the result through `project_analysis()`:

- `api.py:289` `/api/analyze`: `result = project_analysis(result)`
- `api.py:308` `/api/check-and-escalate`: `report = project_analysis(report)` before embedding in composite dict
- `api.py:332` `/api/history`: project each analysis in the list
- `api.py:368` `/api/jobs/{id}`: `"result": project_analysis(job["result"]) if job["method"] in ("analyze", "check-and-escalate") and job["result"] else job["result"]`
- `api.py:523` `/api/batch/{id}`: same pattern per job result
- `api.py:546` `/api/compare`: project analyze-method results AFTER comparison returns

**Step 3: Apply projection in worker.py**

For webhook and callback dispatch:
- `worker.py:139` `_fire_callback`: if the result is Method 2, project before embedding in payload
- `worker.py:162` `_dispatch_webhook`: same

For check-and-escalate dispatch:
- `worker.py:90`: project `report` before embedding in the composite return dict

**Step 4: Run tests**

Run: `python -m pytest tests/test_api_projection.py -v`
Expected: ALL PASS

**Step 5: Full regression check**

Run: `python -m pytest -q tests/test_contracts.py tests/test_agents.py tests/test_orchestrator.py tests/test_integration_m2.py tests/test_config.py tests/test_projection.py tests/test_api_projection.py`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add src/huginn_muninn/api.py src/huginn_muninn/worker.py tests/test_api_projection.py
git commit -m "feat(api): apply AnalysisResponse projection at all 10 serialization boundaries"
```

---

### Task 6: Fix webhook secret prefix leak

**Files:**
- Modify: `src/huginn_muninn/api.py:405,414` (replace secret truncation)

**Step 1: Write failing test**

In `tests/test_api_projection.py` or a dedicated webhook test file:

```python
def test_list_webhooks_does_not_expose_secret_prefix(self):
    # After creating a webhook, list_webhooks should return
    # "secret_configured": True, not any portion of the secret.
    # ... (using TestClient)
    for wh in response.json():
        assert "secret" not in wh or wh.get("secret_configured") is True
```

**Step 2: Fix in api.py**

Replace `wh["secret"] = wh["secret"][:8] + "..."` with:
```python
wh.pop("secret", None)
wh["secret_configured"] = True
```

At both `api.py:405` (list_webhooks) and `api.py:414` (get_webhook).

Note: `create_webhook` at `api.py:398` should still return the full secret once on creation (the only time the caller can read it).

**Step 3: Run tests, commit**

```bash
git commit -m "fix(api): replace webhook secret prefix leak with secret_configured boolean"
```

---

### Task 7: Add OpenAPI Field descriptions for advisory fields

**Files:**
- Modify: `src/huginn_muninn/contracts.py` (5 Field descriptions)

**Step 1: Add Field(description=...) to the 5 advisory fields**

In `BridgeOutput`:
- `communication_posture`: Add `description="ADVISORY ONLY. Selects communicative register for downstream human communicators. Must not be used as an automated routing gate, content-moderation signal, or input to automated decisions with legal or similarly significant effect on individuals without human review. See GDPR Art. 22, EU AI Act Annex III."`
- `pattern_density_warning`: Add `description="Structural warning about the claim content. Not a moderation signal. Operators using this in automated pipelines must comply with applicable transparency obligations."`
- `vacuum_filled_by`: Add `description="Narrative pattern description only. Never names publishers, individuals, or organisations. Schema-level scrubber enforces this constraint."`
- `prebunking_note`: Update `Field(default="", max_length=500, description="Technique-recognition cue. Not a new factual assertion. One sentence maximum.")` 

In `SubClaim`:
- `verification_priority`: Add `description="Triage priority for human verification workflow. Not a legal, clinical, or regulatory determination. Internal analytical signal only."`

**Step 2: Verify OpenAPI schema includes descriptions**

Run the FastAPI app briefly and check `/docs` or use:
```python
from huginn_muninn.contracts import BridgeOutput
print(BridgeOutput.model_json_schema())
```
Verify the `description` fields appear in the JSON schema output.

**Step 3: Commit**

```bash
git commit -m "docs(contracts): add OpenAPI advisory descriptions to 5 regulated fields"
```

---

### Task 8: Wire Sprint 2 Bridge fields into CLI renderer

**Files:**
- Modify: `src/huginn_muninn/cli.py:252-267` (_print_analysis bridge section)

**Step 1: Write a CLI rendering test**

Use Click's `CliRunner` to invoke `huginn analyze --json-output` with a mocked pipeline and verify the 4 fields appear. Also test the pretty-print path.

**Step 2: Add Bridge field rendering after the existing bridge section**

After `cli.py:267` (the socratic_dialogue rendering), add:

```python
        # Sprint 3 PR 1: Sprint 2 Bridge scoped diagnostics
        posture = bridge.get("communication_posture", "direct_correction")
        if posture != "direct_correction":
            click.echo(f"  POSTURE: {posture.replace('_', ' ').title()}")
        if bridge.get("pattern_density_warning"):
            click.echo("  WARNING: High pattern density detected in claim structure")
        vacuum = bridge.get("vacuum_filled_by", "")
        if vacuum and vacuum != "[scope:redacted-named-entity]":
            click.echo(f"  VACUUM FILLED BY: {vacuum}")
        prebunk = bridge.get("prebunking_note", "")
        if prebunk and prebunk != "[scope:redacted-named-entity]":
            click.echo(f"  PREBUNKING NOTE: {prebunk}")
```

**Step 3: For `--json-output` path, apply projection**

In the `analyze` command's JSON output branch (around `cli.py:220`), wrap:
```python
from huginn_muninn.projection import project_analysis
# ...
if json_output:
    projected = project_analysis(result)
    click.echo(json.dumps(projected, indent=2))
```

**Step 4: Run tests, commit**

```bash
git commit -m "feat(cli): wire Sprint 2 Bridge fields into terminal output + JSON projection"
```

---

### Task 9: Add operator documentation to README

**Files:**
- Modify: `README.md` (add Operator Configuration section)

**Step 1: Add section**

After the existing "Scoped Diagnostics (v0.8.0)" section, add:

```markdown
### Operator Configuration (v0.9.0)

**Field Suppression**: Operators can suppress sensitive Bridge diagnostic fields from all API responses, webhooks, and callbacks:

```bash
export HUGINN_SUPPRESS_FIELDS="vacuum_filled_by,prebunking_note"
```

Valid suppressible fields: `communication_posture`, `pattern_density_warning`, `vacuum_filled_by`, `prebunking_note`. Suppressed fields are replaced with safe defaults in all external responses. The `suppressed_fields` array in every response discloses which fields were suppressed (Charter Commitment 5: transparent uncertainty).

**Important**: `HUGINN_SUPPRESS_FIELDS` is an operator control mechanism, not a standalone compliance control. Operators deploying under UK OSA, GDPR, or equivalent frameworks must implement their own audit logging recording which fields were suppressed, when, and why. Suppression takes effect at process startup; changes require restart.

**Known limitation**: Field suppression does not prevent the Adversarial Auditor from referencing suppressed content in `AuditFinding.description`. Full Auditor-description suppression is planned for a future release.
```

**Step 2: Commit**

```bash
git commit -m "docs(readme): add operator field-suppression configuration guide"
```

---

### Task 10: Update CHANGELOG + full regression + sync to public repo

**Files:**
- Modify: `CHANGELOG.md` (add 0.9.0 entry)
- All test files for final regression

**Step 1: Add CHANGELOG entry**

Add a `## [0.9.0] - 2026-04-12 -- "External Surface Hardening"` entry documenting: AnalysisResponse envelope, 10-boundary projection, operator field suppression, CLI wiring, OpenAPI advisory descriptions, webhook secret fix, orchestrator normalized return.

**Step 2: Run the full test suite**

Run: `python -m pytest -q -m "not e2e"`
Expected: ALL PASS, zero errors, zero failures

**Step 3: Sync to public repo and verify**

Copy all modified files to `C:/LocalAgent/github/huginn-muninn/`, run tests there, commit, push.

**Step 4: Final commit**

```bash
git commit -m "feat: Sprint 3 PR 1 -- Response Projection + CLI Wiring (v0.9.0)"
```

---

## Execution Order Summary

| Task | What | Risk | Est. Tests |
|------|------|------|-----------|
| 1 | pytest-httpx baseline | Low | +22 |
| 2 | suppressed_fields config | Low | +9 |
| 3 | AnalysisResponse envelope | Medium | +9 |
| 4 | projection.py + orchestrator normalize | Medium | +5 |
| 5 | 10-boundary projection (the big one) | High | +10 |
| 6 | Webhook secret fix | Low | +1 |
| 7 | OpenAPI Field descriptions | Low | +0 |
| 8 | CLI renderer wiring | Low | +2 |
| 9 | README operator docs | Low | +0 |
| 10 | CHANGELOG + regression + sync | Low | +0 |

**Total new tests**: ~58
**Commits**: 10 atomic commits following TDD RED-GREEN discipline
**Zero-regression constraints**: All 16 enforced by test suite
