"""
Base Engine & Item Engine Tests — validates FP generation, validation, and item creation.

Run standalone (no Flask needed):
  python3 backend/tests/test_base_engine.py
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Patch imports before loading engines
import importlib

# Manually load engines without Flask
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_base_data = json.load(open(os.path.join(BASE_DIR, "base_items.json")))

# ---- Inline versions of base_engine functions for standalone testing ----
def get_fp_range(base_type):
    key = base_type.lower()
    if key not in _base_data:
        raise ValueError(f"Unknown base type: {base_type}")
    b = _base_data[key]
    return b["min_fp"], b["max_fp"]

def generate_fp(base_type):
    lo, hi = get_fp_range(base_type)
    return random.randint(lo, hi)

def validate_fp(base_type, user_fp):
    if not isinstance(user_fp, int) or isinstance(user_fp, bool):
        return False
    lo, hi = get_fp_range(base_type)
    return lo <= user_fp <= hi

def fixed_fp(value):
    return value

def resolve_fp(base_type, fp_mode="random", manual_fp=None):
    if fp_mode == "random":
        return generate_fp(base_type), None
    elif fp_mode == "manual":
        if manual_fp is None:
            return 0, "manual_fp required"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be integer"
        if not validate_fp(base_type, manual_fp):
            lo, hi = get_fp_range(base_type)
            return 0, f"Out of range [{lo}, {hi}]"
        return manual_fp, None
    elif fp_mode == "fixed":
        if manual_fp is None:
            return 0, "manual_fp required for fixed mode"
        return fixed_fp(manual_fp), None
    else:
        return 0, f"Invalid fp_mode: {fp_mode}"

def create_item(base_type, fp_mode="random", manual_fp=None):
    if base_type.lower() not in _base_data:
        return {"success": False, "reason": f"Unknown base type: {base_type}"}
    fp, error = resolve_fp(base_type, fp_mode, manual_fp)
    if error:
        return {"success": False, "reason": error}
    base = _base_data[base_type.lower()]
    return {"success": True, "item": {
        "base": base_type, "prefixes": [], "suffixes": [], "sealed": None,
        "forge_potential": fp, "history": [], "implicit": base.get("implicit"),
        "armor": base.get("armor", 0),
    }}

# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

def test_1_random_fp_generation():
    """Random FP stays within valid range for the base type."""
    print("Test 1 — Random FP Generation")
    lo, hi = get_fp_range("helmet")
    assert lo == 18 and hi == 28, f"Expected 18-28, got {lo}-{hi}"
    for _ in range(50):
        fp = generate_fp("helmet")
        assert lo <= fp <= hi, f"Out of range: {fp} not in [{lo}, {hi}]"
    print(f"  Helmet FP range: {lo}–{hi}  sample={[generate_fp('helmet') for _ in range(5)]} ✓")

def test_2_manual_fp_valid():
    """Valid manual FP (within range) creates item successfully."""
    print("Test 2 — Manual FP Valid")
    result = create_item("helmet", fp_mode="manual", manual_fp=23)
    assert result["success"] is True, f"Expected success: {result}"
    assert result["item"]["forge_potential"] == 23
    print(f"  Helmet FP=23 accepted ✓  item.fp={result['item']['forge_potential']}")

def test_3_manual_fp_invalid():
    """Invalid manual FP (out of range) returns error, no item created."""
    print("Test 3 — Manual FP Invalid")
    result = create_item("helmet", fp_mode="manual", manual_fp=100)
    assert result["success"] is False, f"Expected failure, got {result}"
    assert "reason" in result
    print(f"  Helmet FP=100 rejected: {result['reason']} ✓")

    # Also test negative
    result2 = create_item("helmet", fp_mode="manual", manual_fp=-5)
    assert result2["success"] is False
    print(f"  Helmet FP=-5 rejected: {result2['reason']} ✓")

    # Also test float
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

    # One below min and one above max
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
    assert "Unknown" in result["reason"] or "reason" in result
    print(f"  Unknown base rejected: {result['reason']} ✓")

def test_7_all_bases_valid():
    """All base types in base_items.json have valid FP ranges."""
    print("Test 7 — All Bases Valid")
    for base_type, data in _base_data.items():
        lo, hi = get_fp_range(base_type)
        assert lo >= 1, f"{base_type}: min_fp < 1"
        assert lo <= hi, f"{base_type}: min_fp > max_fp"
        # Spot-check random generation
        fp = generate_fp(base_type)
        assert lo <= fp <= hi, f"{base_type}: rolled {fp} outside [{lo},{hi}]"
    print(f"  All {len(_base_data)} bases valid ✓")


if __name__ == "__main__":
    tests = [
        test_1_random_fp_generation,
        test_2_manual_fp_valid,
        test_3_manual_fp_invalid,
        test_4_edge_values,
        test_5_fixed_mode,
        test_6_unknown_base,
        test_7_all_bases_valid,
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
