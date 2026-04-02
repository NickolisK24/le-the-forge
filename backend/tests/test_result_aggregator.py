"""Tests for encounter result aggregator (Step 105)."""

import math
import pytest
from encounter.result_aggregator import AggregatedResult, aggregate_results
from encounter.state_machine import EncounterRunResult


def _result(damage, time=10.0, killed=1, casts=50, dt=0, all_dead=True):
    return EncounterRunResult(
        total_damage=damage, elapsed_time=time, ticks_simulated=100,
        all_enemies_dead=all_dead, enemies_killed=killed,
        total_casts=casts, downtime_ticks=dt, active_phase_id=None,
    )


class TestAggregateResults:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            aggregate_results([])

    def test_single_result(self):
        agg = aggregate_results([_result(1000.0)])
        assert agg.run_count == 1
        assert agg.total_damage_avg == pytest.approx(1000.0)
        assert agg.total_damage_min == pytest.approx(1000.0)
        assert agg.total_damage_max == pytest.approx(1000.0)
        assert agg.total_damage_std == pytest.approx(0.0)

    def test_average_correct(self):
        agg = aggregate_results([_result(100.0), _result(200.0), _result(300.0)])
        assert agg.total_damage_avg == pytest.approx(200.0)

    def test_min_max_correct(self):
        agg = aggregate_results([_result(100.0), _result(500.0), _result(300.0)])
        assert agg.total_damage_min == pytest.approx(100.0)
        assert agg.total_damage_max == pytest.approx(500.0)

    def test_std_correct(self):
        # values [100, 300] -> mean=200, std=100
        agg = aggregate_results([_result(100.0), _result(300.0)])
        assert agg.total_damage_std == pytest.approx(100.0)

    def test_elapsed_time_avg(self):
        agg = aggregate_results([_result(100.0, time=5.0), _result(100.0, time=15.0)])
        assert agg.elapsed_time_avg == pytest.approx(10.0)

    def test_dps_avg(self):
        # 1000 dmg / 10s = 100 dps
        agg = aggregate_results([_result(1000.0, time=10.0)])
        assert agg.average_dps_avg == pytest.approx(100.0)

    def test_kills_avg(self):
        agg = aggregate_results([_result(100.0, killed=1), _result(100.0, killed=3)])
        assert agg.kills_avg == pytest.approx(2.0)

    def test_casts_avg(self):
        agg = aggregate_results([_result(100.0, casts=40), _result(100.0, casts=60)])
        assert agg.total_casts_avg == pytest.approx(50.0)

    def test_downtime_avg(self):
        agg = aggregate_results([_result(100.0, dt=10), _result(100.0, dt=20)])
        assert agg.downtime_ticks_avg == pytest.approx(15.0)

    def test_all_killed_rate_full(self):
        agg = aggregate_results([_result(100.0, all_dead=True)] * 5)
        assert agg.all_killed_rate == pytest.approx(1.0)

    def test_all_killed_rate_partial(self):
        results = [_result(100.0, all_dead=True)] * 3 + [_result(100.0, all_dead=False)] * 2
        agg = aggregate_results(results)
        assert agg.all_killed_rate == pytest.approx(0.6)

    def test_all_killed_rate_zero(self):
        agg = aggregate_results([_result(100.0, all_dead=False)] * 3)
        assert agg.all_killed_rate == pytest.approx(0.0)

    def test_run_count(self):
        agg = aggregate_results([_result(100.0)] * 7)
        assert agg.run_count == 7
