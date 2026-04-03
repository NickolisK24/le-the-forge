from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import random


class GlyphType(Enum):
    STABILITY = "stability"  # reduces instability gain
    HOPE = "hope"            # chance to not consume FP
    CHAOS = "chaos"          # randomizes affix tiers


@dataclass
class GlyphResult:
    glyph_type: str
    applied: bool
    instability_modifier: float   # multiplier on instability gain
    fp_saved: bool                # True if FP was preserved
    affix_changed: str | None     # affix_id that was randomized by Chaos


class GlyphEngine:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def apply_stability(self, state) -> GlyphResult:
        # Reduces instability gain by 50% on next craft (tracked in metadata)
        state.metadata["instability_modifier"] = 0.5
        return GlyphResult("stability", True, 0.5, False, None)

    def apply_hope(self, state) -> GlyphResult:
        # 50% chance to save FP on next craft
        saved = self._rng.random() < 0.5
        state.metadata["fp_preserved"] = saved
        return GlyphResult("hope", True, 1.0, saved, None)

    def apply_chaos(self, state) -> GlyphResult:
        # Randomly changes tier of one random affix to random value
        if not state.affixes:
            return GlyphResult("chaos", False, 1.0, False, None)
        target = self._rng.choice(state.affixes)
        target.current_tier = self._rng.randint(1, target.max_tier)
        return GlyphResult("chaos", True, 1.0, False, target.affix_id)

    def apply(self, glyph_type: str | GlyphType, state) -> GlyphResult:
        if isinstance(glyph_type, GlyphType):
            glyph_type = glyph_type.value
        if glyph_type == GlyphType.STABILITY.value:
            return self.apply_stability(state)
        elif glyph_type == GlyphType.HOPE.value:
            return self.apply_hope(state)
        elif glyph_type == GlyphType.CHAOS.value:
            return self.apply_chaos(state)
        return GlyphResult(glyph_type, False, 1.0, False, None)
