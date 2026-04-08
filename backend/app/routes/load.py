"""
J14 — POST /api/load/game-data

Triggers a hot-reload of the game-data pipeline and runs a data-integrity
pass on the freshly loaded data.  Returns counts, version info, and any
integrity warnings/errors detected during loading.
"""

from flask import Blueprint, current_app

from app import limiter
from app.utils.responses import ok, error
from data.loaders.raw_data_loader import RawDataLoader
from data.versioning.versioned_loader import VersionedLoader
from data.mappers.data_mapper import DataMapper
from debug.data_integrity_logger import DataIntegrityLogger, Severity

load_bp = Blueprint("load", __name__)


@load_bp.post("/game-data")
@limiter.limit("5 per minute")
def load_game_data():
    """
    Reload game data and run integrity checks.

    Returns
    -------
    200 OK
        {
          "version": "...",
          "counts": { "skills": N, "affixes": N, "enemies": N, "passives": N },
          "integrity": { "total": N, "errors": N, "warnings": N, "infos": N },
          "issues": [ { "severity": "...", "category": "...", ... } ]
        }
    """
    integrity = DataIntegrityLogger(max_entries=200)

    # 1. Reload the existing pipeline
    try:
        pipeline = current_app.extensions["game_data"]
        pipeline.reload()
        integrity.info("pipeline", "reload", "Pipeline reloaded successfully")
    except Exception as exc:
        return error(f"Pipeline reload failed: {exc}", 500)

    # 2. Detect version via the standalone VersionedLoader
    vl = VersionedLoader()
    version_info = vl.detect_version()

    # 3. Run mapper integrity checks on the live data
    raw_loader = RawDataLoader()
    counts: dict[str, int] = {}
    mapper = DataMapper()

    # Skills
    try:
        from app.game_data.game_data_loader import get_skill_stats
        raw_skills = get_skill_stats()
        n_skills = len(raw_skills)
        counts["skills"] = n_skills
        integrity.info("skills", "count", f"Loaded {n_skills} skill definitions")
    except Exception as exc:
        integrity.error("skills", "load", str(exc))
        counts["skills"] = 0

    # Affixes
    try:
        bundle = raw_loader.load("items/affixes.json")
        affixes = mapper.affixes_from_bundle(bundle)
        counts["affixes"] = len(affixes)
        integrity.info("affixes", "count", f"Mapped {len(affixes)} affix tiers")
    except Exception as exc:
        integrity.error("affixes", "load", str(exc))
        counts["affixes"] = 0

    # Enemies
    try:
        bundle = raw_loader.load("entities/enemy_profiles.json")
        enemies = mapper.enemies_from_bundle(bundle)
        counts["enemies"] = len(enemies)
        for e in enemies:
            if e.max_health <= 0:
                integrity.warning("enemy", e.enemy_id, "max_health <= 0")
    except Exception as exc:
        integrity.error("enemies", "load", str(exc))
        counts["enemies"] = 0

    # Passives
    try:
        bundle = raw_loader.load("classes/passives.json")
        passives = mapper.passives_from_bundle(bundle)
        counts["passives"] = len(passives)
        integrity.info("passives", "count", f"Mapped {len(passives)} passive nodes")
    except Exception as exc:
        integrity.error("passives", "load", str(exc))
        counts["passives"] = 0

    # 4. Build response
    issues = integrity.to_list(Severity.WARNING) + integrity.to_list(Severity.ERROR)

    return ok({
        "version": version_info.version,
        "version_source": version_info.source,
        "counts": counts,
        "integrity": integrity.summary(),
        "issues": issues,
    })
