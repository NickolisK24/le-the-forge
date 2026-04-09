"""
Import Blueprint — /api/import

POST /api/import/url    → Proxy-fetch a Last Epoch Tools build URL and return
                          a mapped build payload ready to be reviewed / saved.
POST /api/import/build  → Parse URL (LET or Maxroll), validate, save build, track failures.
"""

import json as json_lib
import logging
import os
import re
import traceback
from typing import Dict, List, Optional

import requests as _requests
from flask import Blueprint, current_app, request

from app import db, limiter
from app.models import ImportFailure
from app.services import build_service
from app.services.importers import get_importer, detect_source, ImportResult
from app.services.discord_notifier import send_import_failure_alert
from app.utils.auth import get_current_user
from app.utils.responses import ok, error as err_response

import_bp = Blueprint("import", __name__)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Last Epoch class / mastery ID maps
# These mirror the internal game enum values used by Last Epoch Tools.
# ---------------------------------------------------------------------------
_CLASS_MAP: Dict[int, str] = {
    0: "Primalist",
    1: "Mage",
    2: "Sentinel",
    3: "Acolyte",
    4: "Rogue",
}

_MASTERY_MAP: Dict[str, Dict[int, str]] = {
    "Primalist": {1: "Beastmaster", 2: "Shaman",      3: "Druid"},
    "Mage":      {1: "Sorcerer",    2: "Spellblade",  3: "Runemaster"},
    "Sentinel":  {1: "Void Knight", 2: "Forge Guard", 3: "Paladin"},
    "Acolyte":   {1: "Necromancer", 2: "Lich",        3: "Warlock"},
    "Rogue":     {1: "Bladedancer", 2: "Marksman",    3: "Falconer"},
}

# ---------------------------------------------------------------------------
# Skill tree ID → display name (built lazily from data/skills_metadata.json)
# ---------------------------------------------------------------------------
_SKILL_ID_TO_NAME: Optional[Dict[str, str]] = None


def _get_skill_id_map() -> Dict[str, str]:
    """Return {treeID: skill_name} built from data/skills_metadata.json."""
    global _SKILL_ID_TO_NAME
    if _SKILL_ID_TO_NAME is not None:
        return _SKILL_ID_TO_NAME

    try:
        # Project layout: project_root/data/ and project_root/backend/app/
        # current_app.root_path = .../backend/app
        # go up two levels to reach project root
        project_root = os.path.dirname(os.path.dirname(current_app.root_path))
        data_path = os.path.join(project_root, "data", "classes", "skills_metadata.json")
        with open(data_path) as f:
            skills_data: dict = json_lib.load(f)
        _SKILL_ID_TO_NAME = {
            v["id"]: v["name"]
            for v in skills_data.values()
            if isinstance(v, dict) and "id" in v and "name" in v
        }
        logger.info(
            "import: loaded %d skill ID mappings from %s",
            len(_SKILL_ID_TO_NAME), data_path,
        )
    except Exception as exc:
        logger.warning("import: could not load skill ID map: %s", exc)
        _SKILL_ID_TO_NAME = {}

    return _SKILL_ID_TO_NAME


# ---------------------------------------------------------------------------
# HTML extraction — structure-aware JSON parsing
# ---------------------------------------------------------------------------

