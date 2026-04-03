from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    ADD_AFFIX = "add_affix"
    UPGRADE_AFFIX = "upgrade_affix"
    REMOVE_AFFIX = "remove_affix"
    REROLL_AFFIX = "reroll_affix"
    APPLY_GLYPH = "apply_glyph"
    APPLY_RUNE = "apply_rune"


@dataclass
class CraftAction:
    action_type: ActionType
    target_affix_id: str | None = None      # for targeted actions
    glyph_type: str | None = None           # for APPLY_GLYPH
    rune_type: str | None = None            # for APPLY_RUNE
    new_affix_id: str | None = None         # for ADD_AFFIX
    parameters: dict = field(default_factory=dict)

    def is_valid_for(self, state) -> tuple[bool, str]:
        # Returns (valid, reason)
        if state.is_fractured:
            return False, "item is fractured"
        if state.forging_potential <= 0 and self.action_type not in (ActionType.APPLY_RUNE,):
            return False, "no forging potential"
        if self.action_type == ActionType.ADD_AFFIX:
            if len(state.affixes) >= 4:
                return False, "item already has 4 affixes"
            if self.new_affix_id is None:
                return False, "new_affix_id required"
        if self.action_type == ActionType.UPGRADE_AFFIX:
            if not any(
                a.affix_id == self.target_affix_id and a.current_tier < a.max_tier
                for a in state.affixes
            ):
                return False, "target affix not found or already maxed"
        if self.action_type == ActionType.REMOVE_AFFIX:
            if not any(
                a.affix_id == self.target_affix_id and not a.locked
                for a in state.affixes
            ):
                return False, "target affix not found or locked"
        return True, "ok"
