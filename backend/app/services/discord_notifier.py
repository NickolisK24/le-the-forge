"""
Discord Webhook Notifier — posts alerts for import failures.

Reads DISCORD_IMPORT_WEBHOOK_URL from the environment.
If the URL is not set or the request fails, logs a warning and continues —
never crashes or affects the user-facing response.
"""

import json
import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("DISCORD_IMPORT_WEBHOOK_URL", "")

COLOR_RED = 0xFF0000
COLOR_ORANGE = 0xFF8C00

# Discord embed field value limit
_FIELD_LIMIT = 1024
# Discord total embed character limit
_EMBED_LIMIT = 5800


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


def _summarize_partial_data(partial_data: dict | None) -> str:
    """Summarize what DID parse successfully from partial_data."""
    if not partial_data:
        return "No data parsed"
    parts = []
    if partial_data.get("character_class"):
        parts.append(f"Class: {partial_data['character_class']}")
    if partial_data.get("mastery"):
        parts.append(f"Mastery: {partial_data['mastery']}")
    skills = partial_data.get("skills", [])
    if skills:
        parts.append(f"Skills: {len(skills) if isinstance(skills, list) else skills}")
    passives = partial_data.get("passive_tree", partial_data.get("passives"))
    if passives:
        parts.append(f"Passives: {len(passives) if isinstance(passives, (list, dict)) else passives}")
    gear = partial_data.get("gear", [])
    if gear:
        parts.append(f"Gear slots: {len(gear) if isinstance(gear, list) else gear}")
    return ", ".join(parts) if parts else "No fields parsed"


def _extract_raw_gear(partial_data: dict | None) -> str:
    """Extract raw gear entries for debugging ID mapping issues."""
    if not partial_data:
        return "No gear data"
    gear = partial_data.get("gear", partial_data.get("raw_gear", []))
    if not gear:
        return "No gear entries"
    # Show first 3 entries for debugging
    entries = gear[:3]
    try:
        raw = json.dumps(entries, indent=1, ensure_ascii=False)
    except (TypeError, ValueError):
        raw = str(entries)
    if len(raw) > _FIELD_LIMIT - 50:
        raw = raw[:_FIELD_LIMIT - 80] + "\n... (truncated for length)"
    if len(gear) > 3:
        raw += f"\n\n+{len(gear) - 3} more entries"
    return f"```json\n{raw}\n```"


def _post_alert(failure, severity: str) -> None:
    """Actual webhook POST — runs in a daemon thread."""
    color = COLOR_RED if severity == "hard" else COLOR_ORANGE
    title = f"Import Failure — {failure.source}"
    if severity == "partial":
        title = f"Partial Import — {failure.source}"

    fields = [
        {"name": "Source", "value": failure.source or "unknown", "inline": True},
        {"name": "URL", "value": failure.raw_url or "N/A", "inline": False},
        {
            "name": "Missing Fields",
            "value": ", ".join(failure.missing_fields) if failure.missing_fields else "None",
            "inline": True,
        },
        {
            "name": "Parsed Data",
            "value": _summarize_partial_data(failure.partial_data),
            "inline": False,
        },
        {
            "name": "Error",
            "value": (failure.error_message or "—")[:_FIELD_LIMIT],
            "inline": False,
        },
    ]

    # Add raw gear data for debugging gear import issues
    raw_gear = _extract_raw_gear(failure.partial_data)
    if raw_gear not in ("No gear data", "No gear entries"):
        fields.append({
            "name": "Raw Gear Data (first 3 entries)",
            "value": raw_gear,
            "inline": False,
        })

    if failure.user_id:
        fields.append({"name": "User", "value": str(failure.user_id), "inline": True})
    else:
        fields.append({"name": "User", "value": "anonymous", "inline": True})

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
