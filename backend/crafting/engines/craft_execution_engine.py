from __future__ import annotations
from dataclasses import dataclass
import random

from crafting.models.craft_action import CraftAction, ActionType
from crafting.models.craft_state import AffixState
from crafting.engines.forging_potential_engine import ForgingPotentialEngine
from crafting.engines.instability_engine import InstabilityEngine
from crafting.engines.fracture_engine import FractureEngine
from crafting.engines.glyph_engine import GlyphEngine
from crafting.engines.rune_engine import RuneEngine


@dataclass
class ExecutionResult:
    success: bool
    action_type: str
    fp_cost: int
    instability_added: int
    fracture_result: any   # FractureResult | None
    message: str
    state_snapshot: dict | None = None


class CraftExecutionEngine:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()
        self._fp_engine = ForgingPotentialEngine(self._rng)
        self._inst_engine = InstabilityEngine()
        self._frac_engine = FractureEngine(self._rng)
        self._glyph_engine = GlyphEngine(self._rng)
        self._rune_engine = RuneEngine(self._rng)

    def execute(self, state, action: CraftAction, available_affixes: list[str] | None = None) -> ExecutionResult:
        valid, reason = action.is_valid_for(state)
        if not valid:
            return ExecutionResult(False, action.action_type.value, 0, 0, None, reason)

        fp_cost = 0
        inst_added = 0
        frac = None

        # Apply action
        if action.action_type == ActionType.ADD_AFFIX:
            state.affixes.append(AffixState(action.new_affix_id, 1, 7))
        elif action.action_type == ActionType.UPGRADE_AFFIX:
            for a in state.affixes:
                if a.affix_id == action.target_affix_id:
                    a.current_tier = min(a.current_tier + 1, a.max_tier)
                    break
        elif action.action_type == ActionType.REMOVE_AFFIX:
            state.affixes = [a for a in state.affixes if a.affix_id != action.target_affix_id]
        elif action.action_type == ActionType.REROLL_AFFIX:
            for a in state.affixes:
                if a.affix_id == action.target_affix_id:
                    a.current_tier = self._rng.randint(1, a.max_tier)
                    break
        elif action.action_type == ActionType.APPLY_GLYPH:
            self._glyph_engine.apply(action.glyph_type, state)
        elif action.action_type == ActionType.APPLY_RUNE:
            self._rune_engine.apply(action.rune_type, state, available_affixes)

        # Apply FP cost (runes bypass FP)
        if action.action_type != ActionType.APPLY_RUNE:
            fp_result = self._fp_engine.apply_cost(state, action.action_type.value)
            fp_cost = fp_result.actual_cost
            # Check for FP preservation from Glyph of Hope
            if state.metadata.get("fp_preserved"):
                state.forging_potential += fp_cost
                state.metadata.pop("fp_preserved")

        # Apply instability
        if action.action_type not in (ActionType.APPLY_RUNE, ActionType.APPLY_GLYPH):
            inst_mod = state.metadata.pop("instability_modifier", 1.0)
            inst_result = self._inst_engine.apply(state, inst_mod)
            inst_added = inst_result.added
            # Check fracture
            frac = self._frac_engine.apply(state, inst_result.fracture_chance)

        state.craft_count += 1
        return ExecutionResult(
            True, action.action_type.value, fp_cost, inst_added, frac, "ok", state.snapshot()
        )
