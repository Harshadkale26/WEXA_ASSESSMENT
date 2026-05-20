"""Hash API keys for storage and lookup (SHA-256 hex of UTF-8 secret)."""

import hashlib


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.strip().encode("utf-8")).hexdigest()