def _extract_build_info(html: str) -> Optional[dict]:
    """
    Extract the build JSON object embedded in a Last Epoch Tools planner page.

    Tries multiple extraction strategies:
    1. window["buildInfo"] = {...}  (classic LE Tools format)
    2. __NEXT_DATA__ script tag     (Next.js SSR format)
    3. Fallback script tag scan     (look for any JSON with bio/charTree)
    """
    # Method 1: window["buildInfo"] or window.buildInfo assignment
    assignment_re = re.search(
        r'window\s*(?:\[\s*["\']buildInfo["\']\s*\]|\.buildInfo)\s*=\s*',
        html,
    )
    if assignment_re:
        start = assignment_re.end()
        while start < len(html) and html[start] in " \t\r\n":
            start += 1
        try:
            decoder = json_lib.JSONDecoder()
            obj, _ = decoder.raw_decode(html, start)
            if isinstance(obj, dict):
                logger.info("import/url: extracted buildInfo via window assignment")
                return obj
        except json_lib.JSONDecodeError as exc:
            logger.warning("import/url: buildInfo assignment found but JSON decode failed: %s", exc)

    # Method 2: __NEXT_DATA__ (Next.js SSR)
    next_data_re = re.search(
        r'<script\s+id="__NEXT_DATA__"\s+type="application/json">\s*',
        html,
    )
    if next_data_re:
        start = next_data_re.end()
        end = html.find("</script>", start)
        if end > start:
            try:
                next_data = json_lib.loads(html[start:end])
                page_props = next_data.get("props", {}).get("pageProps", {})
                if "buildInfo" in page_props:
                    logger.info("import/url: extracted buildInfo via __NEXT_DATA__")
                    return page_props["buildInfo"]
                if "build" in page_props:
                    logger.info("import/url: extracted build via __NEXT_DATA__")
                    return page_props["build"]
                if page_props.get("bio") or page_props.get("charTree"):
                    logger.info("import/url: extracted build from __NEXT_DATA__ pageProps")
                    return page_props
                logger.warning(
                    "import/url: __NEXT_DATA__ found but no buildInfo. pageProps keys: %s",
                    list(page_props.keys()),
                )
            except json_lib.JSONDecodeError as exc:
                logger.warning("import/url: __NEXT_DATA__ JSON decode failed: %s", exc)

    # Method 3: Fallback — scan all script tags for JSON with bio/charTree
    for match in re.finditer(r'<script[^>]*>\s*', html):
        script_start = match.end()
        script_end = html.find("</script>", script_start)
        if script_end < 0:
            continue
        script_content = html[script_start:script_end].strip()
        if not script_content.startswith("{"):
            json_match = re.search(r'=\s*(\{)', script_content)
            if not json_match:
                continue
            script_content = script_content[json_match.start(1):]
        if len(script_content) < 50:
            continue
        try:
            obj, _ = json_lib.JSONDecoder().raw_decode(script_content)
            if isinstance(obj, dict) and ("bio" in obj or "charTree" in obj):
                logger.info("import/url: extracted build data via fallback script scan")
                return obj
        except (json_lib.JSONDecodeError, ValueError):
            continue

    logger.warning("import/url: no build data found in HTML (%d bytes)", len(html))
    return None


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _map_let_build(build_info: dict) -> dict:
    """
    Map a Last Epoch Tools build JSON to The Forge BuildCreatePayload format.

    LE Tools schema (relevant fields):
        bio.level           int
        bio.characterClass  int  (0–4)
        bio.chosenMastery   int  (1–3)
        charTree.selected   {nodeId: pts}
        skillTrees[]        [{treeID, selected, level, slotNumber}]
        hud                 [treeID × 5]   — HUD slot order
    """
    bio = build_info.get("bio", {})
    char_class_id = int(bio.get("characterClass", 0))
    mastery_id = int(bio.get("chosenMastery", 0))
    level = int(bio.get("level", 70))

    char_class = _CLASS_MAP.get(char_class_id, "Sentinel")
    mastery = _MASTERY_MAP.get(char_class, {}).get(mastery_id, "")

    # ---- Passive tree -------------------------------------------------------
    char_tree = build_info.get("charTree", {})
    selected_nodes: dict = char_tree.get("selected", {})
    passive_tree: List[int] = []
    for node_id_str, pts in selected_nodes.items():
        try:
            passive_tree.extend([int(node_id_str)] * max(0, int(pts)))
        except (ValueError, TypeError):
            pass

    # ---- Skills -------------------------------------------------------------
    skill_id_map = _get_skill_id_map()
    skill_trees_raw: List[dict] = build_info.get("skillTrees", [])
    hud: List[str] = build_info.get("hud", [])

    skills: List[dict] = []
    for st in skill_trees_raw:
        tree_id: str = st.get("treeID", "")
        if not tree_id:
            continue

        skill_name = skill_id_map.get(tree_id, tree_id)

        if tree_id in hud:
            slot = hud.index(tree_id)
        else:
            slot = int(st.get("slotNumber", len(skills)))

        selected_spec: dict = st.get("selected", {})
        spec_tree: List[int] = []
        for node_id_str, pts in selected_spec.items():
            try:
                spec_tree.extend([int(node_id_str)] * max(0, int(pts)))
            except (ValueError, TypeError):
                pass

        skills.append({
            "skill_name": skill_name,
            "slot": slot,
            "points_allocated": int(st.get("level", 0)),
            "spec_tree": spec_tree,
        })

    skills.sort(key=lambda s: s["slot"])

    return {
        "name": f"Imported — {char_class} {mastery}".strip(),
        "description": (
            f"Imported from Last Epoch Tools "
            f"(level {level} {char_class}{' — ' + mastery if mastery else ''})"
        ),
        "character_class": char_class,
        "mastery": mastery,
        "level": level,
        "passive_tree": passive_tree,
        "skills": skills,
        "gear": [],
        "_import_meta": {
            "source": "lastepochtools",
            "char_class_id": char_class_id,
            "mastery_id": mastery_id,
            "skill_count": len(skills),
            "passive_nodes": len(selected_nodes),
            "gear_note": (
                "Gear not imported — Last Epoch Tools item IDs "
                "require a separate database lookup"
            ),
        },
    }


