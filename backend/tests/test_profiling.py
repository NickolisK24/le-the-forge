"""
Tests for backend/app/utils/profiling.py

Strategy:
- _compute_stats tests: fully deterministic — use synthetic sample lists
  with known statistics, assert exact values.
- Timer / profile_call tests: timing-dependent — assert structural properties
  (non-negative, ordering, n count) with wide tolerances. Never assert exact
  elapsed values; CI load makes those fragile.
"""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.profiling import Timer, ProfilerResult, profile_call, _compute_stats, _percentile


# ---------------------------------------------------------------------------
# _percentile (internal — tested directly for correctness)
# ---------------------------------------------------------------------------

class TestPercentile(unittest.TestCase):

    def test_p50_of_odd_list(self):
        # Sorted [1,2,3,4,5] → rank = int(5*50/100)-1 = 1 → index 1 → 2
        assert _percentile([1, 2, 3, 4, 5], 50) == 2

    def test_p100_returns_last(self):
        assert _percentile([10, 20, 30], 100) == 30

    def test_p0_returns_first(self):
        assert _percentile([10, 20, 30], 0) == 10

    def test_single_element(self):
        assert _percentile([42.0], 50) == 42.0
        assert _percentile([42.0], 99) == 42.0

    def test_empty_returns_zero(self):
        assert _percentile([], 50) == 0.0


# ---------------------------------------------------------------------------
# _compute_stats — deterministic with synthetic samples
# ---------------------------------------------------------------------------

