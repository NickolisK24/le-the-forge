from flask import Blueprint, request

from app import limiter
from app.utils.responses import ok, error
from bis.models.item_slot import SlotPool
from bis.engine.incremental_search import IncrementalSearchEngine

bis_bp = Blueprint("bis", __name__)


@bis_bp.route("/search", methods=["POST"])
@limiter.limit("15 per minute")
def bis_search():
    data = request.get_json(force=True) or {}
    try:
        slots = data.get("slots", ["helm", "chest"])
        target_affixes = data.get("target_affixes", ["max_life", "resistances"])
        target_tiers = {k: int(v) for k, v in data.get("target_tiers", {}).items()}
        top_n = min(int(data.get("top_n", 10)), 50)
        max_candidates = min(int(data.get("max_candidates", 200)), 1000)

        slot_pool = SlotPool.from_slot_types(slots)
        engine = IncrementalSearchEngine(n_runs_per_eval=30)
        result = engine.search(slot_pool, target_affixes, target_tiers, top_n, max_candidates)

        return ok(data={
            "search_id": result.search_id,
            "total_evaluated": result.total_evaluated,
            "results": [
                {
                    "rank": e.rank,
                    "build_id": e.build_id,
                    "score": e.score.total_score,
                    "percentile": e.percentile,
                }
                for e in result.top_entries
            ],
            "best_score": result.best_score,
            "duration_s": result.search_duration_s,
        })
    except ValueError as e:
        return error(str(e), status=422)
