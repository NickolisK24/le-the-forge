/**
 * Unified build-workspace store — phase 1 of the planner/edit consolidation.
 *
 * Single source of truth for the working-copy build that all editor surfaces
 * on the unified page read from and write to. See docs/unified-planner-design.md
 * for the architectural rationale.
 *
 * This store is scoped to the unified page under `/workspace/*`. The legacy
 * `BuildPlannerPage` keeps its own local useState hooks and is not touched.
 */

import { create } from "zustand";
import type {
  Build,
  BuildSkill,
  CharacterClass,
  GearSlot,
} from "@/types";
import type { SelectedBlessing } from "@/types/blessings";

// ---------------------------------------------------------------------------
// Working-copy shape
// ---------------------------------------------------------------------------

/**
 * The editable subset of a Build. Server-only fields (id, slug, vote/view
 * counts, timestamps, author, tier, user_vote) are held separately in
 * `identity` below so the working copy is free of non-mutable concerns.
 */
export interface BuildWorkspaceBuild {
  name: string;
  description: string;
  character_class: CharacterClass;
  mastery: string;
  level: number;
  passive_tree: number[];
  gear: GearSlot[];
  skills: BuildSkill[];
  blessings: SelectedBlessing[];
  is_ssf: boolean;
  is_hc: boolean;
  is_ladder_viable: boolean;
  is_budget: boolean;
  patch_version: string;
  cycle: string;
  is_public: boolean;
}

export interface BuildWorkspaceIdentity {
  id: string | null;
  slug: string | null;
}

export type WorkspaceMetaPatch = Partial<
  Pick<
    BuildWorkspaceBuild,
    | "name"
    | "description"
    | "character_class"
    | "mastery"
    | "level"
    | "is_ssf"
    | "is_hc"
    | "is_ladder_viable"
    | "is_budget"
    | "patch_version"
    | "cycle"
    | "is_public"
  >
>;

// ---------------------------------------------------------------------------
// Default empty build
// ---------------------------------------------------------------------------

/**
 * Returns a fresh empty working-copy build. Always returns a new object so
 * callers cannot share references into the store's default state.
 */
export function emptyBuild(): BuildWorkspaceBuild {
  return {
    name: "",
    description: "",
    character_class: "Acolyte",
    mastery: "",
    level: 100,
    passive_tree: [],
    gear: [],
    skills: [],
    blessings: [],
    is_ssf: false,
    is_hc: false,
    is_ladder_viable: true,
    is_budget: false,
    patch_version: "1.2.1",
    cycle: "1.2",
    is_public: true,
  };
}

// ---------------------------------------------------------------------------
// Store interface
// ---------------------------------------------------------------------------

export type WorkspaceStatus = "empty" | "loading" | "ready";

export interface BuildWorkspaceState {
  build: BuildWorkspaceBuild;
  identity: BuildWorkspaceIdentity;
  status: WorkspaceStatus;

  // Lifecycle
  initializeFromServer: (b: Build) => void;
  initializeEmpty: () => void;
  setLoading: () => void;
  reset: () => void;

  // Editor actions — each produces a new top-level state via set().
  setMeta: (patch: WorkspaceMetaPatch) => void;
  setSkills: (skills: BuildSkill[]) => void;
  setGear: (gear: GearSlot[]) => void;
  setPassiveTree: (nodeIds: number[]) => void;
  setBlessings: (blessings: SelectedBlessing[]) => void;
}

// ---------------------------------------------------------------------------
// Store implementation
// ---------------------------------------------------------------------------

export const useBuildWorkspaceStore = create<BuildWorkspaceState>((set) => ({
  build: emptyBuild(),
  identity: { id: null, slug: null },
  status: "empty",

  initializeFromServer: (b) =>
    set({
      identity: { id: b.id, slug: b.slug },
      build: {
        name: b.name,
        description: b.description ?? "",
        character_class: b.character_class,
        mastery: b.mastery,
        level: b.level,
        passive_tree: [...(b.passive_tree ?? [])],
        gear: [...(b.gear ?? [])],
        skills: [...(b.skills ?? [])],
        blessings: [...(b.blessings ?? [])],
        is_ssf: !!b.is_ssf,
        is_hc: !!b.is_hc,
        is_ladder_viable: !!b.is_ladder_viable,
        is_budget: !!b.is_budget,
        patch_version: b.patch_version,
        cycle: b.cycle,
        is_public: !!b.is_public,
      },
      status: "ready",
    }),

  initializeEmpty: () =>
    set({
      identity: { id: null, slug: null },
      build: emptyBuild(),
      status: "ready",
    }),

  setLoading: () => set({ status: "loading" }),

  reset: () =>
    set({
      identity: { id: null, slug: null },
      build: emptyBuild(),
      status: "empty",
    }),

  setMeta: (patch) =>
    set((s) => ({ build: { ...s.build, ...patch } })),

  setSkills: (skills) =>
    set((s) => ({ build: { ...s.build, skills: [...skills] } })),

  setGear: (gear) =>
    set((s) => ({ build: { ...s.build, gear: [...gear] } })),

  setPassiveTree: (nodeIds) =>
    set((s) => ({ build: { ...s.build, passive_tree: [...nodeIds] } })),

  setBlessings: (blessings) =>
    set((s) => ({ build: { ...s.build, blessings: [...blessings] } })),
}));
