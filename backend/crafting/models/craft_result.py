from __future__ import annotations
from dataclasses import dataclass, field

from crafting.models.craft_action import CraftAction
from crafting.optimization.scoring import CraftScore


@dataclass
class CraftResult:
    build_id: str
    item_id: str
    best_sequence: list[CraftAction]
    score: CraftScore
    success_probability: float
    mean_fp_cost: float
    expected_fracture_rate: float
    total_steps: int
    metadata: dict = field(default_factory=dict)

    @property
    def is_viable(self) -> bool:
        return self.success_probability >= 0.3 and self.score.total >= 0.5

    def summary(self) -> dict:
        return {
            "build_id": self.build_id,
            "item_id": self.item_id,
            "score": self.score.total,
            "success_probability": self.success_probability,
            "mean_fp_cost": self.mean_fp_cost,
            "steps": self.total_steps,
            "viable": self.is_viable,
        }
