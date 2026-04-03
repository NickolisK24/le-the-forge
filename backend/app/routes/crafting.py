from __future__ import annotations
from flask import Blueprint, request, jsonify
from crafting.models.craft_state import CraftState, AffixState
from crafting.models.craft_action import CraftAction, ActionType
from crafting.models.bis_target import BisTarget, AffixRequirement
from crafting.optimization.craft_optimizer import CraftOptimizer
from crafting.simulation.monte_carlo_crafting import MonteCarloCraftSimulator, MCCraftConfig
from crafting.metrics.craft_metrics import compute_craft_metrics

crafting_bp = Blueprint("crafting", __name__)


@crafting_bp.route("/api/optimize/crafting", methods=["POST"])
def optimize_crafting():
    data = request.get_json(force=True) or {}
    try:
        # Build CraftState from payload
        base = data.get("base_item", {})
        affixes = [AffixState(**a) for a in base.get("affixes", [])]
        state = CraftState(
            item_id=base.get("item_id", "unknown"),
            item_name=base.get("item_name", "Unknown Item"),
            item_class=base.get("item_class", "helm"),
            forging_potential=base.get("forging_potential", 60),
            instability=base.get("instability", 0),
            affixes=affixes,
        )
        target_affixes = data.get("target_affixes", [])
        tier_goals = data.get("tier_goals", {})
        n_runs = min(data.get("n_runs", 500), 5000)

        optimizer = CraftOptimizer()
        opt_result = optimizer.optimize(state, target_affixes, tier_goals)

        mc_config = MCCraftConfig(n_runs=n_runs)
        mc_sim = MonteCarloCraftSimulator(mc_config)
        mc_result = mc_sim.run(state, opt_result.best_path)
        metrics = compute_craft_metrics(mc_result, state.forging_potential)

        return jsonify({
            "optimal_path": [
                {"action_type": a.action_type.value,
                 "target_affix_id": a.target_affix_id,
                 "new_affix_id": a.new_affix_id}
                for a in opt_result.best_path
            ],
            "score": opt_result.best_score.total,
            "success_probability": metrics.success_probability,
            "mean_fp_cost": metrics.mean_fp_cost,
            "fracture_rate": mc_result.fracture_rate,
            "confidence_interval": [metrics.confidence_low, metrics.confidence_high],
            "steps": len(opt_result.best_path),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
