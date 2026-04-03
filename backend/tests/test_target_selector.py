"""I5 — Target Selector tests."""
import random
import pytest
from targets.models.target_entity import TargetEntity
from targets.target_selector import TargetSelector, VALID_MODES


def _targets(n=3, hp=1000.0) -> list[TargetEntity]:
    return [TargetEntity(f"t{i}", max_health=hp, position_index=i) for i in range(n)]


sel = TargetSelector()


class TestModeCorrectness:
    def test_nearest_returns_lowest_position(self):
        ts = _targets(3)
        result = sel.select("nearest", ts)
        assert result[0].position_index == 0

    def test_lowest_health(self):
        ts = _targets(3)
        ts[1].apply_damage(600.0)   # t1 has 400 HP
        result = sel.select("lowest_health", ts)
        assert result[0].target_id == "t1"

    def test_highest_health(self):
        ts = _targets(3)
        ts[0].apply_damage(500.0)   # t0 has 500 HP; t1,t2 have 1000
        result = sel.select("highest_health", ts)
        assert result[0].current_health == 1000.0

    def test_all_targets_returns_all(self):
        ts = _targets(4)
        result = sel.select("all_targets", ts)
        assert len(result) == 4

    def test_random_returns_one(self):
        ts = _targets(5)
        rng = random.Random(42)
        result = sel.select("random", ts, rng=rng)
        assert len(result) == 1


class TestSelectionDistribution:
    def test_random_covers_all_targets_over_many_trials(self):
        ts = _targets(3)
        rng = random.Random(0)
        seen = set()
        for _ in range(100):
            seen.add(sel.select("random", ts, rng=rng)[0].target_id)
        assert len(seen) == 3


class TestEdgeCases:
    def test_single_target_nearest(self):
        t = TargetEntity("only", max_health=1000.0)
        result = sel.select("nearest", [t])
        assert result[0].target_id == "only"

    def test_empty_pool_raises(self):
        with pytest.raises(ValueError, match="No alive targets"):
            sel.select("nearest", [])

    def test_dead_targets_excluded(self):
        ts = _targets(2)
        ts[0].apply_damage(1000.0)
        result = sel.select("all_targets", ts)
        assert len(result) == 1
        assert result[0].target_id == "t1"

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown selection mode"):
            sel.select("blaster", _targets(1))
