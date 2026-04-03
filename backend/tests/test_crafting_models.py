"""
Tests for Phase P crafting models:
  - CraftState / AffixState  (craft_state.py)
  - AffixTier                (affix_tier.py)
  - CraftAction              (craft_action.py)
  - BisTarget                (bis_target.py)
"""
from __future__ import annotations

import pytest

from crafting.models.craft_state import AffixState, CraftState
from crafting.models.affix_tier import AffixTier, TIER_WEIGHTS
from crafting.models.craft_action import ActionType, CraftAction
from crafting.models.bis_target import AffixRequirement, BisTarget


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state(
    fp: int = 50,
    instability: int = 0,
    affixes=None,
    is_fractured: bool = False,
    fracture_type: str | None = None,
    craft_count: int = 0,
    metadata: dict | None = None,
) -> CraftState:
    return CraftState(
        item_id="item-001",
        item_name="Iron Helm",
        item_class="helm",
        forging_potential=fp,
        instability=instability,
        affixes=affixes if affixes is not None else [],
        is_fractured=is_fractured,
        fracture_type=fracture_type,
        craft_count=craft_count,
        metadata=metadata if metadata is not None else {},
    )


def make_affix(affix_id: str, current_tier: int = 1, max_tier: int = 7, locked: bool = False) -> AffixState:
    return AffixState(affix_id=affix_id, current_tier=current_tier, max_tier=max_tier, locked=locked)


# ---------------------------------------------------------------------------
# AffixState tests
# ---------------------------------------------------------------------------

class TestAffixState:
    def test_locked_default_false(self):
        a = AffixState(affix_id="flat_life", current_tier=1, max_tier=7)
        assert a.locked is False

    def test_fields_accessible(self):
        a = AffixState(affix_id="fire_res", current_tier=3, max_tier=5, locked=True)
        assert a.affix_id == "fire_res"
        assert a.current_tier == 3
        assert a.max_tier == 5
        assert a.locked is True

    def test_locked_can_be_set_true(self):
        a = AffixState(affix_id="cold_res", current_tier=2, max_tier=7, locked=True)
        assert a.locked is True

    def test_affix_id_is_string(self):
        a = AffixState(affix_id="mana_regen", current_tier=1, max_tier=7)
        assert isinstance(a.affix_id, str)

    def test_default_locked_false_via_positional(self):
        a = AffixState("hp_percent", 4, 7)
        assert a.locked is False


# ---------------------------------------------------------------------------
# CraftState tests – default fields
# ---------------------------------------------------------------------------

class TestCraftStateDefaults:
    def test_affixes_default_empty_list(self):
        state = make_state()
        assert state.affixes == []

    def test_is_fractured_default_false(self):
        state = make_state()
        assert state.is_fractured is False

    def test_fracture_type_default_none(self):
        state = make_state()
        assert state.fracture_type is None

    def test_craft_count_default_zero(self):
        state = make_state()
        assert state.craft_count == 0

    def test_metadata_default_empty_dict(self):
        state = make_state()
        assert state.metadata == {}

    def test_forging_potential_stored(self):
        state = make_state(fp=75)
        assert state.forging_potential == 75

    def test_instability_stored(self):
        state = make_state(instability=20)
        assert state.instability == 20

    def test_item_fields_stored(self):
        state = make_state()
        assert state.item_id == "item-001"
        assert state.item_name == "Iron Helm"
        assert state.item_class == "helm"


# ---------------------------------------------------------------------------
# CraftState.affix_count
# ---------------------------------------------------------------------------

class TestCraftStateAffixCount:
    def test_affix_count_empty(self):
        state = make_state()
        assert state.affix_count == 0

    def test_affix_count_one(self):
        state = make_state(affixes=[make_affix("flat_life")])
        assert state.affix_count == 1

    def test_affix_count_four(self):
        affixes = [make_affix(f"affix_{i}") for i in range(4)]
        state = make_state(affixes=affixes)
        assert state.affix_count == 4

    def test_affix_count_reflects_mutation(self):
        state = make_state()
        assert state.affix_count == 0
        state.affixes.append(make_affix("new"))
        assert state.affix_count == 1


