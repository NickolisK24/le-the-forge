import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2SkillsDebugPage from "@/pages/debug/V2SkillsDebugPage";

describe("V2SkillsDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({ success: false, error: "v2_skill_bundle_missing", message: "v2 skill bundle not found" });

    render(<V2SkillsDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 skill bundle not found")).toBeInTheDocument();
  });

  it("renders skill summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2SkillsDebugPage />);

    expect(await screen.findByText("184")).toBeInTheDocument();
    expect(screen.getByText("136")).toBeInTheDocument();
    expect(screen.getByText("3919")).toBeInTheDocument();
    expect(screen.getByText("Fireball")).toBeInTheDocument();
    expect(screen.getByText("skill:fi9")).toBeInTheDocument();
    expect(screen.getByText("skill_tree:fi9")).toBeInTheDocument();
  });

  it("uses controls when loading", async () => {
    mockFetch(successPayload());

    render(<V2SkillsDebugPage />);
    await screen.findByText("skill:fi9");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "fire" } });
    fireEvent.change(screen.getByLabelText(/Class ID/i), { target: { value: "class:mage" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/skills?limit=2&q=fire&class_id=class%3Amage");
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
    data_source: "v2_skill_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_skill_bundle.json",
    total_skills: 184,
    total_skill_trees: 136,
    total_skill_nodes: 3919,
    result_count: 1,
    summary: {
      support_status_counts: { partial: 184 },
      skill_special_behavior_classification_counts: { partial_modifier: 57, scripted_runtime_behavior: 83 },
    },
    records: [
      {
        canonical_id: "skill:fi9",
        display_name: "Fireball",
        source_id: "fi9",
        source_file: "skills_with_trees.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: { source_path: "skills_with_trees.json" },
        owner_class_ids: [],
        owner_mastery_ids: [],
        source_skill_id: "fi9",
        skill_tree_id: "skill_tree:fi9",
        skill_tags: ["Fire", "Spell"],
        damage_types: ["Fire", "Spell"],
        scaling_tags: ["Intelligence"],
        text_effects: ["Cast a fireball."],
        special_behavior_classification: "partial_modifier",
        stable_calculable: false,
      },
    ],
  };
}
