"""FastAPI REST API for Huginn & Muninn."""
from __future__ import annotations

import ipaddress
import json
import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

from huginn_muninn.batch import BatchStore
from huginn_muninn.comparison import ComparisonEngine
from huginn_muninn.config import get_settings
from huginn_muninn.db import HuginnDB
from huginn_muninn.jobs import JobStatus, JobStore
from huginn_muninn.llm import create_client, extract_json_from_response
from huginn_muninn.model_registry import ModelRegistry
from huginn_muninn.models import ClaimInput, JobRequest, VerdictOutput
from huginn_muninn.orchestrator import Orchestrator
from huginn_muninn.projection import project_analysis
from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt
from huginn_muninn.search import SearchClient
from huginn_muninn.webhooks import WebhookDispatcher
from huginn_muninn.worker import JobRunner

log = logging.getLogger(__name__)

# Static files path
_WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"


@asynccontextmanager
async def lifespan(a: FastAPI):
    settings = get_settings()
    db = HuginnDB(settings.db_path)
    client = create_client(
        provider=settings.llm_provider,
        base_url=settings.ollama_base_url,
        model=settings.default_model,
        api_key=settings.llm_api_key,
    )
    model_registry = ModelRegistry(settings.models_config_path)
    search_client = (
        SearchClient(api_key=settings.search_api_key, provider=settings.search_provider)
        if settings.search_api_key
        else None
    )
    comparison_engine = ComparisonEngine(model_registry, db)
    job_store = JobStore(max_jobs=settings.max_jobs)
    batch_store = BatchStore(job_store)
    webhook_dispatcher = WebhookDispatcher(db)
    job_runner = JobRunner(db, client, job_store, webhook_dispatcher, search_client=search_client)
    try:
        if _WEB_DIR.is_dir():
            a.state.index_html = (_WEB_DIR / "index.html").read_text()
        else:
            a.state.index_html = None
            log.warning("Web UI directory not found at %s; static files disabled", _WEB_DIR)
        a.state.db = db
        a.state.client = client
        a.state.model_registry = model_registry
        a.state.job_store = job_store
        a.state.batch_store = batch_store
        a.state.search_client = search_client
        a.state.comparison_engine = comparison_engine
        a.state.job_runner = job_runner
        a.state.webhook_dispatcher = webhook_dispatcher
        yield
    finally:
        job_runner.shutdown(wait=True)
        comparison_engine.shutdown()
        webhook_dispatcher.stop()
        if search_client:
            search_client.close()
        # Mark in-progress jobs as failed
        for job in job_store.list_jobs(limit=10000):
            if job["status"] in (JobStatus.PENDING, JobStatus.RUNNING):
                job_store.update(job["id"], status=JobStatus.FAILED, error="Server shutdown")
        client.close()
        db.close()


