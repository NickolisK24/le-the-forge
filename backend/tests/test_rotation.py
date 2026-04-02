"""
Tests for Multi-Skill Rotation Support (Step 57).

Validates:
  - SkillEntry construction and validation
  - select_next: priority ordering, mana gating, cooldown gating
  - Tie-breaking by list position
  - RotationEngine: add, trigger, tick, next_skill
  - Cooldown correctly decrements and unblocks skill
  - Mana prevents selection even when cooldown ready
  - No skills ready → None returned
"""

import pytest
from app.domain.rotation import SkillEntry, RotationEngine, select_next


# ---------------------------------------------------------------------------
# SkillEntry construction
# ---------------------------------------------------------------------------

class TestSkillEntryConstruction:
    def test_basic_construction(self):
        e = SkillEntry("fireball", mana_cost=30.0, cooldown=2.0, priority=1)
        assert e.name == "fireball"
        assert e.mana_cost == pytest.approx(30.0)
        assert e.cooldown == pytest.approx(2.0)
        assert e.priority == 1

    def test_defaults(self):
        e = SkillEntry("basic_attack", mana_cost=0.0)
        assert e.cooldown == pytest.approx(0.0)
        assert e.priority == 1

    def test_negative_mana_cost_raises(self):
        with pytest.raises(ValueError, match="mana_cost"):
            SkillEntry("skill", mana_cost=-1.0)

    def test_negative_cooldown_raises(self):
        with pytest.raises(ValueError, match="cooldown"):
            SkillEntry("skill", mana_cost=0.0, cooldown=-0.5)

    def test_zero_priority_raises(self):
        with pytest.raises(ValueError, match="priority"):
            SkillEntry("skill", mana_cost=0.0, priority=0)

    def test_negative_priority_raises(self):
        with pytest.raises(ValueError, match="priority"):
            SkillEntry("skill", mana_cost=0.0, priority=-1)


# ---------------------------------------------------------------------------
# select_next — pure function
# ---------------------------------------------------------------------------

class TestSelectNext:
    def _make(self, name, mana_cost=10.0, cooldown=0.0, priority=1):
        return SkillEntry(name, mana_cost=mana_cost, cooldown=cooldown, priority=priority)

    def test_single_ready_skill_selected(self):
        e = self._make("fireball")
        assert select_next([e], current_mana=50.0) is e

    def test_returns_none_with_empty_list(self):
        assert select_next([], current_mana=100.0) is None

    def test_mana_insufficient_returns_none(self):
        e = self._make("fireball", mana_cost=50.0)
        assert select_next([e], current_mana=40.0) is None

    def test_exact_mana_selects_skill(self):
        e = self._make("fireball", mana_cost=50.0)
        assert select_next([e], current_mana=50.0) is e

    def test_cooldown_blocks_skill(self):
        e = self._make("fireball")
        assert select_next([e], current_mana=100.0, cooldown_remaining={"fireball": 1.5}) is None

    def test_expired_cooldown_selects_skill(self):
        e = self._make("fireball")
        assert select_next([e], current_mana=100.0, cooldown_remaining={"fireball": 0.0}) is e

    def test_priority_order_lower_wins(self):
        e1 = self._make("high_prio", priority=1)
        e2 = self._make("low_prio", priority=2)
        result = select_next([e2, e1], current_mana=100.0)
        assert result is e1

    def test_tie_broken_by_position(self):
        e1 = self._make("first", priority=2)
        e2 = self._make("second", priority=2)
        result = select_next([e1, e2], current_mana=100.0)
        assert result is e1

    def test_highest_prio_on_cooldown_falls_back(self):
        e1 = self._make("best", mana_cost=10.0, priority=1)
        e2 = self._make("fallback", mana_cost=5.0, priority=2)
        result = select_next(
            [e1, e2],
            current_mana=100.0,
            cooldown_remaining={"best": 2.0},
        )
        assert result is e2

    def test_all_on_cooldown_returns_none(self):
        e1 = self._make("a")
        e2 = self._make("b")
        result = select_next(
            [e1, e2],
            current_mana=100.0,
            cooldown_remaining={"a": 1.0, "b": 0.5},
        )
        assert result is None

    def test_none_cooldown_dict_treated_as_empty(self):
        e = self._make("fireball")
        result = select_next([e], current_mana=100.0, cooldown_remaining=None)
        assert result is e

    def test_mixed_mana_and_cooldown_constraints(self):
        # e1: wrong mana; e2: on cooldown; e3: ready
        e1 = self._make("expensive", mana_cost=200.0, priority=1)
        e2 = self._make("cooldown_skill", mana_cost=10.0, priority=2)
        e3 = self._make("ready", mana_cost=10.0, priority=3)
        result = select_next(
            [e1, e2, e3],
            current_mana=50.0,
            cooldown_remaining={"cooldown_skill": 1.0},
        )
        assert result is e3


