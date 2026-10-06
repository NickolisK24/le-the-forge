"""Content hashing, byte-for-byte compatible with R1 (last-epoch-data r1_snapshot.py).

``content_sha256`` = sha256 of canonical JSON (sorted keys, compact separators,
ASCII) after removing volatile capture keys. It must equal the
``content_sha256`` that the R1 run manifest records for the same file; a test
pins this against an R1-computed value.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

# Must stay identical to r1_snapshot.VOLATILE_KEYS.
VOLATILE_KEYS = frozenset({
    "generated_at", "generated_on", "extracted_at", "timestamp", "run_started_at",
    "created_at", "generation_time", "installPath", "install_path",
})


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip_volatile(v) for k, v in value.items() if k not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [strip_volatile(v) for v in value]
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha256_of(data: Any) -> str:
    return sha256_bytes(canonical_json(strip_volatile(data)).encode("utf-8"))


def content_sha256_file(path: Path) -> str:
    return content_sha256_of(json.loads(path.read_text(encoding="utf-8")))


def document_hash(doc: dict, exclude_key: str) -> str:
    """sha256 of a manifest's canonical JSON without its own hash field."""
    return sha256_bytes(canonical_json({k: v for k, v in doc.items() if k != exclude_key}).encode("utf-8"))