# ---------------------------------------------------------------------------
# CraftState.can_craft
# ---------------------------------------------------------------------------

class TestCraftStateCanCraft:
    def test_can_craft_true_with_fp(self):
        state = make_state(fp=10)
        assert state.can_craft is True

    def test_can_craft_false_when_fractured(self):
        state = make_state(fp=50, is_fractured=True)
        assert state.can_craft is False

    def test_can_craft_false_when_fp_zero(self):
        state = make_state(fp=0)
        assert state.can_craft is False

    def test_can_craft_false_when_both_fractured_and_no_fp(self):
        state = make_state(fp=0, is_fractured=True)
        assert state.can_craft is False

    def test_can_craft_true_with_fp_one(self):
        state = make_state(fp=1)
        assert state.can_craft is True


# ---------------------------------------------------------------------------
# CraftState.clone
# ---------------------------------------------------------------------------

class TestCraftStateClone:
    def test_clone_is_different_object(self):
        state = make_state()
        clone = state.clone()
        assert clone is not state

    def test_clone_fields_equal(self):
        state = make_state(fp=30, craft_count=5, metadata={"key": "val"})
        clone = state.clone()
        assert clone.forging_potential == 30
        assert clone.craft_count == 5
        assert clone.metadata == {"key": "val"}

    def test_mutating_clone_does_not_affect_original(self):
        state = make_state(affixes=[make_affix("flat_life")])
        clone = state.clone()
        clone.affixes.append(make_affix("fire_res"))
        assert len(state.affixes) == 1

    def test_mutating_clone_affix_tier_does_not_affect_original(self):
        affix = make_affix("flat_life", current_tier=3)
        state = make_state(affixes=[affix])
        clone = state.clone()
        clone.affixes[0].current_tier = 7
        assert state.affixes[0].current_tier == 3

    def test_mutating_clone_fp_does_not_affect_original(self):
        state = make_state(fp=50)
        clone = state.clone()
        clone.forging_potential = 0
        assert state.forging_potential == 50


# ---------------------------------------------------------------------------
# CraftState.snapshot / serialize
# ---------------------------------------------------------------------------

class TestCraftStateSnapshot:
    def test_snapshot_returns_dict(self):
        state = make_state()
        snap = state.snapshot()
        assert isinstance(snap, dict)

    def test_snapshot_contains_all_fields(self):
        state = make_state()
        snap = state.snapshot()
        for key in ("item_id", "item_name", "item_class", "forging_potential",
                    "instability", "affixes", "is_fractured", "fracture_type",
                    "craft_count", "metadata"):
            assert key in snap, f"Missing key: {key}"

    def test_serialize_equals_snapshot(self):
        state = make_state(fp=42)
        assert state.serialize() == state.snapshot()

    def test_snapshot_affixes_serialized(self):
        state = make_state(affixes=[make_affix("flat_life", 2, 7)])
        snap = state.snapshot()
        assert len(snap["affixes"]) == 1
        assert snap["affixes"][0]["affix_id"] == "flat_life"


# ---------------------------------------------------------------------------
# CraftState.from_dict
# ---------------------------------------------------------------------------

class TestCraftStateFromDict:
    def _base_data(self, **kwargs):
        data = {
            "item_id": "helm-42",
            "item_name": "Shadow Helm",
            "item_class": "helm",
            "forging_potential": 60,
            "instability": 10,
            "affixes": [],
            "is_fractured": False,
            "fracture_type": None,
            "craft_count": 0,
            "metadata": {},
        }
        data.update(kwargs)
        return data

    def test_from_dict_basic(self):
        data = self._base_data()
        state = CraftState.from_dict(data)
        assert state.item_id == "helm-42"
        assert state.forging_potential == 60

    def test_from_dict_roundtrip(self):
        original = make_state(
            fp=55,
            affixes=[make_affix("flat_life", 3, 7), make_affix("fire_res", 2, 5)]
        )
        snap = original.snapshot()
        restored = CraftState.from_dict(snap)
        assert restored.forging_potential == 55
        assert len(restored.affixes) == 2
        assert restored.affixes[0].affix_id == "flat_life"
        assert restored.affixes[0].current_tier == 3

    def test_from_dict_uses_defaults(self):
        data = self._base_data()
        del data["is_fractured"]
        del data["craft_count"]
        state = CraftState.from_dict(data)
        assert state.is_fractured is False
        assert state.craft_count == 0

    def test_from_dict_metadata_preserved(self):
        data = self._base_data(metadata={"custom": 42})
        state = CraftState.from_dict(data)
        assert state.metadata["custom"] == 42


