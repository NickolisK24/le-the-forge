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
});
