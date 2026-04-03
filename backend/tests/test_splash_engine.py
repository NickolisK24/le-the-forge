"""I8 — Splash Engine tests."""
import pytest
from targets.models.target_entity import TargetEntity
from damage.splash_engine import SplashEngine


def _targets(positions: list[int], hp=1000.0) -> list[TargetEntity]:
    return [TargetEntity(f"t{i}", max_health=hp, position_index=p) for i, p in enumerate(positions)]


engine = SplashEngine()


class TestSplashRadiusCoverage:
    def test_only_targets_within_radius_hit(self):
        ts = _targets([0, 1, 2, 5, 10])   # positions 0,1,2 close; 5,10 far
        primary = ts[0]   # position 0, radius=2
        result = engine.execute(1000.0, ts, primary, radius=2)
        hit_ids = {e.target_id for e in result.events}
        assert "t0" in hit_ids   # pos 0 distance=0
        assert "t1" in hit_ids   # pos 1 distance=1
        assert "t2" in hit_ids   # pos 2 distance=2
        assert "t3" not in hit_ids  # pos 5 distance=5 > 2
        assert "t4" not in hit_ids  # pos 10 distance=10 > 2

    def test_zero_radius_hits_only_primary(self):
        ts = _targets([0, 1, 2])
        result = engine.execute(1000.0, ts, ts[0], radius=0)
        assert result.targets_hit == 1


class TestDamageFalloff:
    def test_primary_takes_full_damage(self):
        ts = _targets([0, 1])
        result = engine.execute(1000.0, ts, ts[0], radius=2, falloff=0.5)
        primary_evt = next(e for e in result.events if e.target_id == "t0")
        assert primary_evt.damage_dealt == pytest.approx(1000.0)

    def test_falloff_reduces_with_distance(self):
        ts = _targets([0, 1, 2])
        result = engine.execute(1000.0, ts, ts[0], radius=2, falloff=0.5)
        by_id = {e.target_id: e.damage_dealt for e in result.events}
        # distance 0 → factor 1.0 → 1000
        # distance 1 → factor 1 - 0.5*(1/2) = 0.75 → 750
        # distance 2 → factor 1 - 0.5*(2/2) = 0.5 → 500
        assert by_id["t0"] == pytest.approx(1000.0)
        assert by_id["t1"] == pytest.approx(750.0)
        assert by_id["t2"] == pytest.approx(500.0)

    def test_invalid_falloff_raises(self):
        ts = _targets([0, 1])
        with pytest.raises(ValueError):
            engine.execute(1000.0, ts, ts[0], falloff=1.5)
