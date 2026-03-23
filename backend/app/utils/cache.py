"""
Redis caching utilities for The Forge.

Usage
-----
# One-off get/set
from app.utils.cache import get, set, delete_pattern

# Route decorator
from app.utils.cache import cached_route

@ref_bp.get("/classes")
@cached_route("ref:classes", ttl=86400)
def get_classes():
    ...

# Invalidate all build-list keys
delete_pattern("forge:builds:list:*")
"""

import json
import hashlib
import functools
from typing import Any, Callable, Optional

import redis as redis_lib

_client: Optional[redis_lib.Redis] = None


def _get_client() -> redis_lib.Redis:
    """Return a shared Redis client, creating it on first use."""
    global _client
    if _client is None:
        from flask import current_app
        url = current_app.config["REDIS_URL"]
        _client = redis_lib.from_url(url, decode_responses=True, socket_connect_timeout=2)
    return _client


def get(key: str) -> Optional[Any]:
    try:
        raw = _get_client().get(key)
        return json.loads(raw) if raw is not None else None
    except Exception:
        return None


def set(key: str, value: Any, ttl: int = 300) -> None:
    try:
        _get_client().setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def delete(key: str) -> None:
    try:
        _get_client().delete(key)
    except Exception:
        pass


def delete_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Returns count deleted."""
    try:
        client = _get_client()
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception:
        return 0


def make_hash(data: Any) -> str:
    """Stable SHA-256 fingerprint of any JSON-serializable value."""
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cached_route(prefix: str, ttl: int = 300, key_suffix_fn: Callable = None):
    """
    Decorator that caches a Flask route's response payload in Redis.

    The cached key is  forge:<prefix>:<suffix>  where suffix is either
    the return value of key_suffix_fn(*args, **kwargs) or the sorted
    query-string of the current request.

    On a cache HIT the handler is not called; the response includes an
    X-Cache: HIT header.  Cache failures are silently ignored (fallback
    to live response).
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request
            from app.utils.responses import ok

            if key_suffix_fn is not None:
                suffix = key_suffix_fn(*args, **kwargs)
            else:
                qs = "&".join(f"{k}={v}" for k, v in sorted(request.args.items()))
                suffix = qs or "__empty__"

            cache_key = f"forge:{prefix}:{suffix}"

            hit = get(cache_key)
            if hit is not None:
                resp = ok(data=hit)
                resp[0].headers["X-Cache"] = "HIT"
                return resp

            resp = f(*args, **kwargs)

            # resp is a (Response, status_code) tuple from ok()
            try:
                response_obj, status_code = resp if isinstance(resp, tuple) else (resp, 200)
                if status_code == 200:
                    body = response_obj.get_json()
                    if body and body.get("data") is not None:
                        set(cache_key, body["data"], ttl)
            except Exception:
                pass

            return resp

        return wrapper
    return decorator
