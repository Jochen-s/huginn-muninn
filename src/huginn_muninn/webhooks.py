"""Webhook HMAC signing and dispatching."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import queue
import threading
import time
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from huginn_muninn.db import HuginnDB

log = logging.getLogger(__name__)


def sign_payload(body: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 hex digest for a payload."""
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def verify_signature(body: bytes, secret: str, signature: str) -> bool:
    """Verify HMAC-SHA256 signature using constant-time comparison."""
    expected = sign_payload(body, secret)
    return hmac.compare_digest(expected, signature)


class WebhookDispatcher:
    """Queue-based webhook delivery with retry."""

    _RETRY_DELAYS = (1, 4, 16)

    def __init__(self, db: HuginnDB):
        self._db = db
        self._queue: queue.Queue[tuple[str, dict] | None] = queue.Queue()
        self._thread = threading.Thread(target=self._consumer, daemon=True)
        self._running = True
        self._thread.start()

    def dispatch(self, event: str, payload: dict) -> None:
        """Queue an event for delivery to registered webhooks."""
        if self._running:
            self._queue.put((event, payload))

    def stop(self, timeout: float = 5.0) -> None:
        """Signal consumer to stop and wait for drain."""
        self._running = False
        self._queue.put(None)
        self._thread.join(timeout=timeout)

    def _consumer(self) -> None:
        while True:
            item = self._queue.get()
            if item is None:
                break
            event, payload = item
            try:
                self._deliver(event, payload)
            except Exception:
                log.exception("Webhook delivery error for event %s", event)

    def _deliver(self, event: str, payload: dict) -> None:
        webhooks = self._db.get_webhooks_for_event(event)
        body = json.dumps({"event": event, "data": payload}).encode()
        for wh in webhooks:
            sig = sign_payload(body, wh["secret"])
            headers = {
                "Content-Type": "application/json",
                "X-Huginn-Event": event,
                "X-Huginn-Signature-256": f"sha256={sig}",
            }
            self._post_with_retry(wh["url"], body, headers)

    def _post_with_retry(
        self, url: str, body: bytes, headers: dict
    ) -> None:
        for attempt, delay in enumerate(self._RETRY_DELAYS):
            try:
                resp = httpx.post(
                    url, content=body, headers=headers, timeout=10.0
                )
                if resp.status_code < 400:
                    return
                if 400 <= resp.status_code < 500:
                    log.warning(
                        "Webhook %s returned %d, not retrying",
                        url, resp.status_code,
                    )
                    return
            except httpx.HTTPError as e:
                log.warning(
                    "Webhook %s attempt %d failed: %s", url, attempt + 1, e
                )
            if attempt < len(self._RETRY_DELAYS) - 1:
                time.sleep(delay)
        log.error("Webhook %s failed after %d attempts", url, len(self._RETRY_DELAYS))
