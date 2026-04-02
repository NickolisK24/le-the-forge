"""
Profiling utilities — measure execution speed and generate timing metrics.

Three entry points:

  Timer (context manager)
      Captures the wall-clock duration of an arbitrary code block.
          with Timer() as t:
              expensive_operation()
          print(t.elapsed_ms)

  profile_call(fn, *args, n=100, **kwargs) -> ProfilerResult
      Runs fn(*args, **kwargs) n times and returns aggregate statistics.
      Use for micro-benchmarking calculator functions or engine hot paths.

  _compute_stats(samples_ms) -> ProfilerResult
      Internal function exposed for testing: converts a list of millisecond
      samples into a ProfilerResult without running any timed code.

All functions are pure timing utilities: no Flask context, no I/O, no logging.
Use the existing ``timed`` decorator in app.utils.logging for structured
per-call logging in production code.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Timer — context manager for single-block timing
# ---------------------------------------------------------------------------

class Timer:
    """
    Context manager that records the wall-clock duration of a code block.

    Attributes:
        elapsed_ms: Duration in milliseconds, set on __exit__.

    Usage:
        with Timer() as t:
            result = some_function()
        print(f"took {t.elapsed_ms:.2f} ms")
    """

    def __init__(self) -> None:
        self.elapsed_ms: float = 0.0
        self._t0: float = 0.0

    def __enter__(self) -> "Timer":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        self.elapsed_ms = (time.perf_counter() - self._t0) * 1000.0


# ---------------------------------------------------------------------------
# ProfilerResult — aggregate timing statistics
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProfilerResult:
    """
    Aggregate timing statistics from profiling N calls to a function.

    All duration values are in milliseconds.
    Percentiles use nearest-rank interpolation on the sorted sample list.
    """

    n:        int
    mean_ms:  float
    min_ms:   float
    max_ms:   float
    p50_ms:   float   # median
    p95_ms:   float
    p99_ms:   float
    total_ms: float


# ---------------------------------------------------------------------------
# Internal stats computation (exposed for testing)
# ---------------------------------------------------------------------------

def _percentile(sorted_samples: list[float], pct: float) -> float:
    """
    Nearest-rank percentile from a pre-sorted sample list.

    pct in [0, 100]. Returns sorted_samples[0] for empty lists.
    """
    if not sorted_samples:
        return 0.0
    rank = max(0, int(len(sorted_samples) * pct / 100.0) - 1)
    return sorted_samples[min(rank, len(sorted_samples) - 1)]


def _compute_stats(samples_ms: list[float]) -> ProfilerResult:
    """
    Convert a list of millisecond timings into a ProfilerResult.

    Sorts the samples internally — the input order does not matter.
    Raises ValueError if samples_ms is empty.
    """
    if not samples_ms:
        raise ValueError("_compute_stats: samples_ms must not be empty")

    s = sorted(samples_ms)
    n = len(s)
    total = sum(s)
    return ProfilerResult(
        n=n,
        mean_ms=total / n,
        min_ms=s[0],
        max_ms=s[-1],
        p50_ms=_percentile(s, 50),
        p95_ms=_percentile(s, 95),
        p99_ms=_percentile(s, 99),
        total_ms=total,
    )


# ---------------------------------------------------------------------------
# profile_call — benchmark a callable over N runs
# ---------------------------------------------------------------------------

def profile_call(fn, *args, n: int = 100, **kwargs) -> ProfilerResult:
    """
    Run fn(*args, **kwargs) n times and return aggregate timing statistics.

    Use for micro-benchmarking calculator functions or engine hot paths.
    The function's return value is discarded; only timing is recorded.

    Example:
        from app.engines.combat_engine import calculate_dps
        result = profile_call(calculate_dps, stats, "Fireball", 20, n=1000)
        print(f"mean={result.mean_ms:.3f}ms  p99={result.p99_ms:.3f}ms")
    """
    if n < 1:
        raise ValueError(f"profile_call: n must be >= 1, got {n}")

    samples: list[float] = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        samples.append((time.perf_counter() - t0) * 1000.0)

    return _compute_stats(samples)