app = FastAPI(
    title="Huginn & Muninn",
    description="Fact-checking with Common Humanity",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Static files (web UI) -- mounted after API routes so /api/* takes priority
if _WEB_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(_WEB_DIR)), name="static")


# --- Request/Response models ---

class ClaimRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=2000)
    no_cache: bool = False
    deep_sources: bool = False


class FeedbackRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=2000)
    type: Literal["agree", "disagree", "partial", "unsure"]
    comment: str | None = Field(None, max_length=1000)


class WebhookCreateRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2000)
    events: list[str] = Field(..., min_length=1)


class WebhookUpdateRequest(BaseModel):
    active: bool | None = None
    events: list[str] | None = None


class BatchRequest(BaseModel):
    claims: list[str] = Field(..., min_length=1, max_length=50)
    method: Literal["check", "analyze", "check-and-escalate"] = "check"
    callback_url: str | None = Field(default=None, max_length=2000)
    session_id: int | None = None
    deep_sources: bool = False


class CompareRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=2000)
    models: list[str] = Field(..., min_length=2, max_length=5)
    method: Literal["check", "analyze"] = "check"
    reconcile: bool = False


class SessionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class SessionItemRequest(BaseModel):
    item_type: Literal["verdict", "analysis"]
    item_id: int


# --- Helpers ---

def _check_llm() -> dict:
    try:
        available = app.state.client.check_available()
        return {"status": "ok" if available else "unavailable", "available": available}
    except Exception as e:
        log.warning("LLM backend check failed: %s", e)
        return {"status": "unavailable", "available": False}


def _run_method1(claim: str, no_cache: bool = False) -> tuple[dict, int | None]:
    db = app.state.db
    if not no_cache:
        result = db.get_cached_verdict_with_id(claim)
        if result:
            return result

    client = app.state.client
    if not client.check_available():
        raise HTTPException(503, detail="LLM backend unavailable or model not found")

    try:
        p1_raw = client.generate(build_pass1_prompt(claim))
        p1_data = extract_json_from_response(p1_raw)
        p2_raw = client.generate(build_pass2_prompt(claim, json.dumps(p1_data)))
        p2_data = extract_json_from_response(p2_raw)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        log.error("LLM output parse error: %s", e)
        raise HTTPException(502, detail="LLM returned malformed output")

    try:
        output = VerdictOutput(claim=claim, **p2_data)
    except (ValidationError, TypeError) as e:
        log.error("LLM response schema error: %s", e)
        raise HTTPException(502, detail="LLM response did not match expected schema")

    verdict_dict = output.model_dump(mode="json")
    row_id = db.store_verdict(claim, verdict_dict)
    return verdict_dict, row_id


def _run_method2(claim: str, no_cache: bool = False) -> tuple[dict, int | None]:
    db = app.state.db
    if not no_cache:
        result = db.get_cached_analysis_with_id(claim)
        if result:
            return result

    client = app.state.client
    if not client.check_available():
        raise HTTPException(503, detail="LLM backend unavailable or model not found")
    orch = Orchestrator(client)
    result = orch.run(claim)

    row_id = db.store_analysis(claim, result)
    return result, row_id


_VALID_WEBHOOK_EVENTS = {
    "verdict.completed", "analysis.completed", "job.completed", "job.failed",
}


def _validate_webhook_events(events: list[str]) -> None:
    invalid = set(events) - _VALID_WEBHOOK_EVENTS
    if invalid:
        raise HTTPException(422, detail=f"Invalid events: {sorted(invalid)}")


def _validate_url(url: str, field: str = "url") -> None:
    """Block private/internal IPs to prevent SSRF."""
    try:
        parsed = urlparse(url)
    except ValueError:
        raise HTTPException(422, detail=f"Invalid {field}")
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(422, detail=f"{field} must use http or https")
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(422, detail=f"Invalid {field}: missing hostname")
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise HTTPException(422, detail=f"{field} must not point to a private/internal address")
    except ValueError:
        # hostname is a DNS name -- block obvious internal names
        lower = hostname.lower()
        if lower in ("localhost",) or lower.endswith(".local") or lower.endswith(".internal"):
            raise HTTPException(422, detail=f"{field} must not point to a private/internal address")


# --- Routes ---

@app.get("/api/health")
def health():
    info = _check_llm()
    if not info["available"]:
        raise HTTPException(503, detail=info)
    return info


@app.post("/api/check")
def check(req: ClaimRequest):
    try:
        ClaimInput(text=req.claim)
    except ValidationError as e:
        raise HTTPException(422, detail=str(e))
    try:
        result, verdict_id = _run_method1(req.claim, no_cache=req.no_cache)
        if verdict_id is not None:
            result["verdict_id"] = verdict_id
        return result
    except httpx.ReadTimeout:
        raise HTTPException(504, detail="LLM request timed out")
    except httpx.HTTPError as e:
        log.error("Ollama error: %s", e)
        raise HTTPException(503, detail="LLM backend error")


@app.post("/api/analyze")
def analyze(req: ClaimRequest):
    try:
        ClaimInput(text=req.claim)
    except ValidationError as e:
        raise HTTPException(422, detail=str(e))
    try:
        result, analysis_id = _run_method2(req.claim, no_cache=req.no_cache)
        if analysis_id is not None:
            result["analysis_id"] = analysis_id
        result = project_analysis(result)
        return result
    except httpx.ReadTimeout:
        raise HTTPException(504, detail="LLM request timed out")
    except httpx.HTTPError as e:
        log.error("Ollama error: %s", e)
        raise HTTPException(503, detail="LLM backend error")


@app.post("/api/check-and-escalate")
def check_and_escalate(req: ClaimRequest):
    try:
        ClaimInput(text=req.claim)
    except ValidationError as e:
        raise HTTPException(422, detail=str(e))
    try:
        verdict, verdict_id = _run_method1(req.claim, no_cache=req.no_cache)
        should_escalate = verdict.get("escalation", {}).get("should_escalate", False)
        if should_escalate:
            report, analysis_id = _run_method2(req.claim, no_cache=req.no_cache)
            report = project_analysis(report)
            return {"method_1": verdict, "method_2": report, "escalated": True,
                    "verdict_id": verdict_id, "analysis_id": analysis_id}
        return {"method_1": verdict, "escalated": False, "verdict_id": verdict_id}
    except httpx.ReadTimeout:
        raise HTTPException(504, detail="LLM request timed out")
    except httpx.HTTPError as e:
        log.error("Ollama error: %s", e)
        raise HTTPException(503, detail="LLM backend error")


@app.post("/api/feedback")
def feedback(req: FeedbackRequest):
    db = app.state.db
    cached = db.get_cached_verdict(req.claim)
    verdict = cached.get("verdict", "unknown") if cached else "unknown"
    db.store_feedback(req.claim, verdict, req.type, req.comment)
    return {"status": "recorded"}


@app.get("/api/history")
def history(limit: int = Query(default=20, ge=1, le=100)):
    db = app.state.db
    analyses = db.get_recent_analyses(limit=limit)
    projected_analyses = []
    for a in analyses:
        if "data" in a and isinstance(a["data"], dict):
            a["data"] = project_analysis(a["data"])
        projected_analyses.append(a)
    return {
        "verdicts": db.get_recent_verdicts(limit=limit),
        "analyses": projected_analyses,
    }


# --- Job endpoints ---

@app.post("/api/jobs", status_code=202)
def create_job(req: JobRequest):
    try:
        ClaimInput(text=req.claim)
    except ValidationError as e:
        raise HTTPException(422, detail=str(e))
    if req.callback_url:
        _validate_url(req.callback_url, field="callback_url")
    job_store = app.state.job_store
    job_id = job_store.create(
        claim=req.claim,
        method=req.method,
        callback_url=req.callback_url,
        session_id=req.session_id,
        deep_sources=req.deep_sources,
    )
    app.state.job_runner.submit(job_id)
    return {"job_id": job_id, "status": "pending"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = app.state.job_store.get(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    raw_result = job["result"]
    if raw_result and job["method"] in ("analyze", "check-and-escalate"):
        if job["method"] == "check-and-escalate" and isinstance(raw_result, dict) and "method_2" in raw_result:
            raw_result = dict(raw_result)
            raw_result["method_2"] = project_analysis(raw_result["method_2"])
        elif job["method"] == "analyze":
            raw_result = project_analysis(raw_result)
    return {
        "id": job["id"],
        "claim": job["claim"],
        "method": job["method"],
        "status": job["status"].value if hasattr(job["status"], "value") else job["status"],
        "result": raw_result,
        "error": job["error"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }


@app.get("/api/jobs")
def list_jobs(limit: int = Query(default=50, ge=1, le=200)):
    jobs = app.state.job_store.list_jobs(limit=limit)
    return [
        {
            "id": j["id"],
            "claim": j["claim"],
            "method": j["method"],
            "status": j["status"].value if hasattr(j["status"], "value") else j["status"],
            "created_at": j["created_at"],
        }
        for j in jobs
    ]


# --- Webhook endpoints ---

@app.post("/api/webhooks", status_code=201)
def create_webhook(req: WebhookCreateRequest):
    _validate_webhook_events(req.events)
    _validate_url(req.url, field="webhook url")
    secret = secrets.token_hex(32)
    wh_id = app.state.db.create_webhook(req.url, secret, req.events)
    return {"id": wh_id, "url": req.url, "events": req.events, "active": True, "secret": secret}


@app.get("/api/webhooks")
def list_webhooks():
    webhooks = app.state.db.list_webhooks()
    for wh in webhooks:
        # Sprint 3 PR 1 Klingon fix: never expose any portion of the
        # HMAC secret. Full secret returned once on POST creation only.
        wh.pop("secret", None)
        wh["secret_configured"] = True
    return webhooks


@app.get("/api/webhooks/{webhook_id}")
def get_webhook(webhook_id: int):
    wh = app.state.db.get_webhook(webhook_id)
    if not wh:
        raise HTTPException(404, detail="Webhook not found")
    wh.pop("secret", None)
    wh["secret_configured"] = True
    return wh


@app.patch("/api/webhooks/{webhook_id}")
def update_webhook(webhook_id: int, req: WebhookUpdateRequest):
    if req.events is not None:
        _validate_webhook_events(req.events)
    kwargs = {}
    if req.active is not None:
        kwargs["active"] = req.active
    if req.events is not None:
        kwargs["events"] = req.events
    if not kwargs:
        raise HTTPException(422, detail="No fields to update")
    wh = app.state.db.update_webhook(webhook_id, **kwargs)
    if not wh:
        raise HTTPException(404, detail="Webhook not found")
    wh.pop("secret", None)
    wh["secret_configured"] = True
    return wh


@app.delete("/api/webhooks/{webhook_id}", status_code=204)
def delete_webhook(webhook_id: int):
    deleted = app.state.db.delete_webhook(webhook_id)
    if not deleted:
        raise HTTPException(404, detail="Webhook not found")
    return Response(status_code=204)


# --- Session endpoints ---

@app.post("/api/sessions", status_code=201)
def create_session(req: SessionCreateRequest):
    session_id = app.state.db.create_session(req.name)
    return {"id": session_id, "name": req.name}


@app.get("/api/sessions")
def list_sessions():
    return app.state.db.list_sessions()


@app.get("/api/sessions/{session_id}")
def get_session(session_id: int):
    session = app.state.db.get_session(session_id)
    if not session:
        raise HTTPException(404, detail="Session not found")
    return session


@app.post("/api/sessions/{session_id}/items", status_code=201)
def add_session_item(session_id: int, req: SessionItemRequest):
    session = app.state.db.get_session(session_id)
    if not session:
        raise HTTPException(404, detail="Session not found")
    item_id = app.state.db.add_session_item(session_id, req.item_type, req.item_id)
    return {"id": item_id, "session_id": session_id, "item_type": req.item_type, "item_id": req.item_id}


# --- Batch endpoints ---

@app.post("/api/batch", status_code=202)
def create_batch(req: BatchRequest):
    settings = get_settings()
    if len(req.claims) > settings.max_batch_size:
        raise HTTPException(
            422, detail=f"Too many claims (max {settings.max_batch_size})"
        )
    for claim in req.claims:
        try:
            ClaimInput(text=claim)
        except ValidationError as e:
            raise HTTPException(422, detail=f"Invalid claim: {e}")
    if req.callback_url:
        _validate_url(req.callback_url, field="callback_url")

    job_store = app.state.job_store
    job_runner = app.state.job_runner
    job_ids = []
    for claim in req.claims:
        jid = job_store.create(
            claim=claim,
            method=req.method,
            callback_url=req.callback_url,
            session_id=req.session_id,
            deep_sources=req.deep_sources,
        )
        job_ids.append(jid)
        job_runner.submit(jid)

    batch_id = app.state.batch_store.create(job_ids, session_id=req.session_id)
    return {"batch_id": batch_id, "job_ids": job_ids, "status": "pending"}


@app.get("/api/batch/{batch_id}")
def get_batch(batch_id: str):
    batch = app.state.batch_store.get(batch_id)
    if not batch:
        raise HTTPException(404, detail="Batch not found")
    # Attach individual job results
    results = []
    for jid in batch["job_ids"]:
        job = app.state.job_store.get(jid)
        if job:
            result = job["result"]
            if result and job["method"] in ("analyze", "check-and-escalate"):
                if job["method"] == "check-and-escalate" and isinstance(result, dict) and "method_2" in result:
                    result = dict(result)
                    result["method_2"] = project_analysis(result["method_2"])
                elif job["method"] == "analyze":
                    result = project_analysis(result)
            results.append({
                "job_id": jid,
                "claim": job["claim"],
                "status": job["status"].value if hasattr(job["status"], "value") else job["status"],
                "result": result,
                "error": job["error"],
            })
    batch["results"] = results
    return batch


# --- Compare endpoints ---

@app.post("/api/compare")
def create_comparison(req: CompareRequest):
    registry = app.state.model_registry
    available = registry.list_names()
    invalid = [m for m in req.models if m not in available]
    if invalid:
        raise HTTPException(422, detail=f"Unknown models: {invalid}")
    try:
        result = app.state.comparison_engine.compare(
            claim=req.claim,
            model_names=req.models,
            method=req.method,
            reconcile=req.reconcile,
        )
        if req.method == "analyze" and isinstance(result, dict) and "results" in result:
            for model_name, analysis in result["results"].items():
                if isinstance(analysis, dict):
                    result["results"][model_name] = project_analysis(analysis)
        return result
    except Exception as e:
        log.error("Comparison failed: %s", e)
        raise HTTPException(500, detail="Comparison failed")


@app.get("/api/compare/{comparison_id}")
def get_comparison(comparison_id: int):
    result = app.state.db.get_comparison(comparison_id)
    if not result:
        raise HTTPException(404, detail="Comparison not found")
    return result


# --- Models endpoint ---

@app.get("/api/models")
def list_models():
    registry = app.state.model_registry
    return {"models": registry.list_names()}


@app.get("/")
def root():
    if app.state.index_html:
        return Response(content=app.state.index_html, media_type="text/html")
    return {"message": "Huginn & Muninn API", "docs": "/docs"}
