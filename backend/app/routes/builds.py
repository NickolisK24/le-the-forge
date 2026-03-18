"""
Builds Blueprint — /api/builds

GET    /api/builds                 → Paginated list with filters
POST   /api/builds                 → Create build (auth optional — anon builds allowed)
GET    /api/builds/<slug>          → Get single build (increments view_count)
PATCH  /api/builds/<slug>          → Update build (owner only)
DELETE /api/builds/<slug>          → Delete build (owner only)
POST   /api/builds/<slug>/vote     → Cast or toggle vote (auth required)
GET    /api/builds/meta/snapshot   → Aggregate meta stats
"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models import Build
from app.schemas import (
    BuildSchema,
    BuildListSchema,
    BuildCreateSchema,
    BuildUpdateSchema,
    VoteSchema,
)
from app.services import build_service
from app.utils.auth import login_required, get_current_user
from app.utils.responses import (
    ok, created, no_content, error,
    not_found, forbidden, validation_error,
    paginate_meta,
)

builds_bp = Blueprint("builds", __name__)

build_schema = BuildSchema()
build_list_schema = BuildListSchema(many=True)
build_create_schema = BuildCreateSchema()
build_update_schema = BuildUpdateSchema()
vote_schema = VoteSchema()


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

@builds_bp.get("")
def list_builds():
    args = request.args

    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
    except (TypeError, ValueError):
        return error("page and per_page must be integers.")

    # Boolean filter coercion
    def _bool(key):
        v = args.get(key)
        if v is None:
            return None
        return v.lower() in ("1", "true", "yes")

    builds, total, pages = build_service.list_builds(
        page=page,
        per_page=per_page,
        character_class=args.get("class"),
        mastery=args.get("mastery"),
        tier=args.get("tier"),
        is_ssf=_bool("ssf"),
        is_hc=_bool("hc"),
        is_ladder_viable=_bool("ladder"),
        is_budget=_bool("budget"),
        cycle=args.get("cycle"),
        sort=args.get("sort", "votes"),
        search=args.get("q"),
    )

    return ok(
        data=build_list_schema.dump(builds),
        meta=paginate_meta(page, per_page, total, pages),
    )


# ---------------------------------------------------------------------------
# Meta snapshot (before <slug> routes to avoid "meta" matching as slug)
# ---------------------------------------------------------------------------

@builds_bp.get("/meta/snapshot")
def meta_snapshot():
    return ok(data=build_service.meta_snapshot())


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@builds_bp.post("")
def create_build():
    try:
        data = build_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    user = get_current_user()
    build = build_service.create_build(data, user_id=user.id if user else None)
    return created(data=build_schema.dump(build))


# ---------------------------------------------------------------------------
# Single build
# ---------------------------------------------------------------------------

@builds_bp.get("/<slug>")
def get_build(slug: str):
    build = build_service.get_build(slug, increment_views=True)
    if not build:
        return not_found("Build")

    result = build_schema.dump(build)

    user = get_current_user()
    if user:
        result["user_vote"] = build_service.get_user_vote(build.id, user.id)
    else:
        result["user_vote"] = 0

    return ok(data=result)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@builds_bp.patch("/<slug>")
@login_required
def update_build(slug: str):
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    user = get_current_user()
    if build.author_id and build.author_id != user.id:
        return forbidden()

    try:
        data = build_update_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    build = build_service.update_build(build, data)
    return ok(data=build_schema.dump(build))


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@builds_bp.delete("/<slug>")
@login_required
def delete_build(slug: str):
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    user = get_current_user()
    if build.author_id and build.author_id != user.id:
        return forbidden()

    build_service.delete_build(build)
    return no_content()


# ---------------------------------------------------------------------------
# Vote
# ---------------------------------------------------------------------------

@builds_bp.post("/<slug>/simulate")
def simulate_build(slug: str):
    """
    Run the full simulation pipeline for a build.
    Returns DPS, defense, stat aggregation, and upgrade recommendations.
    No authentication required.
    """
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")
    result = build_service.simulate_build(build)
    return ok(data=result)


@builds_bp.post("/<slug>/vote")
@login_required
def vote(slug: str):
    build = Build.query.filter_by(slug=slug).first()
    if not build:
        return not_found("Build")

    try:
        data = vote_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    user = get_current_user()
    result = build_service.cast_vote(build, user.id, data["direction"])
    return ok(data=result)
