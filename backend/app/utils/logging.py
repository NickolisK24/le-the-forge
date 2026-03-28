"""
Structured logging configuration for The Forge backend.

Supports two output formats controlled by the LOG_FORMAT_JSON config flag:

  LOG_FORMAT_JSON=false (default):
    [LEVEL] [timestamp] [module] message  key=value key=value ...

  LOG_FORMAT_JSON=true:
    {"timestamp": "...", "level": "INFO", "module": "...", "event": "...", "key": "value"}

Usage in any module:
    from app.utils.logging import ForgeLogger
    log = ForgeLogger(__name__)
    log.info("simulation.start", skill="Fireball", seed=42, n=10000)
"""

import json
import logging
import time
from functools import wraps


LOG_FORMAT = "%(levelname)s %(asctime)s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class JsonFormatter(logging.Formatter):
    """Emits each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": self.formatTime(record, DATE_FORMAT),
            "level": record.levelname,
            "module": record.name,
            "event": record.getMessage(),
        }
        # Merge structured fields attached by ForgeLogger
        if hasattr(record, "_structured"):
            entry.update(record._structured)
        return json.dumps(entry, default=str)


def configure_logging(app):
    """
    Attach structured logging to a Flask app.
    Called from the app factory after the app is created.

    Set LOG_FORMAT_JSON=true in config for machine-readable JSON output.
    """
    use_json = app.config.get("LOG_FORMAT_JSON", False)

    if use_json:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

    # Set level from app config, defaulting to INFO
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)

    # Configure root logger so all modules use the same format
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Suppress noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app.logger.info("Logging configured at level %s (json=%s)", level_name, use_json)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)


def _format_kv(kwargs: dict) -> str:
    """Format a dict of key-value pairs into a structured suffix string."""
    if not kwargs:
        return ""
    return "  " + "  ".join(f"{k}={v!r}" for k, v in kwargs.items())


class ForgeLogger:
    """
    Thin wrapper around logging.Logger that appends structured key=value pairs.

    In JSON mode, the key-value pairs are embedded as top-level JSON fields.
    In text mode, they are appended as key=value suffixes.

    Usage:
        log = ForgeLogger(__name__)
        log.info("simulation.start", skill="Fireball", seed=42)
    """

    def __init__(self, name: str):
        self._log = logging.getLogger(name)

    def _emit(self, level: int, event: str, kwargs: dict):
        # Attach structured data for JsonFormatter to pick up
        extra = {"_structured": kwargs} if kwargs else {}
        self._log.log(level, "%s%s", event, _format_kv(kwargs), extra=extra)

    def debug(self, event: str, **kwargs):
        self._emit(logging.DEBUG, event, kwargs)

    def info(self, event: str, **kwargs):
        self._emit(logging.INFO, event, kwargs)

    def warning(self, event: str, **kwargs):
        self._emit(logging.WARNING, event, kwargs)

    def error(self, event: str, **kwargs):
        self._emit(logging.ERROR, event, kwargs)

    def exception(self, event: str, **kwargs):
        self._log.exception("%s%s", event, _format_kv(kwargs))


def timed(event: str, logger: ForgeLogger, **extra):
    """
    Decorator that logs start/end and wall-clock duration of a function.

    Usage:
        @timed("simulation.monte_carlo", logger=log, engine="combat")
        def monte_carlo_dps(...):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            logger.info(f"{event}.start", **extra)
            t0 = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
                logger.info(f"{event}.end", duration_ms=elapsed_ms, **extra)
                return result
            except Exception as exc:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
                logger.error(f"{event}.error", duration_ms=elapsed_ms, error=str(exc), **extra)
                raise
        return wrapper
    return decorator
