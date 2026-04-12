"""
Meta Analytics Service — aggregates data across all public community builds.

Computes class distribution, mastery distribution, popular skills/affixes,
average stats by class, trending builds, and patch breakdown.
"""

from datetime import datetime, timezone, timedelta

from sqlalchemy import func, desc

from app import db
from app.models import Build, BuildSkill
from app.utils.cache import get as cache_get, set as cache_set, delete as cache_del


_META_SNAPSHOT_TTL = 21600  # 6 hours
_META_TRENDING_TTL = 3600   # 1 hour

_KEY_SNAPSHOT = "forge:meta:snapshot"
_KEY_TRENDING = "forge:meta:trending"
_KEY_CLASS_DIST = "forge:meta:class_dist"
_KEY_SKILLS = "forge:meta:skills"
_KEY_AFFIXES = "forge:meta:affixes"


def _class_distribution():
    """Count and percentage of public builds per class."""
    counts = (
        db.session.query(Build.character_class, func.count(Build.id))
        .filter_by(is_public=True)
        .group_by(Build.character_class)
        .order_by(desc(func.count(Build.id)))
        .all()
    )
    total = sum(c for _, c in counts) or 1
    return [
        {"class": cls, "count": cnt, "percentage": round(cnt / total * 100, 1)}
        for cls, cnt in counts
    ]


def _mastery_distribution():
    """Count and percentage per mastery within each class."""
    rows = (
        db.session.query(Build.character_class, Build.mastery, func.count(Build.id))
        .filter_by(is_public=True)
        .group_by(Build.character_class, Build.mastery)
        .order_by(Build.character_class, desc(func.count(Build.id)))
        .all()
    )
    total = sum(c for _, _, c in rows) or 1
    result = {}
    for cls, mastery, cnt in rows:
        if cls not in result:
            result[cls] = []
        result[cls].append({
            "mastery": mastery,
            "count": cnt,
            "percentage": round(cnt / total * 100, 1),
        })
    return result


def _popular_skills(limit=10):
    """Top skills by usage count across all public builds."""
    rows = (
        db.session.query(BuildSkill.skill_name, func.count(BuildSkill.id))
        .join(Build, Build.id == BuildSkill.build_id)
        .filter(Build.is_public == True)  # noqa: E712
        .filter(BuildSkill.skill_name != "")
        .filter(BuildSkill.skill_name.isnot(None))
        .group_by(BuildSkill.skill_name)
        .order_by(desc(func.count(BuildSkill.id)))
        .limit(limit)
        .all()
    )
    return [{"skill_name": name, "usage_count": cnt} for name, cnt in rows]


def _popular_affixes(limit=10):
    """Top affixes by usage count across all public builds (from gear JSON)."""
    # Since affixes are stored as JSON arrays inside gear JSON, we can't
    # do a pure SQL query. We'll iterate builds in batches.
    builds = Build.query.filter_by(is_public=True).all()
    affix_counts = {}
    for build in builds:
        for slot in (build.gear or []):
            for affix in (slot.get("affixes") or []):
                name = affix.get("name", "")
                if name:
                    affix_counts[name] = affix_counts.get(name, 0) + 1

    sorted_affixes = sorted(affix_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [{"affix_name": name, "usage_count": cnt} for name, cnt in sorted_affixes]


def _average_stats_by_class():
    """Mean DPS-related stats per class (using vote_count as proxy for quality)."""
    # We compute a simple aggregate of view_count and vote_count per class
    rows = (
        db.session.query(
            Build.character_class,
            func.count(Build.id),
            func.avg(Build.vote_count),
            func.avg(Build.view_count),
        )
        .filter_by(is_public=True)
        .group_by(Build.character_class)
        .all()
    )
    return [
        {
            "class": cls,
            "build_count": cnt,
            "avg_votes": round(float(avg_votes or 0), 1),
            "avg_views": round(float(avg_views or 0), 1),
        }
        for cls, cnt, avg_votes, avg_views in rows
    ]


def _trending_builds(limit=10):
    """
    Builds with highest view velocity over the last 7 days.
    Velocity = view_count / max(age_in_days, 1), minimum 10 views.
    """
    now = datetime.now(timezone.utc)
    min_views = 10

    builds = (
        Build.query
        .filter_by(is_public=True)
        .filter(Build.view_count >= min_views)
        .all()
    )

    scored = []
    for b in builds:
        created = b.created_at
        # Handle naive datetimes (e.g. SQLite in tests)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_days = max((now - created).total_seconds() / 86400, 1.0)
        velocity = b.view_count / age_days
        scored.append((b, velocity))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:limit]

    return [
        {
            "id": b.id,
            "slug": b.slug,
            "name": b.name,
            "character_class": b.character_class,
            "mastery": b.mastery,
            "tier": b.tier,
            "vote_count": b.vote_count,
            "view_count": b.view_count,
            "trending_score": round(velocity, 2),
            "author": b.author.username if b.author else None,
        }
        for b, velocity in top
    ]