# ---------------------------------------------------------------------------
# Helper: record failure + fire Discord alert
# ---------------------------------------------------------------------------

def _record_and_alert(source: str, url: str, user_id: str | None,
                      error_message: str, severity: str = "hard",
                      missing_fields: list | None = None,
                      partial_data: dict | None = None) -> None:
    """Create an ImportFailure record and fire the Discord alert."""
    try:
        failure = ImportFailure(
            source=source,
            raw_url=url,
            missing_fields=missing_fields or [],
            partial_data=partial_data,
            user_id=user_id,
            error_message=error_message,
        )
        db.session.add(failure)
        db.session.commit()
        send_import_failure_alert(failure, severity=severity)
    except Exception as exc:
        logger.error("import: failed to record import failure: %s", exc)


# ---------------------------------------------------------------------------
# Route: POST /api/import/url
# ---------------------------------------------------------------------------

@import_bp.post("/url")
@limiter.limit("20 per minute")
def import_from_url():
    """
    POST /api/import/url
    Body: { "url": "https://www.lastepochtools.com/planner/kB5dyWvQ" }

    Proxy-fetches the LE Tools page, extracts the embedded build JSON,
    maps it to our format, and returns it for user review before saving.
    Does NOT save the build — that is left to the caller.
    """
    body = request.get_json(silent=True) or {}
    url: str = body.get("url", "").strip()

    if not url:
        return err_response("url is required", 400)

    # Validate URL contains a planner code
    match = re.search(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)", url)
    if not match:
        return err_response(
            "Invalid URL — expected: https://www.lastepochtools.com/planner/[code]", 400
        )

    code = match.group(1)

    # Top-level try/except — never return a bare 500
    try:
        # Fetch the LE Tools planner page server-side (browser blocked by CORS)
        try:
            resp = _requests.get(
                f"https://www.lastepochtools.com/planner/{code}",
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=15,
            )
            resp.raise_for_status()
        except _requests.Timeout:
            return err_response("Timed out fetching the build page — try again.", 504)
        except _requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 502
            if status == 404:
                return err_response("Build not found — the link may be expired or invalid.", 404)
            return err_response(f"Last Epoch Tools returned HTTP {status}.", 502)
        except _requests.RequestException as exc:
            return err_response(f"Network error fetching build: {exc}", 502)

        html = resp.text
        logger.info("import/url: fetched code=%s html_len=%d", code, len(html))

        # Extract the embedded build JSON using structure-aware parsing
        build_info = _extract_build_info(html)

        if build_info is None:
            logger.warning(
                "import/url: could not find buildInfo for code=%s. HTML snippet: %.500s",
                code, html[:500],
            )
            return err_response(
                "Could not find build data in the page. "
                "The build code may be invalid, or Last Epoch Tools may have updated their page format.",
                422,
            )

        # LE Tools sets buildLoadError on invalid/deleted build codes
        if build_info.get("buildLoadError"):
            return err_response("Build not found or deleted on Last Epoch Tools.", 404)

        # LE Tools sometimes wraps the real payload in a "data" key
        if "data" in build_info and isinstance(build_info["data"], dict):
            build_info = build_info["data"]

        # Sanity check — a valid build always has bio or charTree
        if not build_info.get("bio") and not build_info.get("charTree"):
            logger.warning(
                "import/url: extracted JSON missing bio/charTree for code=%s: %s",
                code, list(build_info.keys()),
            )
            return err_response("Build data is incomplete or in an unexpected format.", 422)

        mapped = _map_let_build(build_info)
        logger.info(
            "import/url: mapped code=%s class=%s mastery=%s passives=%d skills=%d",
            code, mapped["character_class"], mapped["mastery"],
            len(mapped["passive_tree"]), len(mapped["skills"]),
        )
        return ok({"build": mapped, "source_code": code})

    except Exception as exc:
        logger.error(
            "import/url: unhandled exception for url=%s: %s\n%s",
            url, exc, traceback.format_exc(),
        )
        user = get_current_user()
        _record_and_alert(
            source="lastepochtools",
            url=url,
            user_id=user.id if user else None,
            error_message=f"Unhandled error in import/url: {exc}",
            partial_data={"traceback": traceback.format_exc()[-500:]},
        )
        return err_response(f"Import failed unexpectedly: {exc}", 422)


# ---------------------------------------------------------------------------
# Full import — parse, validate, save build, track failures
# ---------------------------------------------------------------------------

