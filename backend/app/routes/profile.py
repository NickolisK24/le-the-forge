"""
Profile Blueprint — /api/profile

GET  /api/profile          → Current user's full profile (builds, sessions, stats)
GET  /api/profile/builds   → Paginated list of user's own builds (incl. private)
GET  /api/profile/sessions → Paginated list of user's craft sessions
"""

from flask import Blueprint, request
from sqlalchemy import desc

from app import db
from app.models import Build, CraftSession, Vote
from app.schemas import BuildListSchema, CraftSessionSchema
from app.services.build_service import list_builds
from app.utils.auth import login_required, get_current_user
from app.utils.responses import ok, paginate_meta

profile_bp = Blueprint("profile", __name__)

build_list_schema = BuildListSchema(many=True)
session_schema = CraftSessionSchema(many=True)


@profile_bp.get("")
@login_required
def get_profile():
    user = get_current_user()

    # Aggregate stats
    total_builds = Build.query.filter_by(author_id=user.id).count()
    total_sessions = CraftSession.query.filter_by(user_id=user.id).count()

    # Recent builds (last 5)
    recent_builds = (
        Build.query
        .filter_by(author_id=user.id)
        .order_by(desc(Build.created_at))
        .limit(5)
        .all()
    )

    # Recent sessions (last 5)
    recent_sessions = (
        CraftSession.query
        .filter_by(user_id=user.id)
        .order_by(desc(CraftSession.created_at))
        .limit(5)
        .all()
    )

    return ok(data={
        "user": {
            "id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat(),
        },
        "stats": {
            "total_builds": total_builds,
            "total_sessions": total_sessions,
        },
        "recent_builds": build_list_schema.dump(recent_builds),
        "recent_sessions": [
            {
                "id": s.id,
                "slug": s.slug,
                "item_type": s.item_type,
                "item_name": s.item_name,
                "instability": s.instability,
                "is_fractured": s.is_fractured,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent_sessions
        ],
    })


@profile_bp.get("/builds")
@login_required
def profile_builds():
    user = get_current_user()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    builds, total, pages = list_builds(
        page=page,
        per_page=per_page,
        author_id=user.id,
        include_private=True,
        sort=request.args.get("sort", "new"),
    )
    return ok(
        data=build_list_schema.dump(builds),
        meta=paginate_meta(page, per_page, total, pages),
    )



@profile_bp.get("/sessions")
@login_required
def profile_sessions():
    user = get_current_user()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    q = (
        CraftSession.query
        .filter_by(user_id=user.id)
        .order_by(desc(CraftSession.created_at))
    )
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)

    return ok(
        data=[
            {
                "id": s.id,
                "slug": s.slug,
                "item_type": s.item_type,
                "item_name": s.item_name,
                "instability": s.instability,
                "forge_potential": s.forge_potential,
                "is_fractured": s.is_fractured,
                "step_count": len(list(s.steps)),
                "created_at": s.created_at.isoformat(),
            }
            for s in pagination.items
        ],
        meta=paginate_meta(page, per_page, pagination.total, pagination.pages),
    )