# ---------------------------------------------------------------------------
# Metadata dict preserved
# ---------------------------------------------------------------------------

class TestCraftStateMetadata:
    def test_metadata_preserved_on_clone(self):
        state = make_state(metadata={"instability_modifier": 0.5, "run_id": "abc"})
        clone = state.clone()
        assert clone.metadata["instability_modifier"] == 0.5
        assert clone.metadata["run_id"] == "abc"

    def test_metadata_mutation_isolation(self):
        state = make_state(metadata={"key": "original"})
        clone = state.clone()
        clone.metadata["key"] = "mutated"
        assert state.metadata["key"] == "original"


# ---------------------------------------------------------------------------
# AffixTier tests
# ---------------------------------------------------------------------------

class TestAffixTier:
    def _tier(self, current=1, max_tier=7) -> AffixTier:
        return AffixTier(affix_id="flat_life", affix_name="Flat Life",
                         current_tier=current, max_tier=max_tier)

    def test_is_maxed_true_when_equal(self):
        t = self._tier(current=7, max_tier=7)
        assert t.is_maxed is True

    def test_is_maxed_false_when_below(self):
        t = self._tier(current=5, max_tier=7)
        assert t.is_maxed is False

    def test_is_maxed_true_with_lower_max(self):
        t = self._tier(current=3, max_tier=3)
        assert t.is_maxed is True

    def test_tier_weight_matches_dict(self):
        for tier, expected_weight in TIER_WEIGHTS.items():
            t = self._tier(current=tier)
            assert t.tier_weight == expected_weight

    def test_tier_weight_unknown_tier_returns_one(self):
        t = self._tier(current=99)
        assert t.tier_weight == 1

    def test_can_upgrade_false_when_maxed(self):
        t = self._tier(current=7, max_tier=7)
        assert t.can_upgrade() is False

    def test_can_upgrade_true_when_not_maxed(self):
        t = self._tier(current=5, max_tier=7)
        assert t.can_upgrade() is True

    def test_upgrade_increments_tier(self):
        t = self._tier(current=3, max_tier=7)
        result = t.upgrade()
        assert result is True
        assert t.current_tier == 4

    def test_upgrade_returns_false_when_maxed(self):
        t = self._tier(current=7, max_tier=7)
        result = t.upgrade()
        assert result is False
        assert t.current_tier == 7

    def test_downgrade_decrements_tier(self):
        t = self._tier(current=5, max_tier=7)
        result = t.downgrade()
        assert result is True
        assert t.current_tier == 4

    def test_downgrade_returns_false_at_tier_one(self):
        t = self._tier(current=1, max_tier=7)
        result = t.downgrade()
        assert result is False
        assert t.current_tier == 1

    def test_set_tier_normal(self):
        t = self._tier(current=1, max_tier=7)
        t.set_tier(5)
        assert t.current_tier == 5

    def test_set_tier_clamped_below_one(self):
        t = self._tier(current=3, max_tier=7)
        t.set_tier(0)
        assert t.current_tier == 1

    def test_set_tier_clamped_above_max(self):
        t = self._tier(current=3, max_tier=5)
        t.set_tier(10)
        assert t.current_tier == 5

    def test_set_tier_exactly_max(self):
        t = self._tier(current=1, max_tier=7)
        t.set_tier(7)
        assert t.current_tier == 7

    def test_tier_progress_min(self):
        t = self._tier(current=1, max_tier=7)
        assert pytest.approx(t.tier_progress(), rel=1e-6) == 1 / 7

    def test_tier_progress_max(self):
        t = self._tier(current=7, max_tier=7)
        assert pytest.approx(t.tier_progress(), rel=1e-6) == 1.0

    def test_tier_progress_mid(self):
        t = self._tier(current=4, max_tier=7)
        assert pytest.approx(t.tier_progress(), rel=1e-6) == 4 / 7