def _rate_key_import():
    """Rate limit key that distinguishes authenticated vs anonymous users."""
    user = get_current_user()
    if user:
        return f"import:user:{user.id}"
    return f"import:anon:{request.remote_addr}"


def _dynamic_import_limit():
    """Return '5 per minute' for authenticated users, '2 per minute' for anon."""
    user = get_current_user()
    return "5 per minute" if user else "2 per minute"


@import_bp.post("/build")
@limiter.limit(_dynamic_import_limit, key_func=_rate_key_import)
def import_build():
    """
    POST /api/import/build
    Body: { "url": "https://www.lastepochtools.com/planner/B4XdLG56" }
           or { "url": "https://maxroll.gg/last-epoch/planner/zge0t60e" }

    1. Detect source from URL
    2. Run the appropriate importer
    3. On success — save as a draft build, return slug + summary
    4. On hard failure — log ImportFailure, fire Discord alert, return 422
    5. On partial — save build, log ImportFailure, return 200 with warnings

    NEVER returns 500 — all exceptions are caught, recorded, and returned as 422.
    """
    body = request.get_json(silent=True) or {}
    url: str = body.get("url", "").strip()
    user = get_current_user()
    user_id = user.id if user else None

    if not url:
        return err_response("url is required", 400)

    # Detect source
    try:
        source = detect_source(url)
    except ValueError as exc:
        return err_response(str(exc), 400)

    # Top-level try/except — catch ANY unhandled error, record it, alert, return 422
    try:
        return _do_import(url, source, user_id)
    except Exception as exc:
        logger.error(
            "import/build: unhandled exception for url=%s: %s\n%s",
            url, exc, traceback.format_exc(),
        )
        _record_and_alert(
            source=source,
            url=url,
            user_id=user_id,
            error_message=f"Unhandled error: {exc}\n{traceback.format_exc()[-500:]}",
            partial_data={"traceback": traceback.format_exc()[-500:]},
        )
        return err_response(f"Import failed unexpectedly: {exc}", 422)


def _do_import(url: str, source: str, user_id: str | None):
    """Inner import logic — separated so the top-level handler can catch everything."""

    # Run importer
    try:
        importer = get_importer(url)
        result: ImportResult = importer.parse(url)
    except Exception as exc:
        logger.exception("import/build: error during parse for %s", url)
        _record_and_alert(
            source=source,
            url=url,
            user_id=user_id,
            error_message=f"Importer crashed: {exc}",
        )
        return err_response(f"Import failed: {exc}", 422)

    # Hard failure — class/mastery unmappable
    if not result.success:
        _record_and_alert(
            source=result.source or source,
            url=url,
            user_id=user_id,
            error_message=result.error_message or "Unknown parse failure",
            missing_fields=result.missing_fields,
            partial_data=result.build_data,
        )
        return err_response(
            result.error_message or "Import failed — could not parse the build.",
            422,
        )

    # Success (possibly partial)
    build_data = result.build_data
    if not build_data:
        _record_and_alert(
            source=source, url=url, user_id=user_id,
            error_message="Importer returned success=True but build_data is None",
        )
        return err_response("Import returned no data despite reporting success.", 422)

    # Force draft (not public) for imported builds
    build_data["is_public"] = False

    try:
        build = build_service.create_build(build_data, user_id=user_id)
    except Exception as exc:
        logger.exception("import/build: failed to save build from %s", url)
        _record_and_alert(
            source=source, url=url, user_id=user_id,
            error_message=f"Build parsed but save failed: {exc}",
            partial_data={"build_data_keys": list(build_data.keys())},
        )
        return err_response(f"Build parsed but could not be saved: {exc}", 422)

    # Track partial imports
    warnings = result.missing_fields
    if warnings:
        _record_and_alert(
            source=result.source or source,
            url=url,
            user_id=user_id,
            error_message="Partial import — some fields could not be mapped.",
            severity="partial",
            missing_fields=warnings,
            partial_data={"slug": build.slug},
        )

    imported_fields = []
    if build_data.get("character_class"):
        imported_fields.append("class")
    if build_data.get("mastery"):
        imported_fields.append("mastery")
    if build_data.get("passive_tree"):
        imported_fields.append(f"passive_tree ({len(build_data['passive_tree'])} nodes)")
    if build_data.get("skills"):
        imported_fields.append(f"skills ({len(build_data['skills'])})")
    if build_data.get("gear"):
        imported_fields.append(f"gear ({len(build_data['gear'])} items)")

    return ok({
        "slug": build.slug,
        "build_name": build.name,
        "source": result.source,
        "imported_fields": imported_fields,
        "missing_fields": warnings,
        "warnings": [f"Could not map: {f}" for f in warnings] if warnings else [],
    }, status=201)
