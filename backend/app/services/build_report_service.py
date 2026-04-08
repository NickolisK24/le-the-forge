"""
Build Report Service — generates a complete read-only build summary for sharing.

Includes identity, stats, DPS, EHP, upgrade recommendations, skills, gear,
and OpenGraph meta fields for Discord unfurling.
"""

from datetime import datetime, timezone

from flask import current_app

from app.models import Build
from app.services.build_analysis_service import analyze_build


def generate_report(build: Build) -> dict:
    """
    Generate a full build report.

    Returns a dict with all report sections and OpenGraph meta fields.
    Raises if the build can't be analyzed (no skills, etc.).
    """
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")

    # Run the analysis pipeline
    analysis = analyze_build(build)

    # Build identity
    identity = {
        "name": build.name,
        "character_class": build.character_class,
        "mastery": build.mastery,
        "level": build.level,
        "patch_version": build.patch_version,
        "author": build.author.username if build.author else None,
        "slug": build.slug,
    }

    # DPS summary
    dps = analysis.get("dps", {})
    dps_summary = {
        "total_dps": dps.get("total_dps", 0),
        "raw_dps": dps.get("dps", 0),
        "crit_contribution_pct": dps.get("crit_contribution_pct", 0),
        "ailment_dps": dps.get("ailment_dps", 0),
        "hit_damage": dps.get("hit_damage", 0),
        "average_hit": dps.get("average_hit", 0),
    }

    # EHP summary
    defense = analysis.get("defense", {})
    ehp_summary = {
        "effective_hp": defense.get("effective_hp", 0),
        "max_health": defense.get("max_health", 0),
        "armor_reduction_pct": defense.get("armor_reduction_pct", 0),
        "avg_resistance": defense.get("avg_resistance", 0),
        "survivability_score": defense.get("survivability_score", 0),
        "dodge_chance_pct": defense.get("dodge_chance_pct", 0),
        "block_chance_pct": defense.get("block_chance_pct", 0),
    }

    # Top 3 upgrades
    upgrades = analysis.get("stat_upgrades", [])[:3]

    # Skills
    skills_summary = [
        {
            "skill_name": s.skill_name,
            "slot": s.slot,
            "points_allocated": s.points_allocated,
            "node_count": len(s.spec_tree or []),
        }
        for s in sorted(build.skills, key=lambda s: s.slot)
    ]

    # Gear
    gear_summary = []
    for slot in (build.gear or []):
        gear_summary.append({
            "slot": slot.get("slot", "unknown"),
            "item_name": slot.get("item_name"),
            "rarity": slot.get("rarity"),
            "affix_count": len(slot.get("affixes") or []),
        })

    # OpenGraph meta
    total_dps = dps.get("total_dps", 0)
    effective_hp = defense.get("effective_hp", 0)
    surv_score = defense.get("survivability_score", 0)

    og_title = f"{build.name} — {build.character_class} {build.mastery} Build"
    og_description = f"DPS: {round(total_dps):,} | EHP: {round(effective_hp):,} | Survivability: {round(surv_score)}/100"
    og_url = f"{frontend_url}/report/{build.slug}"

    generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "identity": identity,
        "stat_summary": analysis.get("stats", {}),
        "dps_summary": dps_summary,
        "ehp_summary": ehp_summary,
        "top_upgrades": upgrades,
        "skills": skills_summary,
        "gear": gear_summary,
        "generated_at": generated_at,
        "og_title": og_title,
        "og_description": og_description,
        "og_url": og_url,
    }
