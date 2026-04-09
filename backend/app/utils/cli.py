"""
Flask CLI commands registered via register_commands().

Usage (inside container or venv):
    flask seed            — Populate reference tables from static data
    flask seed-builds     — Add sample builds for dev/demo
    flask create-admin    — Create a local admin user (dev only)
"""

import click
from flask import Flask

from app import db
from app.game_data.game_data_loader import get_all_affixes


def register_commands(app: Flask) -> None:

    def _build_affix_seed_data():
        result = []
        for affix in get_all_affixes():
            cr = affix.get("class_requirement")
            # DB column is a single VARCHAR; if the JSON gives a list, join it
            if isinstance(cr, list):
                cr = ",".join(cr) if cr else None
            # Convert tiers list to dict for DB storage
            tiers_dict = {str(t["tier"]): [t["min"], t["max"]] for t in affix["tiers"]}
            result.append({
                "name": affix["name"],
                "type": affix.get("type", affix.get("category", "prefix")),
                "stat_key": affix.get("stat_key", ""),
                "tiers": tiers_dict,
                "applicable": affix.get("applicable_to", []),
                "class_requirement": cr,
                "tags": affix.get("tags", []),
            })
        return result

    _ITEM_TYPES = [
        # Weapons
        ("Wand", "weapon", "+X% Spell Damage"),
        ("Staff", "weapon", "+X% Spell Damage"),
        ("Sword", "weapon", "+X% Melee Damage"),
        ("Axe", "weapon", "+X% Melee Damage"),
        ("Dagger", "weapon", "+X% Critical Strike Chance"),
        ("Mace", "weapon", "+X% Melee Damage"),
        ("Sceptre", "weapon", "+X Mana"),
        ("Bow", "weapon", "+X% Bow Damage"),
        ("Polearm", "weapon", "+X% Melee Damage"),
        ("Spear", "weapon", "+X% Melee Damage"),
        # Off-hand
        ("Shield", "off_hand", "+X Armour"),
        ("Quiver", "off_hand", None),
        ("Catalyst", "off_hand", None),
        # Armour
        ("Helm", "armour", None),
        ("Chest", "armour", None),
        ("Gloves", "armour", None),
        ("Boots", "armour", None),
        # Accessories
        ("Belt", "accessory", None),
        ("Ring", "accessory", None),
        ("Amulet", "accessory", None),
        ("Relic", "accessory", None),
        # Idols
        ("Idol_1X1", "idol", None),
        ("Idol_1X2", "idol", None),
        ("Idol_1X3", "idol", None),
        ("Idol_1X4", "idol", None),
        ("Idol_2X2", "idol", None),
    ]

    @app.cli.command("seed")
    def seed():
        """Seed reference data: item types, affix defs (skips existing rows)."""
        from app.models import ItemType, AffixDef

        click.echo("Seeding item types...")
        for name, category, implicit in _ITEM_TYPES:
            if not ItemType.query.filter_by(name=name).first():
                db.session.add(ItemType(name=name, category=category, base_implicit=implicit))

        click.echo("Seeding affix definitions...")
        for a in _build_affix_seed_data():
            if not AffixDef.query.filter_by(name=a["name"]).first():
                db.session.add(AffixDef(
                    name=a["name"],
                    affix_type=a["type"],
                    stat_key=a["stat_key"],
                    tier_ranges=a["tiers"],
                    applicable_types=a["applicable"],
                    class_requirement=a["class_requirement"],
                    tags=a["tags"],
                ))

        db.session.commit()
        click.echo("✓ Reference data seeded.")

    @app.cli.command("reseed-affixes")
    def reseed_affixes():
        """Wipe and re-seed AffixDef table from data/affixes.json."""
        from app.models import AffixDef

        click.echo("Clearing existing affix definitions...")
        AffixDef.query.delete()
        db.session.commit()

        click.echo("Seeding affix definitions...")
        count = 0
        for a in _build_affix_seed_data():
            db.session.add(AffixDef(
                name=a["name"],
                affix_type=a["type"],
                stat_key=a["stat_key"],
                tier_ranges=a["tiers"],
                applicable_types=a["applicable"],
                class_requirement=a["class_requirement"],
                tags=a["tags"],
            ))
            count += 1

        db.session.commit()
        click.echo(f"✓ {count} affix definitions seeded.")

    @app.cli.command("seed-builds")
    def seed_builds():
        """Add sample builds for local dev / demo."""
        from app.models import Build
        from app.services.build_service import create_build

        sample_builds = [
            {
                "name": "Bone Curse Lich",
                "description": "The cycle's dominant Lich build. Ward scaling + Bone Curse.",
                "character_class": "Acolyte",
                "mastery": "Lich",
                "is_ssf": True,
                "is_ladder_viable": True,
                "is_budget": False,
                "patch_version": "1.2.1",
                "cycle": "1.2",
            },
            {
                "name": "Frozen Ruins Runemaster",
                "description": "Rune of Winter + Glacier. Strongest boss killer.",
                "character_class": "Mage",
                "mastery": "Runemaster",
                "is_ssf": False,
                "is_ladder_viable": True,
                "is_budget": True,
                "patch_version": "1.2.1",
                "cycle": "1.2",
            },
            {
                "name": "Manifest Armor Forge Guard",
                "description": "HC meta pick. Armour stacking + Manifest Armor.",
                "character_class": "Sentinel",
                "mastery": "Forge Guard",
                "is_ssf": True,
                "is_hc": True,
                "patch_version": "1.2.1",
                "cycle": "1.2",
            },
        ]

        for data in sample_builds:
            if not Build.query.filter_by(name=data["name"]).first():
                b = create_build(data)
                # Give them some votes for realism
                b.vote_count = {"Bone Curse Lich": 2841, "Frozen Ruins Runemaster": 2204,
                                "Manifest Armor Forge Guard": 1987}.get(b.name, 100)
                b.recalculate_tier()

        db.session.commit()
        click.echo(f"✓ {len(sample_builds)} sample builds seeded.")

    @app.cli.command("seed-passives")
    def seed_passives():
        """Upsert passive nodes from data/passives.json into passive_nodes table."""
        import json
        from pathlib import Path
        from app.models import PassiveNode

        data_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "classes" / "passives.json"
        if not data_path.exists():
            click.echo(f"ERROR: {data_path} not found. Run sync_game_data.py first.", err=True)
            return

        with open(data_path, encoding="utf-8") as f:
            nodes = json.load(f)

        # Build a set of all node IDs in the file for connection validation
        all_ids: set[str] = {n["id"] for n in nodes}

        inserted = updated = warnings = 0

        for node in nodes:
            # Warn about any connection IDs that reference a non-existent node
            for conn_id in node.get("connections", []):
                if conn_id not in all_ids:
                    click.echo(f"  [WARN] Node {node['id']}: connection '{conn_id}' not found in passives.json")
                    warnings += 1

            existing = PassiveNode.query.get(node["id"])
            if existing:
                existing.raw_node_id = node["raw_node_id"]
                existing.character_class = node["character_class"]
                existing.mastery = node.get("mastery")
                existing.mastery_index = node.get("mastery_index", 0)
                existing.mastery_requirement = node.get("mastery_requirement", 0)
                existing.name = node["name"]
                existing.description = node.get("description")
                existing.node_type = node.get("node_type", "core")
                existing.x = node.get("x", 0.0)
                existing.y = node.get("y", 0.0)
                existing.max_points = node.get("max_points", 1)
                existing.connections = node.get("connections", [])
                existing.stats = node.get("stats")
                existing.ability_granted = node.get("ability_granted")
                existing.icon = node.get("icon")
                updated += 1
            else:
                db.session.add(PassiveNode(
                    id=node["id"],
                    raw_node_id=node["raw_node_id"],
                    character_class=node["character_class"],
                    mastery=node.get("mastery"),
                    mastery_index=node.get("mastery_index", 0),
                    mastery_requirement=node.get("mastery_requirement", 0),
                    name=node["name"],
                    description=node.get("description"),
                    node_type=node.get("node_type", "core"),
                    x=node.get("x", 0.0),
                    y=node.get("y", 0.0),
                    max_points=node.get("max_points", 1),
                    connections=node.get("connections", []),
                    stats=node.get("stats"),
                    ability_granted=node.get("ability_granted"),
                    icon=node.get("icon"),
                ))
                inserted += 1

        db.session.commit()
        click.echo(f"✓ Passive nodes seeded: {inserted} inserted, {updated} updated.")
        if warnings:
            click.echo(f"  {warnings} dangling connection ID(s) logged above.")

    @app.cli.command("create-admin")
    @click.argument("username")
    def create_admin(username: str):
        """Create a dev admin user (no real Discord auth needed locally)."""
        from app.models import User
        import uuid

        user = User(
            discord_id=f"dev-{uuid.uuid4().hex[:8]}",
            username=username,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"✓ Admin user '{username}' created. ID: {user.id}")

    @app.cli.command("refresh-meta")
    def refresh_meta():
        """Force-refresh all meta analytics caches regardless of TTL."""
        from app.services import meta_analytics_service
        try:
            snapshot = meta_analytics_service.refresh_all()
            classes = len(snapshot.get("class_distribution", []))
            skills = len(snapshot.get("popular_skills", []))
            click.echo(f"✓ Meta analytics refreshed — {classes} classes, {skills} popular skills.")
        except Exception as e:
            click.echo(f"✗ Failed to refresh meta analytics: {e}", err=True)

    @app.cli.command("validate-data")
    def validate_data():
        """Validate all data files in /data/. Exits with code 1 if any are malformed."""
        import json
        import sys
        from pathlib import Path

        data_root = Path(__file__).resolve().parent.parent.parent.parent / "data"
        if not data_root.exists():
            click.echo(f"ERROR: Data directory not found: {data_root}", err=True)
            sys.exit(1)

        errors: list[str] = []
        checked = 0

        # Required data files — the pipeline depends on these
        required_files = {
            "items/affixes.json": {"type": list, "min_entries": 1},
            "entities/enemy_profiles.json": {"type": list, "min_entries": 1},
            "classes/passives.json": {"type": list, "min_entries": 1},
            "classes/skills_metadata.json": {"type": dict},
            "items/uniques.json": {"type": dict},
            "items/rarities.json": {"type": list},
            "combat/damage_types.json": {"type": list},
            "items/implicit_stats.json": {"type": dict},
            "items/base_items.json": {"type": (list, dict)},
            "items/crafting_rules.json": {"type": dict},
        }

        # Check required files exist and have valid JSON + correct top-level type
        for rel_path, spec in required_files.items():
            fpath = data_root / rel_path
            if not fpath.exists():
                errors.append(f"MISSING: {rel_path}")
                continue
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as exc:
                errors.append(f"MALFORMED JSON: {rel_path}: {exc}")
                continue

            expected_type = spec["type"]
            if isinstance(expected_type, tuple):
                if not isinstance(data, expected_type):
                    errors.append(f"WRONG TYPE: {rel_path}: expected {expected_type}, got {type(data).__name__}")
            elif not isinstance(data, expected_type):
                errors.append(f"WRONG TYPE: {rel_path}: expected {expected_type.__name__}, got {type(data).__name__}")

            min_entries = spec.get("min_entries", 0)
            if min_entries and isinstance(data, (list, dict)) and len(data) < min_entries:
                errors.append(f"TOO FEW ENTRIES: {rel_path}: expected >= {min_entries}, got {len(data)}")

            checked += 1

        # Also validate all JSON files in data/ are parseable
        for json_file in sorted(data_root.rglob("*.json")):
            rel = json_file.relative_to(data_root)
            if str(rel) in required_files:
                continue  # already checked
            try:
                with open(json_file, encoding="utf-8") as f:
                    json.load(f)
                checked += 1
            except json.JSONDecodeError as exc:
                errors.append(f"MALFORMED JSON: {rel}: {exc}")

        if errors:
            click.echo(f"✗ Data validation FAILED — {len(errors)} error(s):", err=True)
            for err in errors:
                click.echo(f"  - {err}", err=True)
            sys.exit(1)
        else:
            click.echo(f"✓ Data validation passed — {checked} files checked.")
