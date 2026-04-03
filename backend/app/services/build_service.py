"""
Build Service — CRUD operations for builds + vote management.

Vote logic:
  - A user can cast one vote per build (+1 or -1).
  - Voting the same direction again removes the vote (toggle).
  - Switching direction removes the old vote and applies the new one.
  - After each vote mutation, build.vote_count and build.tier are recalculated.
"""

import secrets
import re
from typing import Optional

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import desc, asc

from app import db
from app.models import Build, BuildSkill, Vote, User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:40]


def _unique_slug(base: str) -> str:
    slug = _slugify(base)
    if not Build.query.filter_by(slug=slug).first():
        return slug
    suffix = secrets.token_urlsafe(4)
    return f"{slug}-{suffix}"


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_build(data: dict, user_id: Optional[str] = None) -> Build:
    slug = _unique_slug(data["name"])

    build = Build(
        author_id=user_id,
        slug=slug,
        name=data["name"],
        description=data.get("description"),
        character_class=data["character_class"],
        mastery=data["mastery"],
        level=data.get("level", 100),
        passive_tree=data.get("passive_tree", []),
        gear=data.get("gear", []),
        is_ssf=data.get("is_ssf", False),
        is_hc=data.get("is_hc", False),
        is_ladder_viable=data.get("is_ladder_viable", True),
        is_budget=data.get("is_budget", False),
        patch_version=data.get("patch_version", "1.2.1"),
        cycle=data.get("cycle", "1.2"),
        is_public=data.get("is_public", True),
        tier="C",
    )
    db.session.add(build)

    # Attach skills
    for idx, skill_data in enumerate(data.get("skills", [])[:5]):
        skill = BuildSkill(
            build=build,
            slot=idx + 1,
            skill_name=skill_data.get("skill_name", ""),
            points_allocated=skill_data.get("points_allocated", 0),
            spec_tree=skill_data.get("spec_tree", []),
        )
        db.session.add(skill)

    db.session.commit()
    return build


def get_build(build_id_or_slug: str, increment_views: bool = False) -> Optional[Build]:
    build = Build.query.filter(
        (Build.id == build_id_or_slug) | (Build.slug == build_id_or_slug)
    ).first()
    if build and increment_views:
        build.view_count = (build.view_count or 0) + 1
        db.session.commit()
    return build


def update_build(build: Build, data: dict) -> Build:
    updatable = [
        "name", "description", "level", "passive_tree", "gear",
        "is_ssf", "is_hc", "is_ladder_viable", "is_budget",
        "patch_version", "is_public",
    ]
    for key in updatable:
        if key in data:
            setattr(build, key, data[key])

    if "skills" in data:
        # Replace skill set entirely
        BuildSkill.query.filter_by(build_id=build.id).delete()
        for idx, skill_data in enumerate(data["skills"][:5]):
            skill = BuildSkill(
                build_id=build.id,
                slot=idx + 1,
                skill_name=skill_data.get("skill_name", ""),
                points_allocated=skill_data.get("points_allocated", 0),
                spec_tree=skill_data.get("spec_tree", []),
            )
            db.session.add(skill)

    db.session.commit()
    return build


def delete_build(build: Build) -> None:
    db.session.delete(build)
    db.session.commit()


# ---------------------------------------------------------------------------
# Listing & filtering
# ---------------------------------------------------------------------------

