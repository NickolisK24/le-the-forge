"""
Build access policy — the single place that decides who may read or change a
build. Every route that loads a build by slug goes through these helpers.

Rules:
  Public build  (is_public=True)  → anyone may read; only the owner may change.
  Private build (owned)           → only the owner may read or change.
  Anonymous build (author_id None) → read-only for everyone. Readable by
      whoever holds the slug (imports and anonymous saves rely on that link);
      new private anonymous builds get an unguessable slug. Nobody can update
      or delete one through the API until an anonymous edit-token lifecycle
      exists.

An unreadable build is reported as 404 so private slugs are not confirmed.
"""

from __future__ import annotations

from typing import Optional, Tuple

from app.models import Build, User
from app.services import build_service
from app.utils.auth import get_current_user
from app.utils.responses import error, forbidden, not_found, unauthorized

ANONYMOUS_READ_ONLY_MESSAGE = (
    "Anonymous builds are read-only. Sign in and save a copy to make changes."
)


def is_owner(build: Build, user: Optional[User]) -> bool:
    return (
        user is not None
        and build.author_id is not None
        and build.author_id == user.id
    )


def can_read_build(build: Build, user: Optional[User]) -> bool:
    if build.is_public or build.author_id is None:
        return True
    return is_owner(build, user)


def can_modify_build(build: Build, user: Optional[User]) -> bool:
    return is_owner(build, user)


def load_readable_build(slug: str, *, label: str = "Build",
                        increment_views: bool = False) -> Tuple[Optional[Build], object]:
    """Return (build, None) when the current requester may read it, otherwise
    (None, error_response)."""
    build = build_service.get_build(slug)
    if build is None or not can_read_build(build, get_current_user()):
        return None, not_found(label)
    if increment_views:
        build_service.increment_view_count(build)
    return build, None


def load_modifiable_build(slug: str) -> Tuple[Optional[Build], object]:
    """Return (build, None) when the current requester owns the build,
    otherwise (None, error_response): 404 unreadable, 401 anonymous on an owned
    build, 403 for non-owners and for anonymous builds."""
    build = build_service.get_build(slug)
    user = get_current_user()
    if build is None or not can_read_build(build, user):
        return None, not_found("Build")
    if build.author_id is None:
        return None, error(ANONYMOUS_READ_ONLY_MESSAGE, 403)
    if user is None:
        return None, unauthorized()
    if not is_owner(build, user):
        return None, forbidden()
    return build, None
