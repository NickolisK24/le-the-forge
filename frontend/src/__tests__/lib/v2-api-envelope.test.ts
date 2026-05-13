import { describe, expect, it } from "vitest";

import {
  getV2ErrorMessage,
  getV2Records,
  getV2SourcePath,
  getV2Summary,
  summarizeV2Support,
} from "@/lib/v2ApiEnvelope";

describe("v2ApiEnvelope", () => {
  it("reads records from the standardized data envelope", () => {
    const records = getV2Records({
      data: {
        records: [{ canonical_id: "affix:equipment:1" }],
      },
    });

    expect(records).toEqual([{ canonical_id: "affix:equipment:1" }]);
  });

  it("preserves compatibility with top-level records", () => {
    const records = getV2Records({
      records: [{ canonical_id: "item_base:equippable:0:1" }],
    });

    expect(records).toEqual([{ canonical_id: "item_base:equippable:0:1" }]);
  });

  it("reads summary and support from new or legacy shapes", () => {
    expect(summarizeV2Support({ support_summary: { partial: 2, stable_calculable: 0 } })).toBe("partial: 2, stable_calculable: 0");
    expect(getV2Summary({ debug_summary: { summary: { trust_level_counts: { generated_from_game_data: 2 } } } })).toEqual({
      trust_level_counts: { generated_from_game_data: 2 },
    });
  });

  it("reads provenance source path from the envelope", () => {
    expect(getV2SourcePath({ provenance: { source_path: "docs/generated/v2_affix_bundle.json" } })).toBe("docs/generated/v2_affix_bundle.json");
  });

  it("reads standardized error messages", () => {
    expect(getV2ErrorMessage({ error: { code: "missing", message: "Bundle missing" } })).toBe("Bundle missing");
    expect(getV2ErrorMessage({ error: "legacy_missing", message: "Legacy missing" })).toBe("Legacy missing");
  });
});
