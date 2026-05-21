"""HMAC-SHA256 verification for webhook ingestion payloads."""

from __future__ import annotations

import hashlib
import hmac


def compute_webhook_signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_webhook_signature(body: bytes, secret: str, header_value: str | None) -> bool:
    if not header_value or not secret:
        return False
    expected = compute_webhook_signature(body, secret)
    provided = header_value.strip()
    if provided.startswith("sha256="):
        provided_digest = provided[7:]
    else:
        provided_digest = provided
    expected_digest = expected[7:]
    return hmac.compare_digest(expected_digest, provided_digest)