def _patch_breakdown():
    """Distribution of builds by patch version."""
    rows = (
        db.session.query(Build.patch_version, func.count(Build.id))
        .filter_by(is_public=True)
        .group_by(Build.patch_version)
        .order_by(desc(func.count(Build.id)))
        .all()
    )
    return [{"patch_version": v, "count": c} for v, c in rows]


def compute_snapshot() -> dict:
    """Compute the full meta analytics snapshot."""
    from flask import current_app

    now = datetime.now(timezone.utc)
    patch = current_app.config.get("CURRENT_PATCH", "1.4.3")

    return {
        "class_distribution": _class_distribution(),
        "mastery_distribution": _mastery_distribution(),
        "popular_skills": _popular_skills(),
        "popular_affixes": _popular_affixes(),
        "average_stats_by_class": _average_stats_by_class(),
        "patch_breakdown": _patch_breakdown(),
        "last_updated": now.isoformat(),
        "current_patch": patch,
    }


def get_snapshot() -> dict:
    """Get cached snapshot or compute if missing."""
    cached = cache_get(_KEY_SNAPSHOT)
    if cached is not None:
        return cached

    data = compute_snapshot()
    cache_set(_KEY_SNAPSHOT, data, _META_SNAPSHOT_TTL)
    # Also cache sub-keys
    cache_set(_KEY_CLASS_DIST, data["class_distribution"], _META_SNAPSHOT_TTL)
    cache_set(_KEY_SKILLS, data["popular_skills"], _META_SNAPSHOT_TTL)
    cache_set(_KEY_AFFIXES, data["popular_affixes"], _META_SNAPSHOT_TTL)
    return data


def get_trending() -> list:
    """Get cached trending builds or compute if missing."""
    cached = cache_get(_KEY_TRENDING)
    if cached is not None:
        return cached

    data = _trending_builds()
    cache_set(_KEY_TRENDING, data, _META_TRENDING_TTL)
    return data


def refresh_all() -> dict:
    """Force refresh all meta analytics caches."""
    # Delete existing caches
    for key in (_KEY_SNAPSHOT, _KEY_TRENDING, _KEY_CLASS_DIST, _KEY_SKILLS, _KEY_AFFIXES):
        cache_del(key)

    snapshot = compute_snapshot()
    cache_set(_KEY_SNAPSHOT, snapshot, _META_SNAPSHOT_TTL)
    cache_set(_KEY_CLASS_DIST, snapshot["class_distribution"], _META_SNAPSHOT_TTL)
    cache_set(_KEY_SKILLS, snapshot["popular_skills"], _META_SNAPSHOT_TTL)
    cache_set(_KEY_AFFIXES, snapshot["popular_affixes"], _META_SNAPSHOT_TTL)

    trending = _trending_builds()
    cache_set(_KEY_TRENDING, trending, _META_TRENDING_TTL)

    return snapshot
