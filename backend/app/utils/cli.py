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

    @app.cli.command("seed")
    def seed():
        """Seed reference data: item types, affix defs."""
        from app.models import ItemType, AffixDef

        affix_seed_data = [
            {
                "name": affix["name"],
                "type": affix["category"],
                "stat_key": affix["stat_key"],
                "tiers": affix["tiers"],
                "applicable": affix.get("applicable", []),
                "class_requirement": affix.get("class_requirement"),
                "tags": affix.get("tags", []),
            }
            for affix in get_all_affixes()
        ]

        click.echo("Seeding item types...")
        item_types = [
            ("Wand", "weapon", "+X% Spell Damage"),
            ("Staff", "weapon", "+X% Spell Damage"),
            ("Sword", "weapon", "+X% Melee Damage"),
            ("Axe", "weapon", "+X% Melee Damage"),
            ("Dagger", "weapon", "+X% Critical Strike Chance"),
            ("Mace", "weapon", "+X% Melee Damage"),
            ("Sceptre", "weapon", "+X Mana"),
            ("Bow", "weapon", "+X% Bow Damage"),
            ("Shield", "off_hand", "+X Armour"),
            ("Helm", "armour", None),
            ("Chest", "armour", None),
            ("Gloves", "armour", None),
            ("Boots", "armour", None),
            ("Belt", "accessory", None),
            ("Ring", "accessory", None),
            ("Amulet", "accessory", None),
        ]
        for name, category, implicit in item_types:
            if not ItemType.query.filter_by(name=name).first():
                db.session.add(ItemType(name=name, category=category, base_implicit=implicit))

        click.echo("Seeding affix definitions...")
        for a in affix_seed_data:
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
