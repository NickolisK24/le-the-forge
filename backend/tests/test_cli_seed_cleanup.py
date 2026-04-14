"""
Tests for the seed-builds, reset-demo-votes, and remove-seeded-builds
Flask CLI commands.

These commands are used to keep the community builds table clean before
launch — fake inflated vote counts and empty-shell demo builds destroy
trust with real users.
"""

import pytest
from click.testing import CliRunner

from app.models import Build
from app.services.build_service import create_build


SEEDED_NAMES = (
    "Bone Curse Lich",
    "Frozen Ruins Runemaster",
    "Manifest Armor Forge Guard",
)


def _invoke(app, cmd_name: str, args=None):
    """Invoke a flask CLI command by name within the app context."""
    runner = CliRunner()
    cmd = app.cli.commands[cmd_name]
    return runner.invoke(cmd, args or [])


# ---------------------------------------------------------------------------
# seed-builds
# ---------------------------------------------------------------------------

def test_seed_builds_uses_zero_vote_count_and_current_patch(app, db):
    """Seeded builds must start at vote_count=0 and patch 1.4.3.

    Inflated vote counts are launch-day anti-patterns; stale patch strings
    trigger "OUTDATED BUILD" warnings in the planner UI.
    """
    result = _invoke(app, "seed-builds")
    assert result.exit_code == 0, result.output

    for name in SEEDED_NAMES:
        b = Build.query.filter_by(name=name).first()
        assert b is not None, f"Seeded build '{name}' not found"
        assert b.vote_count == 0, (
            f"Seeded build '{name}' has vote_count={b.vote_count}, expected 0"
        )
        assert b.patch_version == "1.4.3", (
            f"Seeded build '{name}' has patch={b.patch_version}, expected 1.4.3"
        )


# ---------------------------------------------------------------------------
# reset-demo-votes
# ---------------------------------------------------------------------------

def test_reset_demo_votes_zeroes_builds_above_threshold(app, db):
    """Any build with vote_count > threshold is reset to 0."""
    # Create a fake "inflated" build directly
    b1 = create_build({
        "name": "Inflated Build",
        "character_class": "Mage",
        "mastery": "Sorcerer",
    })
    b1.vote_count = 2500
    b1.recalculate_tier()

    # And a "realistic" build under the threshold
    b2 = create_build({
        "name": "Organic Build",
        "character_class": "Rogue",
        "mastery": "Marksman",
    })
    b2.vote_count = 42
    b2.recalculate_tier()
    db.session.commit()

    result = _invoke(app, "reset-demo-votes")
    assert result.exit_code == 0, result.output

    db.session.refresh(b1)
    db.session.refresh(b2)
    assert b1.vote_count == 0
    assert b2.vote_count == 42  # below threshold — untouched


def test_reset_demo_votes_noop_when_empty(app, db):
    """Command is a no-op when no inflated builds exist."""
    result = _invoke(app, "reset-demo-votes")
    assert result.exit_code == 0, result.output
    assert "Nothing to do" in result.output


# ---------------------------------------------------------------------------
# remove-seeded-builds
# ---------------------------------------------------------------------------

def test_remove_seeded_builds_removes_exactly_the_three_demos(app, db):
    """Removes only the three well-known demo builds, by exact name."""
    # Seed the three demo builds
    seed_result = _invoke(app, "seed-builds")
    assert seed_result.exit_code == 0, seed_result.output

    # Create an unrelated build that must NOT be touched
    safe = create_build({
        "name": "Real User Build",
        "character_class": "Primalist",
        "mastery": "Druid",
    })
    db.session.commit()
    safe_id = safe.id

    remove_result = _invoke(app, "remove-seeded-builds")
    assert remove_result.exit_code == 0, remove_result.output
    assert "Removed 3" in remove_result.output

    for name in SEEDED_NAMES:
        assert Build.query.filter_by(name=name).first() is None, (
            f"Seeded build '{name}' was not removed"
        )
    assert Build.query.filter_by(id=safe_id).first() is not None, (
        "Unrelated build was incorrectly deleted"
    )


def test_remove_seeded_builds_idempotent(app, db):
    """Running twice is safe — second call finds nothing to do."""
    _invoke(app, "seed-builds")
    first = _invoke(app, "remove-seeded-builds")
    assert first.exit_code == 0

    second = _invoke(app, "remove-seeded-builds")
    assert second.exit_code == 0
    assert "Nothing to do" in second.output