# ---------------------------------------------------------------------------
# CraftAction.is_valid_for tests
# ---------------------------------------------------------------------------

class TestCraftActionIsValidFor:
    def test_fractured_item_invalid_for_any_action(self):
        state = make_state(fp=50, is_fractured=True)
        action = CraftAction(ActionType.ADD_AFFIX, new_affix_id="flat_life")
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "fractured" in reason

    def test_fractured_item_invalid_for_upgrade(self):
        state = make_state(fp=50, is_fractured=True,
                           affixes=[make_affix("flat_life", current_tier=3)])
        action = CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="flat_life")
        valid, _ = action.is_valid_for(state)
        assert valid is False

    def test_zero_fp_invalid_for_add_affix(self):
        state = make_state(fp=0)
        action = CraftAction(ActionType.ADD_AFFIX, new_affix_id="flat_life")
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "forging potential" in reason

    def test_zero_fp_invalid_for_upgrade(self):
        state = make_state(fp=0, affixes=[make_affix("flat_life", 3, 7)])
        action = CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="flat_life")
        valid, _ = action.is_valid_for(state)
        assert valid is False

    def test_zero_fp_valid_for_rune(self):
        state = make_state(fp=0, affixes=[make_affix("flat_life")])
        action = CraftAction(ActionType.APPLY_RUNE)
        valid, _ = action.is_valid_for(state)
        assert valid is True

    def test_add_affix_with_four_affixes_invalid(self):
        affixes = [make_affix(f"affix_{i}") for i in range(4)]
        state = make_state(fp=50, affixes=affixes)
        action = CraftAction(ActionType.ADD_AFFIX, new_affix_id="new_affix")
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "4 affixes" in reason

    def test_add_affix_missing_new_affix_id_invalid(self):
        state = make_state(fp=50)
        action = CraftAction(ActionType.ADD_AFFIX, new_affix_id=None)
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "new_affix_id" in reason

    def test_add_affix_valid(self):
        state = make_state(fp=50, affixes=[make_affix("existing")])
        action = CraftAction(ActionType.ADD_AFFIX, new_affix_id="new_one")
        valid, reason = action.is_valid_for(state)
        assert valid is True
        assert reason == "ok"

    def test_upgrade_affix_at_max_tier_invalid(self):
        state = make_state(fp=50, affixes=[make_affix("flat_life", 7, 7)])
        action = CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="flat_life")
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "maxed" in reason

    def test_upgrade_affix_upgradeable_valid(self):
        state = make_state(fp=50, affixes=[make_affix("flat_life", 3, 7)])
        action = CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="flat_life")
        valid, _ = action.is_valid_for(state)
        assert valid is True

    def test_remove_affix_locked_invalid(self):
        state = make_state(fp=50, affixes=[make_affix("flat_life", locked=True)])
        action = CraftAction(ActionType.REMOVE_AFFIX, target_affix_id="flat_life")
        valid, reason = action.is_valid_for(state)
        assert valid is False
        assert "locked" in reason

    def test_remove_affix_unlocked_valid(self):
        state = make_state(fp=50, affixes=[make_affix("flat_life", locked=False)])
        action = CraftAction(ActionType.REMOVE_AFFIX, target_affix_id="flat_life")
        valid, _ = action.is_valid_for(state)
        assert valid is True

    def test_remove_affix_not_found_invalid(self):
        state = make_state(fp=50, affixes=[make_affix("other_affix")])
        action = CraftAction(ActionType.REMOVE_AFFIX, target_affix_id="missing_affix")
        valid, _ = action.is_valid_for(state)
        assert valid is False


