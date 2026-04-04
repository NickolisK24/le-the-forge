from __future__ import annotations
from dataclasses import dataclass, field
import random

from crafting.models.craft_state import CraftState
from crafting.models.craft_action import CraftAction
from crafting.optimization.path_generator import PathGenerator, PathCandidate
from crafting.optimization.scoring import CraftScorer, CraftScore
from crafting.simulation.sequence_simulator import SequenceSimulator


@dataclass
class OptimizationResult:
    best_path: list[CraftAction]
    best_score: CraftScore
    strategy: str
    candidates_evaluated: int
    iterations: int


class CraftOptimizer:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()
        self._generator = PathGenerator(self._rng)
        self._scorer = CraftScorer()

    def beam_search(self, state: CraftState, target_affixes: list[str],
                    target_tiers: dict[str, int], beam_width: int = 5,
                    n_eval_runs: int = 10) -> OptimizationResult:
        initial_fp = state.forging_potential
        # Generate initial candidates
        candidates = self._generator.randomized(state, target_affixes, target_tiers, beam_width)
        best_score = CraftScore(0.0, 0.0, 0.0, 0.0, 0.0)
        best_path = candidates[0].actions if candidates else []
        evaluated = 0

        for candidate in candidates:
            score = self._evaluate_candidate(state, candidate, target_affixes, target_tiers,
                                             initial_fp, n_eval_runs)
            evaluated += n_eval_runs
            if score.total > best_score.total:
                best_score = score
                best_path = candidate.actions

        return OptimizationResult(best_path, best_score, "beam_search", evaluated, beam_width)

    def optimize(self, state: CraftState, target_affixes: list[str],
                 target_tiers: dict[str, int], iterations: int = 3,
                 beam_width: int = 5) -> OptimizationResult:
        best = self.beam_search(state, target_affixes, target_tiers, beam_width)
        total_evaluated = best.candidates_evaluated
        for _ in range(iterations - 1):
            result = self.beam_search(state, target_affixes, target_tiers, beam_width)
            total_evaluated += result.candidates_evaluated
            if result.best_score.total > best.best_score.total:
                best = result
        best.candidates_evaluated = total_evaluated
        best.iterations = iterations
        return best

    def _evaluate_candidate(self, state, candidate, target_affixes, target_tiers,
                            initial_fp, n_runs) -> CraftScore:
        scores = []
        for _ in range(n_runs):
            rng = random.Random(self._rng.randint(0, 2**31))
            sim = SequenceSimulator(rng)
            result = sim.simulate(state, candidate.actions)
            s = self._scorer.score(result.final_state, target_affixes, target_tiers, initial_fp)
            scores.append(s.total)
        avg = sum(scores) / len(scores)
        return CraftScore(avg, 0.0, 0.0, 0.0, 0.0)
