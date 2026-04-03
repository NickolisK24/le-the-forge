from __future__ import annotations
from dataclasses import dataclass


TIER_WEIGHTS = {1: 100, 2: 80, 3: 60, 4: 45, 5: 30, 6: 15, 7: 5}  # lower weight = rarer


@dataclass
class AffixTier:
    affix_id: str
    affix_name: str
    current_tier: int        # 1-7
    max_tier: int = 7
    weight: int = 100        # roll weight for this affix being selected
    category: str = "prefix"  # "prefix" or "suffix"

    @property
    def is_maxed(self) -> bool:
        return self.current_tier >= self.max_tier

    @property
    def tier_weight(self) -> int:
        return TIER_WEIGHTS.get(self.current_tier, 1)

    def can_upgrade(self) -> bool:
        return self.current_tier < self.max_tier

    def upgrade(self) -> bool:
        if self.can_upgrade():
            self.current_tier += 1
            return True
        return False

    def downgrade(self) -> bool:
        if self.current_tier > 1:
            self.current_tier -= 1
            return True
        return False

    def set_tier(self, tier: int) -> None:
        self.current_tier = max(1, min(self.max_tier, tier))

    def tier_progress(self) -> float:
        return self.current_tier / self.max_tier