# ---------------------------------------------------------------------------
# RotationEngine
# ---------------------------------------------------------------------------

class TestRotationEngineAdd:
    def test_add_single_skill(self):
        engine = RotationEngine()
        e = SkillEntry("fireball", mana_cost=20.0)
        engine.add(e)
        assert e in engine.entries

    def test_duplicate_name_raises(self):
        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=20.0))
        with pytest.raises(ValueError, match="fireball"):
            engine.add(SkillEntry("fireball", mana_cost=10.0))

    def test_initial_cooldown_is_zero(self):
        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=20.0, cooldown=3.0))
        assert engine.cooldowns["fireball"] == pytest.approx(0.0)


class TestRotationEngineTrigger:
    def test_trigger_sets_cooldown(self):
        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=20.0, cooldown=2.0))
        engine.trigger("fireball")
        assert engine.cooldowns["fireball"] == pytest.approx(2.0)

    def test_trigger_unknown_skill_raises(self):
        engine = RotationEngine()
        with pytest.raises(KeyError, match="unknown"):
            engine.trigger("unknown")

    def test_zero_cooldown_skill_ready_immediately_after_trigger(self):
        engine = RotationEngine()
        engine.add(SkillEntry("spam", mana_cost=5.0, cooldown=0.0))
        engine.trigger("spam")
        assert engine.cooldowns["spam"] == pytest.approx(0.0)
        assert engine.next_skill(current_mana=50.0) is not None


class TestRotationEngineTick:
    def test_tick_reduces_cooldown(self):
        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=20.0, cooldown=3.0))
        engine.trigger("fireball")
        engine.tick(1.0)
        assert engine.cooldowns["fireball"] == pytest.approx(2.0)

    def test_tick_clamps_at_zero(self):
        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=20.0, cooldown=1.0))
        engine.trigger("fireball")
        engine.tick(5.0)
        assert engine.cooldowns["fireball"] == pytest.approx(0.0)

    def test_negative_delta_raises(self):
        engine = RotationEngine()
        with pytest.raises(ValueError, match="delta"):
            engine.tick(-1.0)


class TestRotationEngineNextSkill:
    def test_skill_ready_on_first_call(self):
        engine = RotationEngine()
        engine.add(SkillEntry("blast", mana_cost=10.0, cooldown=1.0))
        result = engine.next_skill(current_mana=50.0)
        assert result is not None
        assert result.name == "blast"

    def test_skill_blocked_after_trigger_until_tick(self):
        engine = RotationEngine()
        engine.add(SkillEntry("blast", mana_cost=10.0, cooldown=2.0))
        engine.trigger("blast")
        assert engine.next_skill(current_mana=50.0) is None
        engine.tick(2.0)
        assert engine.next_skill(current_mana=50.0) is not None

    def test_priority_respected(self):
        engine = RotationEngine()
        engine.add(SkillEntry("prio1", mana_cost=10.0, priority=1))
        engine.add(SkillEntry("prio2", mana_cost=10.0, priority=2))
        assert engine.next_skill(current_mana=50.0).name == "prio1"

    def test_fallback_when_best_on_cooldown(self):
        engine = RotationEngine()
        engine.add(SkillEntry("prio1", mana_cost=10.0, cooldown=3.0, priority=1))
        engine.add(SkillEntry("prio2", mana_cost=5.0,  cooldown=0.0, priority=2))
        engine.trigger("prio1")
        result = engine.next_skill(current_mana=50.0)
        assert result.name == "prio2"

    def test_no_affordable_skill_returns_none(self):
        engine = RotationEngine()
        engine.add(SkillEntry("expensive", mana_cost=100.0))
        assert engine.next_skill(current_mana=50.0) is None

    def test_full_rotation_cycle(self):
        # Simulate: cast prio1, wait cooldown, cast again
        engine = RotationEngine()
        engine.add(SkillEntry("prio1", mana_cost=20.0, cooldown=2.0, priority=1))
        engine.add(SkillEntry("filler", mana_cost=5.0,  cooldown=0.0, priority=2))

        # First cast: prio1
        skill = engine.next_skill(current_mana=100.0)
        assert skill.name == "prio1"
        engine.trigger("prio1")

        # While prio1 on cooldown: filler fires
        engine.tick(0.5)
        skill = engine.next_skill(current_mana=100.0)
        assert skill.name == "filler"

        # After cooldown expires: prio1 fires again
        engine.tick(1.6)  # total 2.1s > 2.0s cooldown
        skill = engine.next_skill(current_mana=100.0)
        assert skill.name == "prio1"
