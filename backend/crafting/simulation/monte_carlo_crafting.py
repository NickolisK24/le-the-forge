from __future__ import annotations
from dataclasses import dataclass, field
import random, statistics, math

from crafting.models.craft_state import CraftState
from crafting.models.craft_action import CraftAction
from crafting.simulation.sequence_simulator import SequenceSimulator


@dataclass
class MCCraftConfig:
    n_runs: int = 1000
    base_seed: int = 42
    stop_on_fracture: bool = True
    available_affixes: list[str] = field(default_factory=list)


@dataclass
class MCCraftResult:
    n_runs: int
    success_rate: float      # fraction that didn't fracture
    mean_fp_spent: float
    std_fp_spent: float
    mean_crafts: float
    fracture_rate: float
    percentile_5_fp: float
    percentile_95_fp: float


class MonteCarloCraftSimulator:
    def __init__(self, config: MCCraftConfig | None = None):
        self.config = config or MCCraftConfig()

    def run(self, initial_state: CraftState, actions: list[CraftAction]) -> MCCraftResult:
        seed_mgr_rng = random.Random(self.config.base_seed)
        fp_spent_list = []
        fracture_count = 0
        craft_counts = []

        for i in range(self.config.n_runs):
            seed = seed_mgr_rng.randint(0, 2**31)
            rng = random.Random(seed)
            sim = SequenceSimulator(rng)
            result = sim.simulate(initial_state, actions,
                                  self.config.available_affixes,
                                  self.config.stop_on_fracture)
            fp_spent_list.append(result.total_fp_spent)
            craft_counts.append(result.total_crafts)
            if result.fractured:
                fracture_count += 1

        fp_sorted = sorted(fp_spent_list)
        n = len(fp_sorted)
        p5 = fp_sorted[max(0, int(n * 0.05) - 1)]
        p95 = fp_sorted[min(n - 1, int(n * 0.95))]

        return MCCraftResult(
            n_runs=self.config.n_runs,
            success_rate=1.0 - fracture_count / self.config.n_runs,
            mean_fp_spent=statistics.mean(fp_spent_list),
            std_fp_spent=statistics.stdev(fp_spent_list) if len(fp_spent_list) > 1 else 0.0,
            mean_crafts=statistics.mean(craft_counts),
            fracture_rate=fracture_count / self.config.n_runs,
            percentile_5_fp=p5,
            percentile_95_fp=p95,
        )
