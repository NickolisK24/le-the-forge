/**
 * Unit tests for useBuildWorkspaceStore.
 *
 * Covers the phase-1 requirements:
 *   - initializeEmpty produces a default empty build
 *   - initializeFromServer seeds all editable fields from a Build row
 *   - setSkills / setGear / setPassiveTree / setBlessings produce new arrays
 *     (no in-place mutation of the argument)
 *   - setMeta patches without replacing unrelated fields
 */

import { describe, it, expect, beforeEach } from "vitest";

import {
  useBuildWorkspaceStore,
  emptyBuild,
} from "@/store/buildWorkspace";
import type { Build, BuildSkill, GearSlot } from "@/types";
import type { SelectedBlessing } from "@/types/blessings";
import type { BuildSimulationResult } from "@/lib/api";

// Reset the store between tests — Zustand stores are module singletons.
beforeEach(() => {
  useBuildWorkspaceStore.getState().reset();
});

function makeServerBuild(): Build {
  return {
    id: "build-id-1",
    slug: "my-build",
    name: "My Build",
    description: "desc",
    character_class: "Sentinel",
    mastery: "Paladin",
    level: 90,
    passive_tree: [1, 2, 3],
    gear: [{ slot: "helmet", rarity: "rare" }] as GearSlot[],
    skills: [
      {
        id: "s1",
        slot: 0,
        skill_name: "Smite",
        points_allocated: 5,
        spec_tree: [10, 11],
      },
    ] as BuildSkill[],
    blessings: [
      {
        timeline_id: "t1",
        blessing_id: "b1",
        is_grand: false,
        value: 50,
      },
    ] as SelectedBlessing[],
    is_ssf: true,
    is_hc: false,
    is_ladder_viable: true,
    is_budget: false,
    patch_version: "1.2.1",
    cycle: "1.2",
    vote_count: 7,
    view_count: 42,
    is_public: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
  };
}

