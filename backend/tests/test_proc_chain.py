"""
Tests for Proc Chain System (Step 68).
"""

import pytest
from app.domain.proc_chain import (
    MAX_CHAIN_DEPTH,
    ProcEvent,
    ProcLink,
    ProcResult,
    resolve_chain,
)
from app.domain.triggers import (
    Trigger,
    TriggerCondition,
    TriggerContext,
    TriggerEffect,
    TriggerType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hit_trigger(effect=TriggerEffect.APPLY_BLEED, source="") -> Trigger:
    return Trigger(
        trigger_type=TriggerType.ON_HIT,
        effect=effect,
        condition=TriggerCondition(),
        source=source,
    )

def cast_trigger(effect=TriggerEffect.GAIN_BUFF, source="") -> Trigger:
    return Trigger(
        trigger_type=TriggerType.ON_CAST,
        effect=effect,
        condition=TriggerCondition(),
        source=source,
    )

def ctx() -> TriggerContext:
    return TriggerContext(current_mana=100.0, max_mana=100.0)


# ---------------------------------------------------------------------------
# Basic resolution
# ---------------------------------------------------------------------------

class TestResolveChainBasic:
    def test_empty_chain_returns_empty(self):
        result = resolve_chain([], ProcEvent.ON_HIT, ctx())
        assert result == []

    def test_no_matching_link_returns_empty(self):
        link = ProcLink(ProcEvent.ON_CAST, (cast_trigger(),))
        result = resolve_chain([link], ProcEvent.ON_HIT, ctx())
        assert result == []

    def test_matching_link_fires_trigger(self):
        t = hit_trigger()
        link = ProcLink(ProcEvent.ON_HIT, (t,))
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx())
        assert len(results) == 1
        assert results[0].trigger is t
        assert results[0].depth == 0

    def test_multiple_triggers_in_link_all_fire(self):
        t1 = hit_trigger(TriggerEffect.APPLY_BLEED,  source="a")
        t2 = hit_trigger(TriggerEffect.APPLY_POISON, source="b")
        link = ProcLink(ProcEvent.ON_HIT, (t1, t2))
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx())
        assert len(results) == 2

    def test_depth_recorded_correctly(self):
        t = hit_trigger()
        link = ProcLink(ProcEvent.ON_HIT, (t,))
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx())
        assert results[0].depth == 0


# ---------------------------------------------------------------------------
# Chain linking
# ---------------------------------------------------------------------------

class TestProcChainLinking:
    def test_chain_continues_to_next_event(self):
        t1 = hit_trigger(source="first")
        t2 = cast_trigger(source="second")
        link1 = ProcLink(ProcEvent.ON_HIT,  (t1,), next_event=ProcEvent.ON_CAST)
        link2 = ProcLink(ProcEvent.ON_CAST, (t2,))

        results = resolve_chain([link1, link2], ProcEvent.ON_HIT, ctx())
        assert len(results) == 2
        assert results[0].depth == 0
        assert results[1].depth == 1

    def test_chain_does_not_continue_if_no_triggers_fire(self):
        # Trigger with 0% chance → never fires → chain should not continue
        t1 = Trigger(
            trigger_type=TriggerType.ON_HIT,
            effect=TriggerEffect.APPLY_BLEED,
            condition=TriggerCondition(chance_pct=0.0),
        )
        t2 = cast_trigger(source="should_not_fire")
        link1 = ProcLink(ProcEvent.ON_HIT,  (t1,), next_event=ProcEvent.ON_CAST)
        link2 = ProcLink(ProcEvent.ON_CAST, (t2,))

        results = resolve_chain([link1, link2], ProcEvent.ON_HIT, ctx(),
                                rng_roll=50.0)
        assert results == []

    def test_three_level_chain(self):
        t1 = hit_trigger(source="L1")
        t2 = cast_trigger(source="L2")
        t3 = hit_trigger(TriggerEffect.APPLY_SHOCK, source="L3")

        link1 = ProcLink(ProcEvent.ON_HIT,  (t1,), next_event=ProcEvent.ON_CAST)
        link2 = ProcLink(ProcEvent.ON_CAST, (t2,), next_event=ProcEvent.ON_HIT)
        link3 = ProcLink(ProcEvent.ON_HIT,  (t3,))

        results = resolve_chain([link1, link2, link3], ProcEvent.ON_HIT, ctx())
        depths = [r.depth for r in results]
        assert 0 in depths
        assert 1 in depths
        assert 2 in depths


# ---------------------------------------------------------------------------
# Depth limit
# ---------------------------------------------------------------------------

class TestDepthLimit:
    def test_chain_stops_at_max_depth(self):
        # Create a self-referencing chain that would loop forever
        t = hit_trigger()
        link = ProcLink(ProcEvent.ON_HIT, (t,), next_event=ProcEvent.ON_HIT)
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx())
        # Should fire at depths 0..MAX_CHAIN_DEPTH, then stop
        depths = [r.depth for r in results]
        assert max(depths) == MAX_CHAIN_DEPTH
        assert len(results) == MAX_CHAIN_DEPTH + 1


# ---------------------------------------------------------------------------
# Chance roll
# ---------------------------------------------------------------------------

class TestChanceRoll:
    def test_50pct_chance_fires_below_threshold(self):
        t = Trigger(
            trigger_type=TriggerType.ON_HIT,
            effect=TriggerEffect.APPLY_BLEED,
            condition=TriggerCondition(chance_pct=50.0),
        )
        link = ProcLink(ProcEvent.ON_HIT, (t,))
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx(), rng_roll=49.9)
        assert len(results) == 1

    def test_50pct_chance_blocked_above_threshold(self):
        t = Trigger(
            trigger_type=TriggerType.ON_HIT,
            effect=TriggerEffect.APPLY_BLEED,
            condition=TriggerCondition(chance_pct=50.0),
        )
        link = ProcLink(ProcEvent.ON_HIT, (t,))
        results = resolve_chain([link], ProcEvent.ON_HIT, ctx(), rng_roll=50.1)
        assert results == []
