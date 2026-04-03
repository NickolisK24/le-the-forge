"""I6 — Multi-Target Distribution tests."""
import pytest
from targets.models.target_entity import TargetEntity
from damage.multi_target_distribution import MultiTargetDistribution, DamageEvent


def _targets(n=3, hp=1000.0) -> list[TargetEntity]:
    return [TargetEntity(f"t{i}", max_health=hp, position_index=i) for i in range(n)]


dist = MultiTargetDistribution()


class TestSingleTarget:
    def test_full_damage_to_primary(self):
        ts = _targets(3)
        evts = dist.distribute(500.0, "single_target", primary=ts[0], all_targets=ts)
        assert len(evts) == 1
        assert evts[0].damage_dealt == pytest.approx(500.0)
        assert evts[0].target_id == "t0"

    def test_no_primary_raises(self):
        with pytest.raises(ValueError):
            dist.distribute(500.0, "single_target")


class TestAoEDistribution:
    def test_full_aoe_hits_all(self):
        ts = _targets(3)
        evts = dist.distribute(300.0, "full_aoe", all_targets=ts)
        assert len(evts) == 3
        for e in evts:
            assert e.damage_dealt == pytest.approx(300.0)


class TestSplitDamage:
    def test_split_divides_equally(self):
        ts = _targets(4)
        evts = dist.distribute(400.0, "split_damage", all_targets=ts)
        assert len(evts) == 4
        for e in evts:
            assert e.damage_dealt == pytest.approx(100.0)


class TestChainBehavior:
    def test_chain_returns_empty_from_distribution(self):
        # Chain is delegated to ChainEngine; distribution returns []
        ts = _targets(3)
        evts = dist.distribute(500.0, "chain", primary=ts[0], all_targets=ts)
        assert evts == []


class TestSplashLogic:
    def test_splash_primary_full_damage(self):
        ts = _targets(3)
        evts = dist.distribute(1000.0, "splash", primary=ts[0], all_targets=ts, splash_pct=0.3)
        primary_evt = next(e for e in evts if e.target_id == "t0")
        assert primary_evt.damage_dealt == pytest.approx(1000.0)

    def test_splash_secondary_reduced(self):
        ts = _targets(3)
        evts = dist.distribute(1000.0, "splash", primary=ts[0], all_targets=ts, splash_pct=0.3)
        secondary_evts = [e for e in evts if e.target_id != "t0"]
        for e in secondary_evts:
            assert e.damage_dealt == pytest.approx(300.0)

    def test_overkill_tracked(self):
        ts = [TargetEntity("t0", max_health=100.0)]
        evts = dist.distribute(500.0, "single_target", primary=ts[0], all_targets=ts)
        assert evts[0].overkill == pytest.approx(400.0)
        assert evts[0].killed is True
