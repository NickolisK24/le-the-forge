"""
Discord Webhook Notifier — posts alerts for import failures.

Reads DISCORD_IMPORT_WEBHOOK_URL from the environment.
If the URL is not set or the request fails, logs a warning and continues —
never crashes or affects the user-facing response.
"""

import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("DISCORD_IMPORT_WEBHOOK_URL", "")

COLOR_RED = 0xFF0000
COLOR_ORANGE = 0xFF8C00


def send_import_failure_alert(failure, severity: str = "hard") -> None:
    """
    Post a formatted embed to the Discord webhook.

    Args:
        failure: An ImportFailure model instance.
        severity: "hard" (red) or "partial" (orange).
    """
    if not WEBHOOK_URL:
        logger.warning(
            "discord_notifier: DISCORD_IMPORT_WEBHOOK_URL not set — skipping alert "
            "for import failure id=%s",
            getattr(failure, "id", "?"),
        )
        return

    # Fire in a background thread so we never block the response
    thread = threading.Thread(
        target=_post_alert,
        args=(failure, severity),
        daemon=True,
    )
    thread.start()


def _post_alert(failure, severity: str) -> None:
    """Actual webhook POST — runs in a daemon thread."""
    color = COLOR_RED if severity == "hard" else COLOR_ORANGE
    title = f"Import Failure — {failure.source}"
    if severity == "partial":
        title = f"Partial Import — {failure.source}"

    fields = [
        {"name": "URL", "value": failure.raw_url or "N/A", "inline": False},
        {
            "name": "Missing Fields",
            "value": ", ".join(failure.missing_fields) if failure.missing_fields else "None",
            "inline": True,
        },
        {
            "name": "Error",
            "value": (failure.error_message or "—")[:1024],
            "inline": False,
        },
    ]

    if failure.user_id:
        fields.append({"name": "User ID", "value": failure.user_id, "inline": True})

    embed = {
        "title": title,
        "color": color,
        "fields": fields,
        "footer": {"text": "The Forge Import System"},
        "timestamp": (
            failure.created_at.isoformat()
            if hasattr(failure, "created_at") and failure.created_at
            else None
        ),
    }

    payload = {"embeds": [embed]}

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code >= 400:
            logger.error(
                "discord_notifier: webhook returned %s: %s",
                resp.status_code,
                resp.text[:200],
            )
        else:
            logger.info("discord_notifier: alert sent for failure id=%s", failure.id)
    except Exception as exc:
        logger.error("discord_notifier: webhook POST failed: %s", exc)