def list_builds(
    page: int = 1,
    per_page: int = 20,
    character_class: Optional[str] = None,
    mastery: Optional[str] = None,
    tier: Optional[str] = None,
    is_ssf: Optional[bool] = None,
    is_hc: Optional[bool] = None,
    is_ladder_viable: Optional[bool] = None,
    is_budget: Optional[bool] = None,
    cycle: Optional[str] = None,
    sort: str = "votes",
    search: Optional[str] = None,
    author_id: Optional[str] = None,
    include_private: bool = False,
) -> tuple:
    """Returns (builds_list, total_count, pages)."""
    q = Build.query
    if not include_private:
        q = q.filter_by(is_public=True)
    if author_id:
        q = q.filter_by(author_id=author_id)

    if character_class:
        q = q.filter_by(character_class=character_class)
    if mastery:
        q = q.filter_by(mastery=mastery)
    if tier:
        q = q.filter_by(tier=tier)
    if is_ssf is not None:
        q = q.filter_by(is_ssf=is_ssf)
    if is_hc is not None:
        q = q.filter_by(is_hc=is_hc)
    if is_ladder_viable is not None:
        q = q.filter_by(is_ladder_viable=is_ladder_viable)
    if is_budget is not None:
        q = q.filter_by(is_budget=is_budget)
    if cycle:
        q = q.filter_by(cycle=cycle)
    if search:
        q = q.filter(Build.name.ilike(f"%{search}%"))

    sort_map = {
        "votes": desc(Build.vote_count),
        "new": desc(Build.created_at),
        "tier": asc(Build.tier),
        "views": desc(Build.view_count),
    }
    q = q.order_by(sort_map.get(sort, desc(Build.vote_count)))

    pagination = q.paginate(page=page, per_page=min(per_page, 100), error_out=False)
    return pagination.items, pagination.total, pagination.pages


# ---------------------------------------------------------------------------
# Voting
# ---------------------------------------------------------------------------

def cast_vote(build: Build, user_id: str, direction: int) -> dict:
    """
    direction: +1 (upvote) or -1 (downvote)

    Returns { vote_count, user_vote, tier }
    """
    existing = Vote.query.filter_by(user_id=user_id, build_id=build.id).first()

    if existing:
        if existing.direction == direction:
            # Toggle off — remove vote
            build.vote_count -= existing.direction
            db.session.delete(existing)
            user_vote = 0
        else:
            # Switch direction
            build.vote_count -= existing.direction
            build.vote_count += direction
            existing.direction = direction
            user_vote = direction
    else:
        vote = Vote(user_id=user_id, build_id=build.id, direction=direction)
        db.session.add(vote)
        build.vote_count += direction
        user_vote = direction

    build.recalculate_tier()
    db.session.commit()

    return {
        "vote_count": build.vote_count,
        "user_vote": user_vote,
        "tier": build.tier,
    }


def get_user_vote(build_id: str, user_id: str) -> int:
    """Returns the user's current vote direction (0 if none)."""
    vote = Vote.query.filter_by(user_id=user_id, build_id=build_id).first()
    return vote.direction if vote else 0


# ---------------------------------------------------------------------------
# Meta stats
# ---------------------------------------------------------------------------

def simulate_build(build: Build) -> dict:
    """Delegate to build_analysis_service for the full simulation pipeline."""
    from app.services.build_analysis_service import analyze_build
    return analyze_build(build)



def meta_snapshot() -> dict:
    """Aggregate stats for the meta tracker sidebar."""
    from sqlalchemy import func

    _empty = {
        "total_builds": 0,
        "most_played_class": "N/A",
        "top_mastery": "N/A",
        "class_distribution": [],
        "s_tier_builds": [],
    }

    try:
        total = Build.query.filter_by(is_public=True).count()

        class_counts = (
            db.session.query(Build.character_class, func.count(Build.id))
            .filter_by(is_public=True)
            .group_by(Build.character_class)
            .order_by(desc(func.count(Build.id)))
            .all()
        )

        most_played = class_counts[0][0] if class_counts else "N/A"

        top_mastery = (
            db.session.query(Build.mastery, func.count(Build.id))
            .filter_by(is_public=True)
            .group_by(Build.mastery)
            .order_by(desc(func.count(Build.id)))
            .first()
        )

        s_tier = (
            Build.query.filter_by(tier="S", is_public=True)
            .order_by(desc(Build.vote_count))
            .limit(5)
            .all()
        )

        return {
            "total_builds": total,
            "most_played_class": most_played,
            "top_mastery": top_mastery[0] if top_mastery else "N/A",
            "class_distribution": [
                {"class": cls, "count": cnt} for cls, cnt in class_counts
            ],
            "s_tier_builds": [
                {"id": b.id, "slug": b.slug, "name": b.name, "mastery": b.mastery}
                for b in s_tier
            ],
        }
    except Exception:
        return _empty