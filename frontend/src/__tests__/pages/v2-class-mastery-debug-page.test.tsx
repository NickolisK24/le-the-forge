import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2ClassMasteryDebugPage from "@/pages/debug/V2ClassMasteryDebugPage";

describe("V2ClassMasteryDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({ success: false, error: "v2_class_mastery_bundle_missing", message: "v2 class/mastery bundle not found" });

    render(<V2ClassMasteryDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 class/mastery bundle not found")).toBeInTheDocument();
  });

  it("renders class summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2ClassMasteryDebugPage />);

    expect(await screen.findByText("5")).toBeInTheDocument();
    expect(screen.getByText("15")).toBeInTheDocument();
    expect(screen.getAllByText("Mage").length).toBeGreaterThan(0);
    expect(screen.getByText("class:mage")).toBeInTheDocument();
    expect(screen.getByText("3 masteries")).toBeInTheDocument();
  });

  it("uses controls when loading masteries", async () => {
    mockFetch(successPayload());

    render(<V2ClassMasteryDebugPage />);
    await screen.findByText("class:mage");

    fireEvent.change(screen.getByLabelText(/Kind/i), { target: { value: "masteries" } });
    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "rune" } });
    fireEvent.change(screen.getByLabelText(/Class ID/i), { target: { value: "class:mage" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/masteries?limit=2&q=rune&class_id=class%3Amage");
    });
  });
});

function mockFetch(payload: unknown) {
  vi.mocked(fetch).mockResolvedValue({ json: async () => payload } as Response);
}

function successPayload() {
  return {
    success: true,
    read_only: true,
    production_consumer: false,
    data_source: "v2_class_mastery_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_class_mastery_bundle.json",
    total_classes: 5,
    total_masteries: 15,
    result_count: 1,
    summary: {
      support_status_counts: { partial: 20 },
      trust_level_counts: { generated_from_game_data: 20 },
    },
    records: [
      {
        canonical_id: "class:mage",
        display_name: "Mage",
        source_id: "class:1",
        source_file: "classes.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: { source_path: "classes.json" },
        mastery_ids: ["mastery:mage:sorcerer", "mastery:mage:spellblade", "mastery:mage:runemaster"],
        passive_tree_ids: ["passive_tree:mg-1"],
        skill_ids: [],
        linked_skill_source_ids: [],
        known_restriction_labels: ["Mage"],
        stable_calculable: false,
      },
    ],
  };
}
