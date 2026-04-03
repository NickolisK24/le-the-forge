"""I7 — Chain Engine tests."""
import pytest
from targets.models.target_entity import TargetEntity
from damage.chain_engine import ChainEngine


def _targets(n=4, hp=1000.0) -> list[TargetEntity]:
    return [TargetEntity(f"t{i}", max_health=hp, position_index=i) for i in range(n)]


engine = ChainEngine()


class TestBounceCountAccuracy:
    def test_bounces_limited_to_max(self):
        ts = _targets(4)
        result = engine.execute(1000.0, ts, ts[0], max_bounces=2)
        assert result.bounces == 2

    def test_bounces_capped_by_available_targets(self):
        ts = _targets(2)   # only 1 additional target
        result = engine.execute(1000.0, ts, ts[0], max_bounces=5)
        assert result.bounces == 1   # only 1 other target to hit

    def test_zero_bounces_hits_only_primary(self):
        ts = _targets(3)
        result = engine.execute(500.0, ts, ts[0], max_bounces=0)
        assert result.bounces == 0
        assert len(result.events) == 1


class TestDamageReductionPerBounce:
    def test_decay_applied(self):
        ts = _targets(3)
        result = engine.execute(1000.0, ts, ts[0], max_bounces=2, decay=0.5)
        dmgs = [e.damage_dealt for e in result.events]
        assert dmgs[0] == pytest.approx(1000.0)
        assert dmgs[1] == pytest.approx(500.0)
        assert dmgs[2] == pytest.approx(250.0)

    def test_final_damage_correct(self):
        ts = _targets(3)
        result = engine.execute(1000.0, ts, ts[0], max_bounces=1, decay=0.7)
        assert result.final_damage == pytest.approx(700.0)


class TestStopConditionValidation:
    def test_stops_when_all_hit(self):
        ts = _targets(2)
        result = engine.execute(500.0, ts, ts[0], max_bounces=10)
        assert len(result.events) == 2   # only 2 unique targets

    def test_invalid_decay_raises(self):
        ts = _targets(2)
        with pytest.raises(ValueError):
            engine.execute(500.0, ts, ts[0], decay=0.0)

    def test_negative_bounces_raises(self):
        ts = _targets(2)
        with pytest.raises(ValueError):
            engine.execute(500.0, ts, ts[0], max_bounces=-1)
