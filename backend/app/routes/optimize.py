"""
Optimize Blueprint — /api/optimize

POST /api/optimize/build
    Run the full optimization pipeline for a BuildDefinition.

    Input:  { build, config?, encounter?, top_n? }
    Output: {
        results:                     [...],
        total_variants_generated:    int,
        variants_passed_constraints: int,
        variants_simulated:          int,
        variants_failed_simulation:  int,
    }
"""

from flask import Blueprint, request
from marshmallow import ValidationError

from app import limiter
from app.schemas.optimize import OptimizeBuildSchema
from app.utils.responses import ok, error, validation_error


optimize_bp = Blueprint("optimize", __name__)

_optimize_build_schema = OptimizeBuildSchema()


@optimize_bp.post("/build")
@limiter.limit("5 per minute")
def optimize_build():
    """Run the full variant-generation + simulation + ranking pipeline."""
    try:
        data = _optimize_build_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    # Lazily import to avoid circular-import issues at module load time
    from builds.build_definition import BuildDefinition
    from optimization.models.optimization_config import OptimizationConfig
    from optimization.optimization_service import optimize

    try:
        base_build = BuildDefinition.from_dict(data["build"])
    except (KeyError, ValueError) as e:
        return error(f"Invalid build definition: {e}", status=400)

    raw_config = data.get("config") or {}
    config = OptimizationConfig(
        target_metric  = raw_config.get("target_metric",  "dps"),
        max_variants   = raw_config.get("max_variants",   50),
        mutation_depth = raw_config.get("mutation_depth", 2),
        constraints    = raw_config.get("constraints",    {}),
        random_seed    = raw_config.get("random_seed",    42),
    )

    encounter_kwargs = None
    if data.get("encounter"):
        encounter_kwargs = dict(data["encounter"])

    try:
        result = optimize(
            base_build       = base_build,
            config           = config,
            encounter_kwargs = encounter_kwargs,
            top_n            = data.get("top_n", 10),
        )
    except Exception as e:
        return error(f"Optimization failed: {e}", status=500)

    return ok(data=result)
