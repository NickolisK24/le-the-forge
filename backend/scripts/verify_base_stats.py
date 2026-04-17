"""
Verify CLASS_BASE_STATS + ATTRIBUTE_SCALING against the in-game level-1
character sheet (no gear, no passives). Expected output is recorded at
the bottom of this file and the script exits non-zero if any class
deviates from the verified data.

Run from the backend directory:
    python -m scripts.verify_base_stats
"""

from __future__ import annotations

import sys

from app.engines.stat_engine import aggregate_stats


EXPECTED = {
    "Sentinel":  {"health": 116, "mana": 51, "dodge": 0,  "ward_retention": 0,
                  "poison_res": 1, "necrotic_res": 1, "et": 23, "crit_mult": 2.0,
                  "stun_avoid": 255},
    "Rogue":     {"health": 110, "mana": 51, "dodge": 12, "ward_retention": 0,
                  "poison_res": 0, "necrotic_res": 0, "et": 22, "crit_mult": 2.0,
                  "stun_avoid": 255},
    "Mage":      {"health": 110, "mana": 51, "dodge": 0,  "ward_retention": 6,
                  "poison_res": 0, "necrotic_res": 0, "et": 22, "crit_mult": 2.0,
                  "stun_avoid": 255},
    "Primalist": {"health": 110, "mana": 53, "dodge": 0,  "ward_retention": 0,
                  "poison_res": 0, "necrotic_res": 0, "et": 22, "crit_mult": 2.0,
                  "stun_avoid": 255},
    "Acolyte":   {"health": 116, "mana": 51, "dodge": 0,  "ward_retention": 4,
                  "poison_res": 1, "necrotic_res": 1, "et": 23, "crit_mult": 2.0,
                  "stun_avoid": 255},
}


def _observed(character_class: str) -> dict:
    s = aggregate_stats(character_class, "", [], [], [])
    return {
        "health":         int(s.max_health),
        "mana":           int(s.max_mana),
        "dodge":          int(s.dodge_rating),
        "ward_retention": int(s.ward_retention_pct),
        "poison_res":     int(s.poison_res),
        "necrotic_res":   int(s.necrotic_res),
        "et":             int(s.endurance_threshold),
        "crit_mult":      float(s.crit_multiplier),
        "stun_avoid":     int(s.stun_avoidance),
    }


def main() -> int:
    failures: list[str] = []
    for klass, want in EXPECTED.items():
        got = _observed(klass)
        row = (f"{klass:<10}: "
               f"health={got['health']}, mana={got['mana']}, dodge={got['dodge']:<2}, "
               f"ward_retention={got['ward_retention']}%, "
               f"poison_res={got['poison_res']}%, necrotic_res={got['necrotic_res']}%, "
               f"ET={got['et']}, crit_mult={got['crit_mult']}, "
               f"stun_avoid={got['stun_avoid']}")
        print(row)
        if got != want:
            failures.append(f"{klass}: expected {want}, got {got}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nAll 5 classes match verified in-game base stats.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
