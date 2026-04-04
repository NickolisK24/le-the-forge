from __future__ import annotations
from dataclasses import dataclass, field
import random

from crafting.models.craft_state import CraftState
from crafting.models.craft_action import CraftAction
from crafting.engines.craft_execution_engine import CraftExecutionEngine


@dataclass
class SimulationStep:
    step_index: int
    action_type: str
    success: bool
    fp_before: int
    fp_after: int
    instability_before: int
    instability_after: int
    fractured: bool
    message: str


@dataclass
class SequenceResult:
    steps: list[SimulationStep]
    final_state: CraftState
    total_fp_spent: int
    total_crafts: int
    fractured: bool
    fracture_step: int | None


class SequenceSimulator:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()
        self._engine = CraftExecutionEngine(self._rng)

    def simulate(
        self,
        initial_state: CraftState,
        actions: list[CraftAction],
        available_affixes: list[str] | None = None,
        stop_on_fracture: bool = True,
    ) -> SequenceResult:
        state = initial_state.clone()
        steps = []
        total_fp = 0
        fracture_step = None

        for i, action in enumerate(actions):
            fp_before = state.forging_potential
            inst_before = state.instability
            result = self._engine.execute(state, action, available_affixes)
            fp_after = state.forging_potential
            inst_after = state.instability
            fp_spent = fp_before - fp_after
            if fp_spent > 0:
                total_fp += fp_spent

            fractured = result.fracture_result is not None and result.fracture_result.fractured
            if fractured and fracture_step is None:
                fracture_step = i

            steps.append(SimulationStep(
                i, result.action_type, result.success,
                fp_before, fp_after, inst_before, inst_after,
                fractured, result.message,
            ))
            if fractured and stop_on_fracture:
                break

        return SequenceResult(
            steps, state, total_fp, len(steps),
            state.is_fractured, fracture_step,
        )

    def branch(
        self,
        initial_state: CraftState,
        actions: list[CraftAction],
        n_branches: int = 10,
    ) -> list[SequenceResult]:
        results = []
        for _ in range(n_branches):
            branch_rng = random.Random(self._rng.randint(0, 2**31))
            sim = SequenceSimulator(branch_rng)
            results.append(sim.simulate(initial_state, actions))
        return results
