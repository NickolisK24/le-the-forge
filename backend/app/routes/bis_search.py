from flask import Blueprint, request

from app import limiter
from app.utils.responses import ok, error
from bis.models.item_slot import SlotPool
from bis.engine.incremental_search import IncrementalSearchEngine

bis_bp = Blueprint("bis", __name__)


def _humanize_affix(affix_id: str) -> str:
    """Turn internal affix ids like 'critical_strike_chance' into
    'Critical Strike Chance' for display in the results table."""
    return affix_id.replace("_", " ").title()


def _serialize_entry(entry, snapshots):
    """Build a result row with the extra readable fields the UI needs.

    Each snapshot in the incremental search currently covers a single slot —
    we surface that slot's base item name and its affixes (with tiers) so
    users see something meaningful instead of 'snap_0002'.
    """
    row = {
        "rank": entry.rank,
        "build_id": entry.build_id,
        "score": entry.score.total_score,
        "percentile": entry.percentile,
        "slot": None,
        "item_name": None,
        "affixes": [],
    }
    snap = snapshots.get(entry.build_id) if snapshots else None
    if snap and snap.slots:
        # Take the primary (first) slot for display. The incremental engine
        # currently evaluates one slot per snapshot; when that changes we can
        # expand this into a per-slot breakdown.
        slot_type, state = next(iter(snap.slots.items()))
        row["slot"] = slot_type
        row["item_name"] = getattr(state, "item_name", None)
        row["affixes"] = [
            {
                "id": a.affix_id,
                "name": _humanize_affix(a.affix_id),
                "tier": a.current_tier,
            }
            for a in state.affixes
        ]
    return row


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

        snapshots = result.metadata.get("snapshots", {})
        return ok(data={
            "search_id": result.search_id,
            "total_evaluated": result.total_evaluated,
            "results": [_serialize_entry(e, snapshots) for e in result.top_entries],
            "best_score": result.best_score,
            "duration_s": result.search_duration_s,
        })
    except ValueError as e:
        return error(str(e), status=422)
