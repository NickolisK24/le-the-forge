"""
Structured logging configuration for The Forge backend.

Provides a consistent log format across engines, services, and routes:
    [LEVEL] [timestamp] [module] message  key=value key=value ...

Usage in any module:
    from app.utils.logging import get_logger
    log = get_logger(__name__)
    log.info("simulation.start", skill="Fireball", seed=42, n=10000)

In engine/service code where Flask context is not available, use get_logger().
In route code, current_app.logger remains available for request-level events.
"""

import logging
import time
from functools import wraps


LOG_FORMAT = "%(levelname)s %(asctime)s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_logging(app):
    """
    Attach structured logging to a Flask app.
    Called from the app factory after the app is created.
    """
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

    app.logger.info("Logging configured at level %s", level_name)


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

    Usage:
        log = ForgeLogger(__name__)
        log.info("simulation.start", skill="Fireball", seed=42)
        # → INFO 2026-01-01T00:00:00 [app.engines.combat_engine] simulation.start  skill='Fireball'  seed=42
    """

    def __init__(self, name: str):
        self._log = logging.getLogger(name)

    def debug(self, event: str, **kwargs):
        self._log.debug("%s%s", event, _format_kv(kwargs))

    def info(self, event: str, **kwargs):
        self._log.info("%s%s", event, _format_kv(kwargs))

    def warning(self, event: str, **kwargs):
        self._log.warning("%s%s", event, _format_kv(kwargs))

    def error(self, event: str, **kwargs):
        self._log.error("%s%s", event, _format_kv(kwargs))

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