describe("useBuildWorkspaceStore", () => {
  describe("emptyBuild()", () => {
    it("returns a new object each call", () => {
      const a = emptyBuild();
      const b = emptyBuild();
      expect(a).not.toBe(b);
      a.gear.push({ slot: "helmet" });
      expect(b.gear).toEqual([]);
    });
  });

  describe("initializeEmpty", () => {
    it("sets status to ready and clears identity", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const s = useBuildWorkspaceStore.getState();
      expect(s.status).toBe("ready");
      expect(s.identity).toEqual({ id: null, slug: null });
      expect(s.build.name).toBe("");
      expect(s.build.skills).toEqual([]);
      expect(s.build.gear).toEqual([]);
      expect(s.build.passive_tree).toEqual([]);
      expect(s.build.blessings).toEqual([]);
    });
  });

  describe("initializeFromServer", () => {
    it("seeds every editable field from the server build", () => {
      useBuildWorkspaceStore
        .getState()
        .initializeFromServer(makeServerBuild());
      const s = useBuildWorkspaceStore.getState();
      expect(s.status).toBe("ready");
      expect(s.identity).toEqual({ id: "build-id-1", slug: "my-build" });
      expect(s.build.name).toBe("My Build");
      expect(s.build.character_class).toBe("Sentinel");
      expect(s.build.mastery).toBe("Paladin");
      expect(s.build.level).toBe(90);
      expect(s.build.passive_tree).toEqual([1, 2, 3]);
      expect(s.build.gear).toHaveLength(1);
      expect(s.build.skills).toHaveLength(1);
      expect(s.build.blessings).toHaveLength(1);
      expect(s.build.is_ssf).toBe(true);
    });

    it("does not alias the server passive_tree array", () => {
      const server = makeServerBuild();
      useBuildWorkspaceStore.getState().initializeFromServer(server);
      const s = useBuildWorkspaceStore.getState();
      expect(s.build.passive_tree).not.toBe(server.passive_tree);
    });
  });

  describe("setMeta", () => {
    it("patches only the provided fields", () => {
      useBuildWorkspaceStore
        .getState()
        .initializeFromServer(makeServerBuild());
      useBuildWorkspaceStore.getState().setMeta({ name: "Renamed" });
      const s = useBuildWorkspaceStore.getState();
      expect(s.build.name).toBe("Renamed");
      expect(s.build.character_class).toBe("Sentinel"); // unchanged
      expect(s.build.mastery).toBe("Paladin"); // unchanged
    });

    it("produces a new build object reference", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const before = useBuildWorkspaceStore.getState().build;
      useBuildWorkspaceStore.getState().setMeta({ level: 55 });
      const after = useBuildWorkspaceStore.getState().build;
      expect(after).not.toBe(before);
      expect(after.level).toBe(55);
    });
  });

  describe("collection setters", () => {
    it("setSkills stores a distinct array from the argument", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const next: BuildSkill[] = [
        {
          id: "a",
          slot: 0,
          skill_name: "X",
          points_allocated: 1,
          spec_tree: [],
        },
      ];
      useBuildWorkspaceStore.getState().setSkills(next);
      const stored = useBuildWorkspaceStore.getState().build.skills;
      expect(stored).toEqual(next);
      expect(stored).not.toBe(next);
    });

    it("setGear stores a distinct array from the argument", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const next: GearSlot[] = [{ slot: "helmet" }];
      useBuildWorkspaceStore.getState().setGear(next);
      const stored = useBuildWorkspaceStore.getState().build.gear;
      expect(stored).toEqual(next);
      expect(stored).not.toBe(next);
    });

    it("setPassiveTree stores a distinct array from the argument", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const next = [7, 8, 9];
      useBuildWorkspaceStore.getState().setPassiveTree(next);
      const stored = useBuildWorkspaceStore.getState().build.passive_tree;
      expect(stored).toEqual(next);
      expect(stored).not.toBe(next);
    });

    it("setBlessings stores a distinct array from the argument", () => {
      useBuildWorkspaceStore.getState().initializeEmpty();
      const next: SelectedBlessing[] = [
        { timeline_id: "t", blessing_id: "b", is_grand: true, value: 1 },
      ];
      useBuildWorkspaceStore.getState().setBlessings(next);
      const stored = useBuildWorkspaceStore.getState().build.blessings;
      expect(stored).toEqual(next);
      expect(stored).not.toBe(next);
    });
  });

  describe("reset", () => {
    it("returns to status 'empty' and default build", () => {
      useBuildWorkspaceStore
        .getState()
        .initializeFromServer(makeServerBuild());
      useBuildWorkspaceStore.getState().reset();
      const s = useBuildWorkspaceStore.getState();
      expect(s.status).toBe("empty");
      expect(s.identity).toEqual({ id: null, slug: null });
      expect(s.build).toEqual(emptyBuild());
    });
  });

  // -------------------------------------------------------------------------
  // Phase 2 — analysis state
  // -------------------------------------------------------------------------
  describe("analysis state", () => {
    function fakeResult(tag = "a"): BuildSimulationResult {
      // Minimal shape — only fields the tests inspect. Casting keeps the
      // fixture small without pulling in the full simulation-result schema.
      return {
        primary_skill: tag,
        skill_level: 20,
        stats: {},
        dps: {} as BuildSimulationResult["dps"],
        monte_carlo: {} as BuildSimulationResult["monte_carlo"],
        defense: {} as BuildSimulationResult["defense"],
        stat_upgrades: [],
        seed: null,
        dps_per_skill: [],
        combined_dps: 0,
      };
    }

    it("starts in the idle state with no result or error", () => {
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("idle");
      expect(s.analysisResult).toBeNull();
      expect(s.analysisError).toBeNull();
      expect(s.analysisRequestId).toBe(0);
    });

    it("requestAnalysis increments the request counter", () => {
      const r1 = useBuildWorkspaceStore.getState().requestAnalysis();
      const r2 = useBuildWorkspaceStore.getState().requestAnalysis();
      const r3 = useBuildWorkspaceStore.getState().requestAnalysis();
      expect(r1).toBe(1);
      expect(r2).toBe(2);
      expect(r3).toBe(3);
      expect(useBuildWorkspaceStore.getState().analysisRequestId).toBe(3);
    });

    it("requestAnalysis moves status to pending and clears any prior error", () => {
      useBuildWorkspaceStore.getState().setAnalysisError(0, "old");
      // The above set used id 0 which matches initial, so we expect error set:
      expect(useBuildWorkspaceStore.getState().analysisError).toBe("old");
      useBuildWorkspaceStore.getState().requestAnalysis();
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("pending");
      expect(s.analysisError).toBeNull();
    });

    it("requestAnalysis does NOT clear the previous result (no-flicker)", () => {
      const id = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().setAnalysisResult(id, fakeResult("a"));
      expect(useBuildWorkspaceStore.getState().analysisResult).not.toBeNull();
      useBuildWorkspaceStore.getState().requestAnalysis();
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("pending");
      expect(s.analysisResult?.primary_skill).toBe("a");
    });

    it("setAnalysisResult with the current requestId stores the result", () => {
      const id = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().setAnalysisResult(id, fakeResult("b"));
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("success");
      expect(s.analysisResult?.primary_skill).toBe("b");
      expect(s.analysisError).toBeNull();
    });

    it("setAnalysisResult with a stale requestId is discarded", () => {
      const staleId = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().requestAnalysis(); // bump past stale
      useBuildWorkspaceStore
        .getState()
        .setAnalysisResult(staleId, fakeResult("stale"));
      const s = useBuildWorkspaceStore.getState();
      // Status must still be "pending" — the fresh request hasn't completed.
      expect(s.analysisStatus).toBe("pending");
      expect(s.analysisResult).toBeNull();
    });

    it("setAnalysisError with the current requestId records the message", () => {
      const id = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().setAnalysisError(id, "boom");
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("error");
      expect(s.analysisError).toBe("boom");
    });

    it("setAnalysisError with a stale requestId is discarded", () => {
      const staleId = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore
        .getState()
        .setAnalysisError(staleId, "stale-boom");
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("pending");
      expect(s.analysisError).toBeNull();
    });

    it("resetAnalysis clears result, error, status, and request counter", () => {
      const id = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().setAnalysisResult(id, fakeResult("x"));
      useBuildWorkspaceStore.getState().resetAnalysis();
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("idle");
      expect(s.analysisResult).toBeNull();
      expect(s.analysisError).toBeNull();
      expect(s.analysisRequestId).toBe(0);
    });

    it("initializeFromServer clears analysis state", () => {
      const id = useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().setAnalysisResult(id, fakeResult("y"));
      useBuildWorkspaceStore
        .getState()
        .initializeFromServer(makeServerBuild());
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("idle");
      expect(s.analysisResult).toBeNull();
      expect(s.analysisRequestId).toBe(0);
    });

    it("initializeEmpty clears analysis state", () => {
      useBuildWorkspaceStore.getState().requestAnalysis();
      useBuildWorkspaceStore.getState().initializeEmpty();
      const s = useBuildWorkspaceStore.getState();
      expect(s.analysisStatus).toBe("idle");
      expect(s.analysisRequestId).toBe(0);
    });
  });
});
