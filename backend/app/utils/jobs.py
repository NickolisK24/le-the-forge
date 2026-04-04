"""
Lightweight background job system using Python's ThreadPoolExecutor + Redis.

Jobs are submitted from a Flask request context and run in a thread pool.
State is persisted in Redis so any process can poll status.

Usage
-----
from app.utils.jobs import enqueue, get_status

# Enqueue work and return immediately
job_id = enqueue(expensive_fn, arg1, kwarg=value)

# Client polls
status = get_status(job_id)
# {"id": "a1b2c3d4", "status": "done", "result": {...}, "error": null}
"""

import uuid
import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Optional

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="forge-job")
_JOB_TTL = 3600  # 1 hour


def _job_key(job_id: str) -> str:
    return f"forge:job:{job_id}"


def _store(client, job_id: str, payload: dict) -> None:
    client.setex(_job_key(job_id), _JOB_TTL, json.dumps(payload, default=str))


def enqueue(fn: Callable, *args, **kwargs) -> str:
    """
    Submit fn(*args, **kwargs) to the thread pool.

    Must be called from within a Flask request context so we can capture
    the current application object for the worker thread.

    Returns
    -------
    job_id : str
        Short hex ID that clients use to poll /api/jobs/<job_id>.
    """
    from flask import current_app
    from app.utils.cache import _get_client

    app = current_app._get_current_object()
    job_id = uuid.uuid4().hex[:8]

    try:
        client = _get_client()
        _store(client, job_id, {
            "id": job_id,
            "status": "pending",
            "created_at": time.time(),
            "finished_at": None,
            "result": None,
            "error": None,
        })
    except Exception:
        pass

    def _run() -> None:
        from app.utils.cache import _get_client as _c
        try:
            redis_client = _c()
        except Exception:
            redis_client = None

        def _save(payload: dict) -> None:
            if redis_client:
                try:
                    _store(redis_client, job_id, payload)
                except Exception:
                    pass

        _save({
            "id": job_id,
            "status": "running",
            "created_at": time.time(),
            "finished_at": None,
            "result": None,
            "error": None,
        })

        with app.app_context():
            try:
                result = fn(*args, **kwargs)
                _save({
                    "id": job_id,
                    "status": "done",
                    "created_at": time.time(),
                    "finished_at": time.time(),
                    "result": result,
                    "error": None,
                })
            except Exception as exc:
                _save({
                    "id": job_id,
                    "status": "error",
                    "created_at": time.time(),
                    "finished_at": time.time(),
                    "result": None,
                    "error": str(exc),
                })

    _executor.submit(_run)
    return job_id


def get_status(job_id: str) -> Optional[dict]:
    """Return job state dict or None if the job_id is unknown."""
    from app.utils.cache import _get_client
    try:
        raw = _get_client().get(_job_key(job_id))
        return json.loads(raw) if raw else None
    except Exception:
        return None