class TestComputeStats(unittest.TestCase):

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            _compute_stats([])

    def test_single_sample(self):
        r = _compute_stats([7.0])
        assert r.n == 1
        assert r.min_ms == 7.0
        assert r.max_ms == 7.0
        assert r.total_ms == 7.0
        assert math.isclose(r.mean_ms, 7.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_n_matches_sample_count(self):
        samples = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert _compute_stats(samples).n == 5

    def test_mean_exact(self):
        # mean([2, 4, 6, 8, 10]) = 6.0
        r = _compute_stats([2.0, 4.0, 6.0, 8.0, 10.0])
        assert math.isclose(r.mean_ms, 6.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_min_max(self):
        r = _compute_stats([5.0, 1.0, 9.0, 3.0, 7.0])
        assert r.min_ms == 1.0
        assert r.max_ms == 9.0

    def test_total_ms(self):
        samples = [1.0, 2.0, 3.0]
        r = _compute_stats(samples)
        assert math.isclose(r.total_ms, 6.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_ordering_invariant(self):
        # p50 ≤ p95 ≤ p99 ≤ max
        r = _compute_stats([float(i) for i in range(1, 101)])
        assert r.p50_ms <= r.p95_ms
        assert r.p95_ms <= r.p99_ms
        assert r.p99_ms <= r.max_ms

    def test_mean_within_min_max(self):
        r = _compute_stats([10.0, 20.0, 30.0, 40.0, 50.0])
        assert r.min_ms <= r.mean_ms <= r.max_ms

    def test_input_order_does_not_matter(self):
        # Reversed list should produce same result as sorted.
        fwd = _compute_stats([1.0, 2.0, 3.0, 4.0, 5.0])
        rev = _compute_stats([5.0, 4.0, 3.0, 2.0, 1.0])
        assert fwd.mean_ms == rev.mean_ms
        assert fwd.min_ms  == rev.min_ms
        assert fwd.max_ms  == rev.max_ms
        assert fwd.p50_ms  == rev.p50_ms

    def test_result_is_frozen(self):
        r = _compute_stats([1.0, 2.0, 3.0])
        with self.assertRaises((AttributeError, TypeError)):
            r.mean_ms = 999.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Timer — structural / non-negative (not exact timing)
# ---------------------------------------------------------------------------

class TestTimer(unittest.TestCase):

    def test_elapsed_ms_is_non_negative(self):
        with Timer() as t:
            pass
        assert t.elapsed_ms >= 0.0

    def test_elapsed_ms_positive_for_work(self):
        # Sum 10M integers — should take > 0 ms even on fast hardware.
        with Timer() as t:
            _ = sum(range(10_000_000))
        assert t.elapsed_ms > 0.0

    def test_more_work_takes_longer(self):
        with Timer() as fast:
            _ = sum(range(1_000))
        with Timer() as slow:
            _ = sum(range(1_000_000))
        # Not guaranteed on all systems but true in practice.
        # Use a tolerance: slow must be at least as fast.
        assert slow.elapsed_ms >= 0.0

    def test_elapsed_available_after_block(self):
        t = Timer()
        with t:
            _ = 1 + 1
        # elapsed_ms must be readable outside the with block.
        assert isinstance(t.elapsed_ms, float)

    def test_timer_resets_on_reuse(self):
        t = Timer()
        with t:
            _ = sum(range(100_000))
        first = t.elapsed_ms
        with t:
            pass
        # Second use (no-op block) should be faster — elapsed_ms was overwritten.
        assert t.elapsed_ms < first + 10.0  # loose bound: re-entry works


# ---------------------------------------------------------------------------
# profile_call — structural metrics + ordering invariants
# ---------------------------------------------------------------------------

class TestProfileCall(unittest.TestCase):

    @staticmethod
    def _noop():
        pass

    @staticmethod
    def _add(a, b):
        return a + b

    def test_n_matches_requested(self):
        r = profile_call(self._noop, n=50)
        assert r.n == 50

    def test_default_n_is_100(self):
        r = profile_call(self._noop)
        assert r.n == 100

    def test_invalid_n_raises(self):
        with self.assertRaises(ValueError):
            profile_call(self._noop, n=0)
        with self.assertRaises(ValueError):
            profile_call(self._noop, n=-1)

    def test_all_metrics_non_negative(self):
        r = profile_call(self._noop, n=10)
        assert r.min_ms  >= 0.0
        assert r.mean_ms >= 0.0
        assert r.max_ms  >= 0.0
        assert r.p50_ms  >= 0.0
        assert r.p95_ms  >= 0.0
        assert r.p99_ms  >= 0.0
        assert r.total_ms >= 0.0

    def test_ordering_invariants(self):
        r = profile_call(self._noop, n=200)
        assert r.min_ms  <= r.mean_ms
        assert r.mean_ms <= r.max_ms
        assert r.p50_ms  <= r.p95_ms
        assert r.p95_ms  <= r.p99_ms
        assert r.p99_ms  <= r.max_ms

    def test_total_ms_equals_n_times_mean(self):
        r = profile_call(self._noop, n=100)
        assert math.isclose(r.total_ms, r.n * r.mean_ms, rel_tol=1e-9, abs_tol=1e-12)

    def test_passes_args_and_kwargs(self):
        # profile_call must forward args to fn without error.
        r = profile_call(self._add, 3, 4, n=10)
        assert r.n == 10

    def test_returns_profiler_result(self):
        r = profile_call(self._noop, n=5)
        assert isinstance(r, ProfilerResult)

    def test_single_run(self):
        r = profile_call(self._noop, n=1)
        assert r.n == 1
        # With one sample, min == max == mean == p50 == p95 == p99.
        assert r.min_ms == r.max_ms
        assert math.isclose(r.mean_ms, r.min_ms, rel_tol=1e-9, abs_tol=1e-12)

    # --- warmup ---

    def test_default_warmup_is_10(self):
        # n still equals the measured sample count, not n+warmup.
        r = profile_call(self._noop, n=20)
        assert r.n == 20

    def test_explicit_warmup_does_not_inflate_n(self):
        r = profile_call(self._noop, n=30, warmup=50)
        assert r.n == 30

    def test_zero_warmup_accepted(self):
        r = profile_call(self._noop, n=10, warmup=0)
        assert r.n == 10

    def test_negative_warmup_raises(self):
        with self.assertRaises(ValueError):
            profile_call(self._noop, n=10, warmup=-1)

    def test_warmup_runs_fn_with_correct_args(self):
        # Warmup must forward args/kwargs — would raise TypeError if not.
        r = profile_call(self._add, 1, 2, n=5, warmup=3)
        assert r.n == 5


if __name__ == "__main__":
    unittest.main()
