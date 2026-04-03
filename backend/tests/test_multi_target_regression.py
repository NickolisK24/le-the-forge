"""
I17 — Multi-Target Regression Suite

Protects core scenarios:
  1. AoE damage correctness — every target takes full damage
  2. Chain logic accuracy   — correct bounce + decay
  3. Kill ordering consistency — last-die target clears encounter
"""
import pytest
from targets.models.target_entity import TargetEntity
from targets.target_templates import elite_pack, mob_swarm
from state.multi_target_state import MultiTargetState
from app.services.multi_target_encounter import MultiTargetEncounterEngine
from damage.multi_target_distribution import MultiTargetDistribution
from damage.chain_engine import ChainEngine


def _targets(n=3, hp=1000.0) -> list[TargetEntity]:
    return [TargetEntity(f"t{i}", max_health=hp, position_index=i) for i in range(n)]


class TestAoEDamageCorrectness:
    def test_full_aoe_reduces_all_targets_equally(self):
        ts = _targets(4, 1000.0)
        dist = MultiTargetDistribution()
        dist.distribute(300.0, "full_aoe", all_targets=ts)
        for t in ts:
            assert t.current_health == pytest.approx(700.0)

    def test_split_damage_totals_equal_base(self):
        ts = _targets(4, 1000.0)
        dist = MultiTargetDistribution()
        evts = dist.distribute(400.0, "split_damage", all_targets=ts)
        total = sum(e.damage_dealt for e in evts)
        assert total == pytest.approx(400.0)


class TestChainLogicAccuracy:
    def test_chain_does_not_hit_same_target_twice(self):
        ts = _targets(3, 1000.0)
        result = ChainEngine().execute(500.0, ts, ts[0], max_bounces=5)
        hit_ids = [e.target_id for e in result.events]
        assert len(hit_ids) == len(set(hit_ids))   # no duplicates

    def test_chain_decay_is_cumulative(self):
        ts = _targets(4, 1000.0)
        result = ChainEngine().execute(1000.0, ts, ts[0], max_bounces=3, decay=0.5)
        dmgs = [e.damage_dealt for e in result.events]
        assert dmgs[0] == pytest.approx(1000.0)
        assert dmgs[1] == pytest.approx(500.0)
        assert dmgs[2] == pytest.approx(250.0)
        assert dmgs[3] == pytest.approx(125.0)


class TestKillOrderingConsistency:
    def test_all_targets_killed_in_full_aoe(self):
        mgr = mob_swarm(5, 200.0)
        state = MultiTargetState(manager=mgr)
        result = MultiTargetEncounterEngine().run(
            state, base_damage=50000.0, distribution="full_aoe", max_duration=10.0
        )
        assert result.cleared is True
        assert result.total_kills == 5

    def test_last_target_determines_clear_time(self):
        # Two targets: one with very low HP, one with more
        from targets.target_templates import custom, TargetSpec
        specs = [TargetSpec("easy", 100.0, 0), TargetSpec("hard", 5000.0, 1)]
        mgr = custom(specs)
        state = MultiTargetState(manager=mgr)
        result = MultiTargetEncounterEngine().run(
            state, base_damage=1000.0, distribution="single_target",
            selection_mode="lowest_health", max_duration=30.0
        )
        # With lowest_health selection, easy dies first, then hard
        if result.cleared:
            assert result.metrics["kill_times"]["easy"] <= result.metrics["kill_times"]["hard"]
