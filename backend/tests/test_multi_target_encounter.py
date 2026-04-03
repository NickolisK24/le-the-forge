"""I12 — Multi-Target Encounter Engine tests."""
import pytest
from targets.target_templates import elite_pack, single_boss, mob_swarm
from state.multi_target_state import MultiTargetState
from app.services.multi_target_encounter import MultiTargetEncounterEngine


def _run(manager, base_damage=10000.0, distribution="full_aoe",
         selection_mode="all_targets", max_duration=30.0):
    state = MultiTargetState(manager=manager)
    return MultiTargetEncounterEngine().run(
        state=state,
        base_damage=base_damage,
        distribution=distribution,
        selection_mode=selection_mode,
        max_duration=max_duration,
    )


class TestFullEncounterSimulation:
    def test_single_boss_clears(self):
        result = _run(single_boss(1000.0), base_damage=5000.0)
        assert result.cleared is True
        assert result.total_kills == 1

    def test_elite_pack_all_killed(self):
        result = _run(elite_pack(3, 500.0), base_damage=5000.0)
        assert result.cleared is True
        assert result.total_kills == 3

    def test_not_cleared_within_timeout(self):
        # Huge HP, tiny damage → won't clear in time
        result = _run(single_boss(1e12), base_damage=1.0, max_duration=1.0)
        assert result.cleared is False
        assert result.time_to_clear is None


class TestMultiTargetCompletion:
    def test_damage_events_logged(self):
        result = _run(single_boss(100.0), base_damage=5000.0)
        assert len(result.damage_events) > 0

    def test_metrics_populated(self):
        result = _run(elite_pack(2, 200.0), base_damage=5000.0)
        assert result.metrics["total_kills"] == 2
        assert result.metrics["time_to_clear"] is not None

    def test_split_distribution_reduces_per_target_damage(self):
        # split_damage with 2 targets: each gets half
        result = _run(elite_pack(2, 1000.0), base_damage=5000.0,
                      distribution="split_damage")
        assert result.cleared is True
