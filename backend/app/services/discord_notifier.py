"""
Discord Webhook Notifier — posts alerts for import failures.

Reads DISCORD_IMPORT_WEBHOOK_URL from the environment.
If the URL is not set or the request fails, logs a warning and continues —
never crashes or affects the user-facing response.

The embed summarises the structured ImportFailure.diagnostics record (stage,
HTTP status, safe upstream headers, missing-field evaluation state, versions).
It never includes raw build payloads; those stay in the admin-only record.
"""

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

    # Snapshot all needed fields now, while still in the app/session context.
    # After db.session.commit() the ORM expires the object; accessing attributes
    # in a background thread would trigger a lazy DB load with no app context.
    snapshot = {
        "id": getattr(failure, "id", None),
        "source": failure.source,
        "raw_url": failure.raw_url,
        "missing_fields": list(failure.missing_fields or []),
        "partial_data": failure.partial_data,
        "error_message": failure.error_message,
        "user_id": failure.user_id,
        "created_at": getattr(failure, "created_at", None),
        "diagnostics": getattr(failure, "diagnostics", None),
    }

    # Fire in a background thread so we never block the response
    thread = threading.Thread(
        target=_post_alert,
        args=(snapshot, severity),
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


def _summarize_gear_slots(partial_data: dict | None) -> str | None:
    """Slot names and affix counts for the first few gear entries — enough to
    debug mapping without copying the imported build into Discord."""
    if not isinstance(partial_data, dict):
        return None
    gear = partial_data.get("gear", partial_data.get("raw_gear", []))
    if not isinstance(gear, list) or not gear:
        return None
    parts = []
    for entry in gear[:3]:
        if isinstance(entry, dict):
            affixes = entry.get("affixes")
            count = len(affixes) if isinstance(affixes, list) else affixes
            parts.append(f"{entry.get('slot', '?')} ({count if count is not None else 0} affixes)")
    summary = ", ".join(parts) or "unrecognised gear entries"
    if len(gear) > 3:
        summary += f"; +{len(gear) - 3} more"
    return summary[:_FIELD_LIMIT]


def _missing_fields_value(state: str | None, missing: list) -> str:
    if state == "NOT_EVALUATED" or (state is None and not missing):
        return "Not evaluated — parsing did not complete"
    if not missing:
        return "None missing"
    value = ", ".join(str(m) for m in missing)
    if len(value) > _FIELD_LIMIT - 40:
        value = value[:_FIELD_LIMIT - 60] + f"… ({len(missing)} total)"
    return value


def _post_alert(failure: dict, severity: str) -> None:
    """Actual webhook POST — runs in a daemon thread. Receives a plain dict snapshot."""
    color = COLOR_RED if severity == "hard" else COLOR_ORANGE
    source = failure.get("source") or "unknown"
    title = f"Import Failure — {source}" if severity == "hard" else f"Partial Import — {source}"

    missing = failure.get("missing_fields") or []
    diag = failure.get("diagnostics") or {}
    stage = diag.get("failure_stage") or "unknown"
    parsing_started = diag.get("parsing_started")
    fields = [
        {"name": "Source", "value": source, "inline": True},
        {"name": "Stage", "value": stage, "inline": True},
        {"name": "Category", "value": diag.get("error_category") or "unknown", "inline": True},
        {"name": "URL", "value": (failure.get("raw_url") or "N/A")[:_FIELD_LIMIT], "inline": False},
    ]
    if diag.get("http_status") is not None:
        fields.append({"name": "HTTP Status", "value": str(diag["http_status"]), "inline": True})
    upstream = diag.get("upstream_headers") or {}
    if upstream:
        value = ", ".join(f"{k}: {v}" for k, v in upstream.items())
        fields.append({"name": "Upstream", "value": value[:_FIELD_LIMIT], "inline": False})
    fields.append({
        "name": "Missing Fields",
        "value": _missing_fields_value(diag.get("missing_field_state"), missing),
        "inline": False,
    })
    parsed_value = (
        f"Not attempted (failed at {stage})"
        if parsing_started is False
        else _summarize_partial_data(failure.get("partial_data"))
    )
    fields.append({"name": "Parsed Data", "value": parsed_value[:_FIELD_LIMIT], "inline": False})
    fields.append({
        "name": "Error",
        "value": (failure.get("error_message") or "—")[:_FIELD_LIMIT],
        "inline": False,
    })

    gear_slots = _summarize_gear_slots(failure.get("partial_data"))
    if gear_slots:
        fields.append({"name": "Gear Slots (first 3)", "value": gear_slots, "inline": False})

    # Add raw top-level keys when present — critical for diagnosing
    # unknown Maxroll data shapes where expected fields are empty.
    partial = failure.get("partial_data") or {}
    raw_keys = partial.get("raw_keys") if isinstance(partial, dict) else None
    if raw_keys:
        value = ", ".join(str(k) for k in raw_keys)[:_FIELD_LIMIT]
        fields.append({
            "name": "Raw Top-Level Keys",
            "value": f"`{value}`" if value else "(empty)",
            "inline": False,
        })

    if diag:
        versions = (
            f"app {diag.get('app_version', 'unknown')} ({str(diag.get('app_commit', 'unknown'))[:12]}), "
            f"data {diag.get('data_version', 'unknown')}, "
            f"extractor {diag.get('extractor_version', 'unknown')}"
        )
        fields.append({"name": "Versions", "value": versions[:_FIELD_LIMIT], "inline": False})
        fields.append({"name": "Replay", "value": str(diag.get("replay", "unknown")), "inline": True})
    if failure.get("id"):
        fields.append({"name": "Failure ID", "value": str(failure["id"]), "inline": True})

    user_id = failure.get("user_id")
    fields.append({"name": "User", "value": str(user_id) if user_id else "anonymous", "inline": True})

    created_at = failure.get("created_at")
    embed = {
        "title": title,
        "color": color,
        "fields": fields,
        "footer": {"text": "The Forge Import System"},
        "timestamp": created_at.isoformat() if hasattr(created_at, "isoformat") else None,
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
            logger.info("discord_notifier: alert sent for failure id=%s", failure.get("id"))
    except Exception as exc:
        logger.error("discord_notifier: webhook POST failed: %s", exc)
