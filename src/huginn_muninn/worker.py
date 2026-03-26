"""Background job runner using a bounded thread pool."""
from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import httpx

from huginn_muninn.jobs import JobStatus

if TYPE_CHECKING:
    from huginn_muninn.db import HuginnDB
    from huginn_muninn.jobs import JobStore
    from huginn_muninn.llm import LLMClient
    from huginn_muninn.search import SearchClient
    from huginn_muninn.webhooks import WebhookDispatcher

log = logging.getLogger(__name__)


class JobRunner:
    """Runs jobs in a bounded thread pool."""

    def __init__(
        self,
        db: HuginnDB,
        client: LLMClient,
        job_store: JobStore,
        webhook_dispatcher: WebhookDispatcher | None = None,
        max_workers: int = 4,
        search_client: SearchClient | None = None,
    ):
        self._db = db
        self._client = client
        self._job_store = job_store
        self._webhook_dispatcher = webhook_dispatcher
        self._search_client = search_client
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="job-worker"
        )

    def submit(self, job_id: str) -> None:
        """Submit a job to the thread pool."""
        self._executor.submit(self._run, job_id)

    def shutdown(self, wait: bool = False) -> None:
        """Shut down the thread pool."""
        self._executor.shutdown(wait=wait, cancel_futures=True)

    def _run(self, job_id: str) -> None:
        job = self._job_store.get(job_id)
        if not job:
            return

        self._job_store.update(job_id, status=JobStatus.RUNNING)

        try:
            result = self._dispatch(job)
            self._job_store.update(
                job_id, status=JobStatus.COMPLETED, result=result
            )
            self._fire_callback(job, result, error=None)
            self._dispatch_webhook(job, result, error=None)
        except Exception as e:
            error_msg = str(e)[:500]
            log.error("Job %s failed: %s", job_id, error_msg)
            self._job_store.update(
                job_id, status=JobStatus.FAILED, error=error_msg
            )
            self._fire_callback(job, result=None, error=error_msg)
            self._dispatch_webhook(job, result=None, error=error_msg)

    def _dispatch(self, job: dict) -> dict:
        """Route to the correct analysis method."""
        claim = job["claim"]
        method = job["method"]
        deep_sources = job.get("deep_sources", False)

        if method == "check":
            return self._run_method1(claim, deep_sources=deep_sources)
        elif method == "analyze":
            return self._run_method2(claim)
        elif method == "check-and-escalate":
            verdict = self._run_method1(claim, deep_sources=deep_sources)
            should_escalate = verdict.get("escalation", {}).get("should_escalate", False)
            if should_escalate:
                report = self._run_method2(claim)
                return {"method_1": verdict, "method_2": report, "escalated": True}
            return {"method_1": verdict, "escalated": False}
        else:
            raise ValueError(f"Unknown method: {method}")

    def _run_method1(self, claim: str, deep_sources: bool = False) -> dict:
        from huginn_muninn.llm import extract_json_from_response
        from huginn_muninn.models import VerdictOutput
        from huginn_muninn.prompt import build_pass1_prompt, build_pass2_prompt

        p1_raw = self._client.generate(build_pass1_prompt(claim))
        p1_data = extract_json_from_response(p1_raw)
        p2_raw = self._client.generate(build_pass2_prompt(claim, json.dumps(p1_data)))
        p2_data = extract_json_from_response(p2_raw)

        if deep_sources and self._search_client:
            from huginn_muninn.search import enrich_evidence
            if "evidence_for" in p2_data:
                p2_data["evidence_for"] = enrich_evidence(
                    p2_data["evidence_for"], self._search_client
                )
            if "evidence_against" in p2_data:
                p2_data["evidence_against"] = enrich_evidence(
                    p2_data["evidence_against"], self._search_client
                )

        output = VerdictOutput(claim=claim, **p2_data)
        verdict_dict = output.model_dump(mode="json")
        self._db.store_verdict(claim, verdict_dict)
        return verdict_dict

    def _run_method2(self, claim: str) -> dict:
        from huginn_muninn.orchestrator import Orchestrator

        orch = Orchestrator(self._client)
        result = orch.run(claim)
        self._db.store_analysis(claim, result)
        return result

    def _fire_callback(
        self, job: dict, result: dict | None, error: str | None
    ) -> None:
        """POST result to the job's callback_url if set."""
        url = job.get("callback_url")
        if not url:
            return
        payload = {
            "job_id": job["id"],
            "status": "completed" if error is None else "failed",
            "result": result,
            "error": error,
        }
        try:
            httpx.post(url, json=payload, timeout=10.0)
        except Exception as e:
            log.warning("Callback to %s failed: %s", url, e)

    def _dispatch_webhook(
        self, job: dict, result: dict | None, error: str | None
    ) -> None:
        """Fire webhook events for job completion/failure."""
        if not self._webhook_dispatcher:
            return
        payload = {
            "job_id": job["id"],
            "claim": job["claim"],
            "method": job["method"],
        }
        if error:
            payload["error"] = error
            self._webhook_dispatcher.dispatch("job.failed", payload)
        else:
            payload["result"] = result
            self._webhook_dispatcher.dispatch("job.completed", payload)
            event_map = {"check": "verdict.completed", "analyze": "analysis.completed"}
            specific_event = event_map.get(job["method"])
            if specific_event:
                self._webhook_dispatcher.dispatch(specific_event, payload)
