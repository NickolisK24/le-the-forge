"""
Base Engine Tests — validates FP generation, validation, and item creation.

Run standalone (no Flask needed):
  python3 backend/tests/test_base_engine.py
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_base_data = json.load(open(os.path.join(BASE_DIR, "base_items.json")))

# Build name → item lookup
_name_lookup: dict = {}
for _slot_items in _base_data.values():
    if isinstance(_slot_items, list):
        for _item in _slot_items:
            _name_lookup[_item["name"].lower()] = _item


# ---- Inline versions of base_engine functions for standalone testing ----

def get_fp_range(name_or_slot: str):
    key = name_or_slot.lower()
    # Slot key → first item
    if key in _base_data:
        items = _base_data[key]
        if isinstance(items, list) and items:
            return items[0]["min_fp"], items[0]["max_fp"]
    # Named item
    if key in _name_lookup:
        item = _name_lookup[key]
        return item["min_fp"], item["max_fp"]
    raise ValueError(f"Unknown base type: {name_or_slot}")


def generate_fp(name_or_slot: str) -> int:
    lo, hi = get_fp_range(name_or_slot)
    return random.randint(lo, hi)


def validate_fp(name_or_slot: str, user_fp: int) -> bool:
    if not isinstance(user_fp, int) or isinstance(user_fp, bool):
        return False
    lo, hi = get_fp_range(name_or_slot)
    return lo <= user_fp <= hi


def fixed_fp(value: int) -> int:
    return value


def resolve_fp(name_or_slot: str, fp_mode="random", manual_fp=None):
    if fp_mode == "random":
        return generate_fp(name_or_slot), None
    elif fp_mode == "manual":
        if manual_fp is None:
            return 0, "manual_fp required"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be integer"
        if not validate_fp(name_or_slot, manual_fp):
            lo, hi = get_fp_range(name_or_slot)
            return 0, f"Out of range [{lo}, {hi}]"
        return manual_fp, None
    elif fp_mode == "fixed":
        if manual_fp is None:
            return 0, "manual_fp required for fixed mode"
        return fixed_fp(manual_fp), None
    else:
        return 0, f"Invalid fp_mode: {fp_mode}"


def create_item(name_or_slot: str, fp_mode="random", manual_fp=None):
    key = name_or_slot.lower()
    item = None
    if key in _base_data:
        items = _base_data[key]
        if isinstance(items, list) and items:
            item = items[0]
    elif key in _name_lookup:
        item = _name_lookup[key]

    if item is None:
        return {"success": False, "reason": f"Unknown base type: {name_or_slot}"}

    fp, error = resolve_fp(name_or_slot, fp_mode, manual_fp)
    if error:
        return {"success": False, "reason": error}
    return {"success": True, "item": {
        "base": item["name"], "prefixes": [], "suffixes": [], "sealed": None,
        "forge_potential": fp, "history": [],
        "implicit": item.get("implicit"),
        "armor": item.get("armor", 0),
    }}


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

def test_1_random_fp_generation():
    """Random FP stays within valid range for the base type."""
    print("Test 1 — Random FP Generation")
    # Slot key returns first item's range
    lo, hi = get_fp_range("helmet")
    assert lo >= 1 and lo < hi, f"Invalid range: {lo}-{hi}"
    for _ in range(50):
        fp = generate_fp("helmet")
        assert lo <= fp <= hi, f"Out of range: {fp} not in [{lo}, {hi}]"

    # Named item lookup
    lo2, hi2 = get_fp_range("Imperial Helm")
    assert lo2 >= 1 and lo2 < hi2, f"Invalid named item range: {lo2}-{hi2}"
    for _ in range(20):
        fp = generate_fp("Imperial Helm")
        assert lo2 <= fp <= hi2

    print(f"  Helmet (first) range: {lo}–{hi}, Imperial Helm: {lo2}–{hi2} ✓")


def test_2_manual_fp_valid():
    """Valid manual FP (within range) creates item successfully."""
    print("Test 2 — Manual FP Valid")
    lo, hi = get_fp_range("helmet")
    mid = (lo + hi) // 2
    result = create_item("helmet", fp_mode="manual", manual_fp=mid)
    assert result["success"] is True, f"Expected success: {result}"
    assert result["item"]["forge_potential"] == mid
    print(f"  Helmet FP={mid} accepted ✓  item.fp={result['item']['forge_potential']}")


def test_3_manual_fp_invalid():
    """Invalid manual FP (out of range) returns error, no item created."""
    print("Test 3 — Manual FP Invalid")
    _, hi = get_fp_range("helmet")
    result = create_item("helmet", fp_mode="manual", manual_fp=hi + 100)
    assert result["success"] is False, f"Expected failure, got {result}"
    assert "reason" in result
    print(f"  Helmet FP={hi+100} rejected: {result['reason']} ✓")

    result2 = create_item("helmet", fp_mode="manual", manual_fp=-5)
    assert result2["success"] is False
    print(f"  Helmet FP=-5 rejected: {result2['reason']} ✓")

    result3 = create_item("helmet", fp_mode="manual", manual_fp=23.5)  # type: ignore
    assert result3["success"] is False
    print(f"  Helmet FP=23.5 rejected: {result3['reason']} ✓")


def test_4_edge_values():
    """Edge values (min_fp and max_fp) are both accepted."""
    print("Test 4 — Edge Values")
    lo, hi = get_fp_range("helmet")

    result_min = create_item("helmet", fp_mode="manual", manual_fp=lo)
    assert result_min["success"] is True
    assert result_min["item"]["forge_potential"] == lo
    print(f"  min_fp={lo} accepted ✓")

    result_max = create_item("helmet", fp_mode="manual", manual_fp=hi)
    assert result_max["success"] is True
    assert result_max["item"]["forge_potential"] == hi
    print(f"  max_fp={hi} accepted ✓")

    result_below = create_item("helmet", fp_mode="manual", manual_fp=lo - 1)
    assert result_below["success"] is False
    print(f"  min_fp-1={lo-1} rejected ✓")

    result_above = create_item("helmet", fp_mode="manual", manual_fp=hi + 1)
    assert result_above["success"] is False
    print(f"  max_fp+1={hi+1} rejected ✓")


def test_5_fixed_mode():
    """Fixed mode returns exact value without range validation."""
    print("Test 5 — Fixed Mode (testing/optimizer)")
    result = create_item("helmet", fp_mode="fixed", manual_fp=25)
    assert result["success"] is True
    assert result["item"]["forge_potential"] == 25
    print(f"  Fixed FP=25 returned exactly ✓")


def test_6_unknown_base():
    """Unknown base type returns error."""
    print("Test 6 — Unknown Base Type")
    result = create_item("dragon_scale_armor")
    assert result["success"] is False
    assert "reason" in result
    print(f"  Unknown base rejected: {result['reason']} ✓")


def test_7_all_bases_valid():
    """All base items in base_items.json have valid FP ranges."""
    print("Test 7 — All Bases Valid")
    total = 0
    for slot, items in _base_data.items():
        assert isinstance(items, list), f"{slot} must be a list of items"
        assert len(items) > 0, f"{slot} has no items"
        for item in items:
            lo = item["min_fp"]
            hi = item["max_fp"]
            assert lo >= 1, f"{item['name']}: min_fp < 1"
            assert lo <= hi, f"{item['name']}: min_fp > max_fp"
            fp = random.randint(lo, hi)
            assert lo <= fp <= hi
            total += 1
    print(f"  All {total} named base items across {len(_base_data)} slots valid ✓")


def test_8_named_item_lookup():
    """Named item lookup returns correct data."""
    print("Test 8 — Named Item Lookup")
    lo, hi = get_fp_range("Imperial Helm")
    assert lo >= 1 and lo < hi

    lo2, hi2 = get_fp_range("Rusted Coif")
    assert lo2 < lo, "Rusted Coif should have lower FP than Imperial Helm"

    # Named sword
    lo3, hi3 = get_fp_range("Arming Sword")
    assert lo3 >= 1

    print(f"  Rusted Coif: {lo2}-{hi2}, Imperial Helm: {lo}-{hi}, Arming Sword: {lo3}-{hi3} ✓")


if __name__ == "__main__":
    tests = [
        test_1_random_fp_generation,
        test_2_manual_fp_valid,
        test_3_manual_fp_invalid,
        test_4_edge_values,
        test_5_fixed_mode,
        test_6_unknown_base,
        test_7_all_bases_valid,
        test_8_named_item_lookup,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
        except Exception as e:
            print(f"  ERROR: {e}")
        print()
    print(f"{'='*40}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    if passed < len(tests):
        sys.exit(1)
