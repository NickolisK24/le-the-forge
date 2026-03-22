"""
Craft Engine Tests — validates crafting actions.

Run standalone (no Flask needed):
  python3 backend/tests/test_craft_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.engines.craft_engine import add_affix


def test_add_affix():

    item = {

        "item_type": "helmet",

        "forging_potential": 40,

        "prefixes": [],
        "suffixes": [],

        "sealed_affix": None

    }

    success = add_affix(

        item,
        "Spell Damage",
        1

    )

    assert success