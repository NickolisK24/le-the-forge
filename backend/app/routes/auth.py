"""
Auth Blueprint — /api/auth

GET  /api/auth/discord              → Redirects to Discord OAuth page
GET  /api/auth/discord/authorized   → OAuth callback; issues JWT; redirects to frontend
GET  /api/auth/me                   → Returns current user profile
POST /api/auth/logout               → Client-side token discard (stateless)
GET  /api/auth/dev-login            → Dev-only bypass (FLASK_ENV=development only)
"""

import requests as _requests

from flask import Blueprint, redirect, current_app, request

from app import limiter
from app.utils.auth import (
    upsert_user_from_discord,
    issue_token,
    login_required,
    get_current_user,
)
from app.utils.responses import ok, unauthorized
from app.schemas import UserSchema

auth_bp = Blueprint("auth", __name__)
user_schema = UserSchema()


@auth_bp.get("/discord")
@limiter.limit("20 per minute")
def discord_login():
    """
    Initiates Discord OAuth2 PKCE flow.
    In production, replace with actual Flask-Dance OAuth redirect.

    If Discord credentials aren't configured (e.g. local dev without a
    client ID), fail silently by redirecting back to the frontend without
    any error params — no toast should fire in that case.
    """
    client_id = current_app.config.get("DISCORD_CLIENT_ID") or ""
    redirect_uri = current_app.config.get("DISCORD_REDIRECT_URI") or ""
    frontend_url = current_app.config["FRONTEND_URL"]
    if not client_id or not redirect_uri:
        current_app.logger.info(
            "Discord login unavailable: DISCORD_CLIENT_ID or DISCORD_REDIRECT_URI not configured."
        )
        return redirect(frontend_url)
    scope = "identify"
    url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
    )
    return redirect(url)


@auth_bp.get("/discord/authorized")
@limiter.limit("20 per minute")
def discord_authorized():
    """
    OAuth2 callback. Full flow:
      1. Receive ?code= from Discord
      2. POST to Discord token endpoint to exchange code → access token
      3. GET /users/@me with that access token to fetch the Discord profile
      4. Upsert our User row from the profile
      5. Issue a signed JWT and redirect to the frontend with it
    """
    code = request.args.get("code")
    if not code:
        current_app.logger.warning("Discord OAuth callback received no code.")
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=no_code")

    redirect_uri = current_app.config["DISCORD_REDIRECT_URI"]

    # ── 1. Exchange authorization code for access token ──────────────────
    try:
        token_response = _requests.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id":     current_app.config["DISCORD_CLIENT_ID"],
                "client_secret": current_app.config["DISCORD_CLIENT_SECRET"],
                "grant_type":    "authorization_code",
                "code":          code,
                "redirect_uri":  redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except _requests.exceptions.ConnectionError as exc:
        current_app.logger.error("Discord token exchange failed: ConnectionError: %s", exc)
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=discord_unreachable")
    except _requests.exceptions.Timeout:
        current_app.logger.error("Discord token exchange timed out")
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=discord_timeout")
    except Exception as exc:
        current_app.logger.error("Discord token exchange unexpected error (%s): %s", type(exc).__name__, exc)
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=token_exchange")

    if not token_response.ok:
        current_app.logger.error(
            "Discord token exchange failed: %s %s",
            token_response.status_code,
            token_response.text,
        )
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=token_exchange")

    discord_token = token_response.json().get("access_token")
    if not discord_token:
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=no_access_token")

    # ── 2. Fetch Discord user profile ─────────────────────────────────────
    try:
        profile_response = _requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {discord_token}"},
            timeout=10,
        )
    except _requests.exceptions.ConnectionError as exc:
        current_app.logger.error("Discord profile fetch failed: ConnectionError: %s", exc)
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=discord_unreachable")
    except _requests.exceptions.Timeout:
        current_app.logger.error("Discord profile fetch timed out")
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=discord_timeout")
    except Exception as exc:
        current_app.logger.error("Discord profile fetch unexpected error (%s): %s", type(exc).__name__, exc)
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=profile_fetch")

    if not profile_response.ok:
        current_app.logger.error(
            "Discord profile fetch failed: %s %s",
            profile_response.status_code,
            profile_response.text,
        )
        return redirect(current_app.config["FRONTEND_URL"] + "?auth=failed&reason=profile_fetch")

    discord_user = profile_response.json()

    # ── 3. Upsert user + issue JWT ────────────────────────────────────────
    user = upsert_user_from_discord(discord_user)
    jwt_token = issue_token(user)

    current_app.logger.info("User %s authenticated via Discord.", user.username)
    return redirect(
        f"{current_app.config['FRONTEND_URL']}/auth/callback?token={jwt_token}"
    )


@auth_bp.get("/dev-login")
def dev_login():
    """
    Development-only login bypass — skips Discord OAuth entirely.
    Issues a JWT for the first user in the DB (or creates a placeholder dev user).
    ONLY available when FLASK_ENV=development. Returns 404 in production.
    """
    from flask import current_app
    if not current_app.debug:
        from app.utils.responses import not_found
        return not_found()

    from app import db
    from app.models import User

    user = User.query.first()
    if not user:
        # Create a dev placeholder user if none exists
        user = User(
            discord_id="dev-local-000000000",
            username="DevUser",
            discriminator="0",
            avatar_url=None,
        )
        db.session.add(user)
        db.session.commit()

    jwt_token = issue_token(user)
    current_app.logger.info("Dev login issued for user %s", user.username)
    return redirect(
        f"{current_app.config['FRONTEND_URL']}/auth/callback?token={jwt_token}"
    )


@auth_bp.get("/me")
@login_required
def me():
    user = get_current_user()
    if not user:
        return unauthorized()
    return ok(data=user_schema.dump(user))


@auth_bp.post("/logout")
def logout():
    # JWT is stateless — client discards the token.
    # If we add token revocation (Redis blocklist), it goes here.
    return ok(data={"message": "Logged out."})