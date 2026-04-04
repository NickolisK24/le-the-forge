"""K13 — Spatial metrics tests."""
import pytest
from metrics.spatial_metrics import SpatialMetrics


class TestRecording:
    def test_initial_state_zeros(self):
        m = SpatialMetrics()
        assert m.total_hits == 0
        assert m.total_misses == 0
        assert m.total_projectiles_spawned == 0
        assert m.total_damage == pytest.approx(0.0)

    def test_record_spawn(self):
        m = SpatialMetrics()
        m.record_projectile_spawn()
        m.record_projectile_spawn()
        assert m.total_projectiles_spawned == 2

    def test_record_hit_increments(self):
        m = SpatialMetrics()
        m.record_hit(damage=50.0)
        assert m.total_hits == 1
        assert m.total_damage == pytest.approx(50.0)

    def test_record_miss_increments(self):
        m = SpatialMetrics()
        m.record_miss()
        assert m.total_misses == 1

    def test_hit_rate_computed(self):
        m = SpatialMetrics()
        m.record_hit(damage=10.0)
        m.record_hit(damage=10.0)
        m.record_miss()
        assert m.hit_rate == pytest.approx(2 / 3)

    def test_hit_rate_no_shots(self):
        m = SpatialMetrics()
        assert m.hit_rate == pytest.approx(0.0)

    def test_crit_rate(self):
        m = SpatialMetrics()
        m.record_hit(damage=100.0, is_critical=True)
        m.record_hit(damage=100.0, is_critical=False)
        assert m.crit_rate == pytest.approx(0.5)

    def test_crit_rate_no_hits(self):
        assert SpatialMetrics().crit_rate == pytest.approx(0.0)

    def test_pierce_tracking(self):
        m = SpatialMetrics()
        m.record_hit(damage=10.0, pierced=True)
        m.record_hit(damage=10.0, pierced=True)
        assert m.total_pierce_count == 2

    def test_chain_bounce_tracking(self):
        m = SpatialMetrics()
        m.record_chain_bounce()
        m.record_chain_bounce()
        assert m.total_chain_bounces == 2

    def test_travel_distance_max(self):
        m = SpatialMetrics()
        m.record_projectile_expired(5.0)
        m.record_projectile_expired(12.0)
        m.record_projectile_expired(3.0)
        assert m.max_travel_distance == pytest.approx(12.0)

    def test_travel_distance_avg(self):
        m = SpatialMetrics()
        m.record_projectile_expired(4.0)
        m.record_projectile_expired(8.0)
        assert m.avg_travel_distance == pytest.approx(6.0)

    def test_aoe_area_accumulates(self):
        m = SpatialMetrics()
        m.record_aoe(area=10.0)
        m.record_aoe(area=20.0)
        assert m.total_aoe_area == pytest.approx(30.0)

    def test_overkill_tracked(self):
        m = SpatialMetrics()
        m.record_hit(damage=50.0, overkill=30.0)
        assert m.total_overkill == pytest.approx(30.0)


class TestSummary:
    def test_summary_keys(self):
        m = SpatialMetrics()
        s = m.summary()
        for key in ["hits", "misses", "hit_rate", "crit_rate", "total_damage",
                    "pierce_count", "chain_bounces", "projectiles_spawned"]:
            assert key in s

    def test_reset_clears_all(self):
        m = SpatialMetrics()
        m.record_hit(damage=100.0, is_critical=True)
        m.record_projectile_spawn()
        m.reset()
        assert m.total_hits == 0
        assert m.total_projectiles_spawned == 0
