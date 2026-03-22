"""
Auth utilities.

Flow:
  1. Frontend redirects user to /api/auth/discord
  2. OAuth callback at /api/auth/discord/authorized handles the exchange
  3. We upsert the User from Discord profile data
  4. We issue a signed JWT and redirect to the frontend with it
  5. Frontend stores JWT in memory (not localStorage) and sends via Authorization header

The JWT contains: { sub: user_id, username: str }

NOTE: Do NOT import from app.utils.responses at module level here.
auth.py lives inside app/utils/ — a top-level import from the same
package causes a circular import. All response helpers are imported
locally inside the functions that need them.
"""

import os
from functools import wraps

from flask import current_app, redirect, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request,
)

from app import db
from app.models import User


def upsert_user_from_discord(discord_data: dict) -> User:
    """
    Create or update a User from Discord OAuth profile data.
    discord_data should include: id, username, discriminator, avatar
    """
    discord_id = str(discord_data["id"])
    user = User.query.filter_by(discord_id=discord_id).first()

    avatar_hash = discord_data.get("avatar")
    avatar_url = (
        f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png"
        if avatar_hash
        else None
    )

    if user:
        user.username = discord_data.get("username", user.username)
        user.discriminator = discord_data.get("discriminator")
        user.avatar_url = avatar_url
    else:
        user = User(
            discord_id=discord_id,
            username=discord_data["username"],
            discriminator=discord_data.get("discriminator"),
            avatar_url=avatar_url,
        )
        db.session.add(user)

    db.session.commit()
    return user


def issue_token(user: User) -> str:
    return create_access_token(
        identity=user.id,
        additional_claims={"username": user.username},
    )


def get_current_user() -> User | None:
    """Returns the authenticated User or None if no valid JWT."""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if not user_id:
            return None
        return db.session.get(User, user_id)
    except Exception:
        return None


def login_required(f):
    """Route decorator — returns 401 if no valid JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.utils.responses import unauthorized
        try:
            verify_jwt_in_request()
        except Exception:
            return unauthorized()
        return f(*args, **kwargs)
    return decorated


def owner_required(get_resource_fn):
    """
    Decorator factory for routes that require ownership.

    Usage:
        @owner_required(lambda: Build.query.get(build_id))
        def delete_build(build_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return unauthorized()

            user_id = get_jwt_identity()
            resource = get_resource_fn()
            if not resource:
                from app.utils.responses import not_found
                return not_found()
            if getattr(resource, "author_id", None) != user_id:
                from app.utils.responses import forbidden
                return forbidden()
            return f(*args, **kwargs)
        return decorated
    return decorator