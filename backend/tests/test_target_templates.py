"""I3 — Target Templates tests."""
import pytest
from targets.target_templates import single_boss, elite_pack, mob_swarm, custom, TargetSpec


class TestTemplateCreation:
    def test_single_boss_one_target(self):
        mgr = single_boss(50000.0)
        assert mgr.total_count == 1
        assert mgr.get("boss").max_health == 50000.0

    def test_elite_pack_count(self):
        mgr = elite_pack(count=4, max_health=20000.0)
        assert mgr.total_count == 4

    def test_mob_swarm_count(self):
        mgr = mob_swarm(count=8, max_health=3000.0)
        assert mgr.total_count == 8


class TestTargetCountAccuracy:
    def test_elite_default_three(self):
        mgr = elite_pack()
        assert mgr.total_count == 3

    def test_mob_default_ten(self):
        mgr = mob_swarm()
        assert mgr.total_count == 10

    def test_zero_count_raises(self):
        with pytest.raises(ValueError):
            elite_pack(count=0)


class TestHealthDistribution:
    def test_all_targets_same_hp(self):
        mgr = elite_pack(count=3, max_health=25000.0)
        hps = {t.max_health for t in mgr.all_targets()}
        assert hps == {25000.0}

    def test_custom_specs(self):
        specs = [TargetSpec("a", 1000.0, 0), TargetSpec("b", 2000.0, 1)]
        mgr = custom(specs)
        assert mgr.get("a").max_health == 1000.0
        assert mgr.get("b").max_health == 2000.0

    def test_custom_empty_raises(self):
        with pytest.raises(ValueError):
            custom([])