# ---------------------------------------------------------------------------
# BisTarget tests
# ---------------------------------------------------------------------------

class TestBisTarget:
    def _make_target(self, reqs=None) -> BisTarget:
        if reqs is None:
            reqs = [
                AffixRequirement("flat_life", min_tier=3, target_tier=7, required=True),
                AffixRequirement("fire_res", min_tier=2, target_tier=5, required=True),
                AffixRequirement("move_speed", min_tier=1, target_tier=3, required=False),
            ]
        return BisTarget(item_class="helm", requirements=reqs)

    def test_required_affixes_only_required(self):
        target = self._make_target()
        req = target.required_affixes
        assert "flat_life" in req
        assert "fire_res" in req
        assert "move_speed" not in req

    def test_required_affixes_empty_when_none_required(self):
        reqs = [AffixRequirement("affix_a", required=False)]
        target = BisTarget("helm", requirements=reqs)
        assert target.required_affixes == []

    def test_target_tiers_correct_dict(self):
        target = self._make_target()
        tiers = target.target_tiers
        assert tiers["flat_life"] == 7
        assert tiers["fire_res"] == 5
        assert tiers["move_speed"] == 3

    def test_target_tiers_empty_no_requirements(self):
        target = BisTarget("helm")
        assert target.target_tiers == {}

    def test_is_satisfied_all_present_at_min_tier(self):
        target = self._make_target()
        state = make_state(affixes=[
            make_affix("flat_life", current_tier=3, max_tier=7),
            make_affix("fire_res", current_tier=2, max_tier=5),
        ])
        assert target.is_satisfied(state) is True

    def test_is_satisfied_above_min_tier(self):
        target = self._make_target()
        state = make_state(affixes=[
            make_affix("flat_life", current_tier=7, max_tier=7),
            make_affix("fire_res", current_tier=5, max_tier=5),
        ])
        assert target.is_satisfied(state) is True

    def test_is_satisfied_false_missing_required(self):
        target = self._make_target()
        state = make_state(affixes=[make_affix("flat_life", current_tier=4)])
        # fire_res missing
        assert target.is_satisfied(state) is False

    def test_is_satisfied_false_tier_too_low(self):
        target = self._make_target()
        state = make_state(affixes=[
            make_affix("flat_life", current_tier=2, max_tier=7),  # below min_tier=3
            make_affix("fire_res", current_tier=2, max_tier=5),
        ])
        assert target.is_satisfied(state) is False

    def test_is_satisfied_optional_missing_still_satisfied(self):
        target = self._make_target()
        state = make_state(affixes=[
            make_affix("flat_life", current_tier=3),
            make_affix("fire_res", current_tier=2),
            # move_speed intentionally absent
        ])
        assert target.is_satisfied(state) is True

    def test_satisfaction_rate_all_met(self):
        reqs = [
            AffixRequirement("a", min_tier=1, required=True),
            AffixRequirement("b", min_tier=1, required=True),
        ]
        target = BisTarget("helm", requirements=reqs)
        state = make_state(affixes=[make_affix("a", 1), make_affix("b", 1)])
        assert pytest.approx(target.satisfaction_rate(state)) == 1.0

    def test_satisfaction_rate_none_met(self):
        reqs = [AffixRequirement("a", min_tier=1), AffixRequirement("b", min_tier=1)]
        target = BisTarget("helm", requirements=reqs)
        state = make_state()
        assert pytest.approx(target.satisfaction_rate(state)) == 0.0

    def test_satisfaction_rate_half_met(self):
        reqs = [AffixRequirement("a", min_tier=1), AffixRequirement("b", min_tier=3)]
        target = BisTarget("helm", requirements=reqs)
        state = make_state(affixes=[make_affix("a", 1), make_affix("b", 2)])
        # b tier 2 < min_tier 3 → not satisfied
        assert pytest.approx(target.satisfaction_rate(state)) == 0.5

    def test_satisfaction_rate_empty_requirements(self):
        target = BisTarget("helm", requirements=[])
        state = make_state()
        assert pytest.approx(target.satisfaction_rate(state)) == 1.0
