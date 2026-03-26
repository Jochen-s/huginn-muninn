"""Tests for webhook HMAC signing and dispatcher."""
import json
from unittest.mock import MagicMock, patch

import pytest

from huginn_muninn.webhooks import WebhookDispatcher, sign_payload, verify_signature


class TestHMAC:
    def test_sign_returns_hex(self):
        sig = sign_payload(b'{"test": 1}', "secret123")
        assert isinstance(sig, str)
        assert len(sig) == 64  # SHA-256 hex digest

    def test_verify_valid_signature(self):
        body = b'{"event": "test"}'
        secret = "mysecret"
        sig = sign_payload(body, secret)
        assert verify_signature(body, secret, sig) is True

    def test_verify_wrong_secret(self):
        body = b'{"event": "test"}'
        sig = sign_payload(body, "correct_secret")
        assert verify_signature(body, "wrong_secret", sig) is False

    def test_verify_tampered_body(self):
        secret = "mysecret"
        sig = sign_payload(b"original", secret)
        assert verify_signature(b"tampered", secret, sig) is False

    def test_roundtrip_consistency(self):
        body = b"consistent payload"
        secret = "key"
        sig1 = sign_payload(body, secret)
        sig2 = sign_payload(body, secret)
        assert sig1 == sig2

    def test_different_secrets_produce_different_sigs(self):
        body = b"payload"
        sig1 = sign_payload(body, "secret1")
        sig2 = sign_payload(body, "secret2")
        assert sig1 != sig2

    def test_empty_body(self):
        sig = sign_payload(b"", "secret")
        assert verify_signature(b"", "secret", sig) is True


class TestWebhookDispatcher:
    def test_dispatch_and_stop(self):
        db = MagicMock()
        db.get_webhooks_for_event.return_value = []
        dispatcher = WebhookDispatcher(db)
        dispatcher.dispatch("test.event", {"key": "value"})
        dispatcher.stop(timeout=2.0)
        # Should not raise; consumer processed the event

    def test_delivers_to_matching_webhooks(self):
        db = MagicMock()
        db.get_webhooks_for_event.return_value = [
            {"url": "http://example.com/hook", "secret": "s3cret"}
        ]
        dispatcher = WebhookDispatcher(db)
        with patch("huginn_muninn.webhooks.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            dispatcher.dispatch("job.completed", {"job_id": "abc"})
            dispatcher.stop(timeout=2.0)
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "X-Huginn-Signature-256" in call_kwargs.kwargs["headers"]

    def test_signature_in_header_is_valid(self):
        db = MagicMock()
        secret = "webhook_secret"
        db.get_webhooks_for_event.return_value = [
            {"url": "http://example.com/hook", "secret": secret}
        ]
        dispatcher = WebhookDispatcher(db)
        with patch("huginn_muninn.webhooks.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            dispatcher.dispatch("job.completed", {"data": "test"})
            dispatcher.stop(timeout=2.0)
        call_kwargs = mock_post.call_args
        body = call_kwargs.kwargs["content"]
        sig_header = call_kwargs.kwargs["headers"]["X-Huginn-Signature-256"]
        sig = sig_header.removeprefix("sha256=")
        assert verify_signature(body, secret, sig)

    def test_no_retry_on_4xx(self):
        db = MagicMock()
        db.get_webhooks_for_event.return_value = [
            {"url": "http://example.com/hook", "secret": "s"}
        ]
        dispatcher = WebhookDispatcher(db)
        with patch("huginn_muninn.webhooks.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=400)
            dispatcher.dispatch("job.failed", {})
            dispatcher.stop(timeout=2.0)
        assert mock_post.call_count == 1

    def test_skips_delivery_when_no_webhooks(self):
        db = MagicMock()
        db.get_webhooks_for_event.return_value = []
        dispatcher = WebhookDispatcher(db)
        with patch("huginn_muninn.webhooks.httpx.post") as mock_post:
            dispatcher.dispatch("job.completed", {})
            dispatcher.stop(timeout=2.0)
        mock_post.assert_not_called()
