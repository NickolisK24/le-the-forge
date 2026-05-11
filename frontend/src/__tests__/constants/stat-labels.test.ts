/**
 * Exhaustiveness test for the stat-label map.
 *
 * `COVERED_STAT_KEYS` enumerates every analysis-response field the
 * presentation layer is allowed to display. If a key ever appears in a
 * component but is missing from the map, `statLabel()` would silently
 * fall back to a title-cased snake_case string — which is the failure
 * mode phase 3 is explicitly closing.
 */

import { describe, it, expect } from "vitest";
import {
  STAT_LABELS,
  COVERED_STAT_KEYS,
  statLabel,
} from "@/constants/statLabels";

describe("STAT_LABELS — exhaustiveness", () => {
  it("has an explicit mapping for every key in COVERED_STAT_KEYS", () => {
    const missing = COVERED_STAT_KEYS.filter((k) => !(k in STAT_LABELS));
    expect(missing).toEqual([]);
  });

  it("every mapped label is non-empty and does not contain raw snake_case", () => {
    for (const key of Object.keys(STAT_LABELS)) {
      const label = STAT_LABELS[key];
      expect(label.length).toBeGreaterThan(0);
      expect(label).not.toMatch(/_/);
    }
  });

  it("includes the prompt's labels — verbatim for the ones that fit, shortened where truncation forced it", () => {
    // The phase-3 prompt pinned the long-form strings for these, but a
    // follow-up adjustment authorised shortening any that ellipsis inside
    // the 320 px analysis rail. "Average Elemental Resistance" (28 chars)
    // was the worst offender; "Critical Strike Chance" / "Critical Strike
    // Multiplier" also did not fit. The shortened forms are documented
    // in docs/unified-planner-phase3-notes.md §2.
    expect(STAT_LABELS.effective_hp).toBe("Effective Health Pool");
    expect(STAT_LABELS.armor_mitigation_pct).toBe("Armor Damage Reduction");
    expect(STAT_LABELS.avg_resistance).toBe("Avg Elemental Res");
    expect(STAT_LABELS.crit_chance).toBe("Crit Chance");
    expect(STAT_LABELS.crit_multiplier).toBe("Crit Multiplier");
    expect(STAT_LABELS.crit_contribution_pct).toBe("Crit Contribution to DPS");
    expect(STAT_LABELS.effective_attack_speed).toBe("Attacks Per Second");
    expect(STAT_LABELS.survivability_score).toBe("Survivability Rating");
    expect(STAT_LABELS.dps_gain_pct).toBe("DPS Improvement");
    expect(STAT_LABELS.ehp_gain_pct).toBe("Survivability Improvement");
    expect(STAT_LABELS.fp_cost).toBe("Forge Potential Cost");
  });
});

describe("statLabel()", () => {
  it("returns the mapped label when the key is known", () => {
    expect(statLabel("total_dps")).toBe("Total DPS");
    expect(statLabel("survivability_score")).toBe("Survivability Rating");
  });

  it("falls back to title-cased input for unknown keys", () => {
    expect(statLabel("my_made_up_stat")).toBe("My Made Up Stat");
  });

  it("does not mutate the input key", () => {
    const key = "effective_hp";
    const label = statLabel(key);
    expect(label).toBe("Effective Health Pool");
    expect(key).toBe("effective_hp");
  });
});
