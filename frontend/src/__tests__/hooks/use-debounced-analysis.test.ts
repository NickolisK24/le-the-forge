/**
 * Tests for useDebouncedAnalysis (phase 2).
 *
 * Covers:
 *  - Field changes trigger a debounced request (400 ms default).
 *  - Multiple rapid edits collapse into one request.
 *  - Successful response populates analysisResult.
 *  - Error response populates analysisError.
 *  - Unmount during a pending debounce cancels the scheduled call.
 *  - A slow response whose requestId is stale does not update state.
 *  - An edit after a completed analysis triggers a new request.
 *  - Non-simulatable builds (missing class/mastery/skill) do not fire.
 *  - runAnalysisNow() bypasses the debounce.
 *  - buildAnalysisPayload / buildIsSimulatable unit behaviour.
 */

import {
  describe,
  it,
  expect,
  beforeEach,
  afterEach,
  vi,
} from "vitest";
import { renderHook, act } from "@testing-library/react";

import {
  useDebouncedAnalysis,
  buildAnalysisPayload,
  buildIsSimulatable,
  runAnalysisNow,
} from "@/hooks/useDebouncedAnalysis";
import { useBuildWorkspaceStore } from "@/store";
import type { BuildWorkspaceBuild } from "@/store/buildWorkspace";
import type { BuildSkill, GearSlot } from "@/types";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock("@/lib/api", async () => {
  const actual =
    await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    simulateApi: {
      ...actual.simulateApi,
      buildInline: vi.fn(),
    },
  };
});

import { simulateApi } from "@/lib/api";

const buildInline = simulateApi.buildInline as unknown as ReturnType<
  typeof vi.fn
>;

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeSimulatableBuild(): BuildWorkspaceBuild {
  return {
    name: "Test",
    description: "",
    character_class: "Mage",
    mastery: "Sorcerer",
    level: 100,
    passive_tree: [1, 2, 3],
    gear: [
      {
        slot: "helmet",
        affixes: [{ name: "Spell Damage", tier: 4, sealed: false }],
      } as GearSlot,
    ],
    skills: [
      {
        id: "s1",
        slot: 0,
        skill_name: "Fireball",
        points_allocated: 20,
        spec_tree: [],
      } as BuildSkill,
    ],
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

function fakeApiResponse(tag = "Fireball") {
  return {
    data: {
      primary_skill: tag,
      skill_level: 20,
      stats: {},
      dps: {},
      monte_carlo: {},
      defense: {},
      stat_upgrades: [],
      seed: null,
      dps_per_skill: [],
      combined_dps: 0,
    },
    meta: null,
    errors: null,
  };
}

function fakeApiError(message: string) {
  return {
    data: null,
    meta: null,
    errors: [{ message }],
  };
}

// Move the store into a simulatable "ready" state before each test.
function seedStore(build: BuildWorkspaceBuild = makeSimulatableBuild()) {
  const s = useBuildWorkspaceStore.getState();
  s.initializeEmpty();
  s.setMeta({
    character_class: build.character_class,
    mastery: build.mastery,
    level: build.level,
  });
  s.setSkills(build.skills);
  s.setPassiveTree(build.passive_tree);
  s.setGear(build.gear);
  s.setBlessings(build.blessings);
}

/**
 * Consume the hook's initial-load 0 ms fire so the rest of the test can
 * reason about edits in isolation. Tests that specifically exercise the
 * initial-load behaviour should NOT call this helper.
 */
async function flushInitialFire() {
  await act(async () => {
    vi.advanceTimersByTime(0);
    await Promise.resolve();
    await Promise.resolve();
  });
  buildInline.mockClear();
}

// ---------------------------------------------------------------------------
// Pure helper tests
// ---------------------------------------------------------------------------

describe("buildIsSimulatable", () => {
  it("returns false when class is missing", () => {
    const b = makeSimulatableBuild();
    b.character_class = "" as any;
    expect(buildIsSimulatable(b)).toBe(false);
  });

  it("returns false when mastery is missing", () => {
    const b = makeSimulatableBuild();
    b.mastery = "";
    expect(buildIsSimulatable(b)).toBe(false);
  });

  it("returns false when no skill is specialised", () => {
    const b = makeSimulatableBuild();
    b.skills = [];
    expect(buildIsSimulatable(b)).toBe(false);
  });

  it("returns false when all skills have empty names", () => {
    const b = makeSimulatableBuild();
    b.skills = [
      {
        id: "s",
        slot: 0,
        skill_name: "",
        points_allocated: 0,
        spec_tree: [],
      },
    ];
    expect(buildIsSimulatable(b)).toBe(false);
  });

  it("returns true when class, mastery, and one named skill are present", () => {
    expect(buildIsSimulatable(makeSimulatableBuild())).toBe(true);
  });
});

describe("buildAnalysisPayload", () => {
  it("uses the lowest-slot skill with a non-empty name as primary", () => {
    const b = makeSimulatableBuild();
    b.skills = [
      {
        id: "s2",
        slot: 2,
        skill_name: "Meteor",
        points_allocated: 15,
        spec_tree: [],
      },
      {
        id: "s0",
        slot: 0,
        skill_name: "Fireball",
        points_allocated: 20,
        spec_tree: [],
      },
    ];
    const p = buildAnalysisPayload(b);
    expect(p.skill_name).toBe("Fireball");
    expect(p.skill_level).toBe(20);
  });

  it("clamps skill_level to at least 1", () => {
    const b = makeSimulatableBuild();
    b.skills[0].points_allocated = 0;
    const p = buildAnalysisPayload(b);
    expect(p.skill_level).toBeGreaterThanOrEqual(1);
  });

  it("flattens affixes from every gear slot", () => {
    const b = makeSimulatableBuild();
    b.gear = [
      {
        slot: "helmet",
        affixes: [
          { name: "Health", tier: 3, sealed: false },
          { name: "Resist", tier: 2, sealed: false },
        ],
      } as GearSlot,
      {
        slot: "chest",
        affixes: [{ name: "Armour", tier: 5, sealed: false }],
      } as GearSlot,
    ];
    const p = buildAnalysisPayload(b);
    expect(p.gear_affixes).toEqual([
      { name: "Health", tier: 3 },
      { name: "Resist", tier: 2 },
      { name: "Armour", tier: 5 },
    ]);
  });

  it("copies passive_tree into allocated_node_ids (new array)", () => {
    const b = makeSimulatableBuild();
    const p = buildAnalysisPayload(b);
    expect(p.allocated_node_ids).toEqual(b.passive_tree);
    expect(p.allocated_node_ids).not.toBe(b.passive_tree);
  });
});

// ---------------------------------------------------------------------------
// Hook tests
// ---------------------------------------------------------------------------

describe("useDebouncedAnalysis", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    buildInline.mockReset();
    useBuildWorkspaceStore.getState().reset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("does not fire before the 400 ms debounce elapses", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    await act(async () => {
      vi.advanceTimersByTime(399);
    });
    expect(buildInline).not.toHaveBeenCalled();
  });

  it("fires exactly once 400 ms after a single edit", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
      // Flush the resolved promise chain.
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);
  });

  it("collapses multiple rapid edits within the debounce window to one call", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 90 });
    });
    await act(async () => {
      vi.advanceTimersByTime(100);
      useBuildWorkspaceStore.getState().setMeta({ level: 91 });
    });
    await act(async () => {
      vi.advanceTimersByTime(100);
      useBuildWorkspaceStore.getState().setMeta({ level: 92 });
    });
    await act(async () => {
      vi.advanceTimersByTime(100);
      useBuildWorkspaceStore.getState().setMeta({ level: 93 });
    });

    // Not yet — 400 ms has not elapsed since the last edit.
    expect(buildInline).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);
    expect(buildInline.mock.calls[0][0]).toMatchObject({
      character_class: "Mage",
      mastery: "Sorcerer",
      skill_name: "Fireball",
    });
  });

  it("populates analysisResult on success", async () => {
    buildInline.mockResolvedValue(fakeApiResponse("Fireball"));
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });

    const s = useBuildWorkspaceStore.getState();
    expect(s.analysisStatus).toBe("success");
    expect(s.analysisResult?.primary_skill).toBe("Fireball");
  });

  it("populates analysisError when the endpoint returns an error response", async () => {
    buildInline.mockResolvedValue(fakeApiError("Invalid mastery"));
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });

    const s = useBuildWorkspaceStore.getState();
    expect(s.analysisStatus).toBe("error");
    expect(s.analysisError).toBe("Invalid mastery");
  });

  it("cancels a pending debounce when the component unmounts", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    const { unmount } = renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    unmount();
    await act(async () => {
      vi.advanceTimersByTime(800);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).not.toHaveBeenCalled();
  });

  it("discards a stale response whose requestId is older than the current one", async () => {
    // Two deferred responses: the first (slow) resolves AFTER the second one.
    let resolveSlow: (v: any) => void = () => {};
    let resolveFast: (v: any) => void = () => {};
    const slow = new Promise((r) => {
      resolveSlow = r;
    });
    const fast = new Promise((r) => {
      resolveFast = r;
    });
    // First call (the initial 0 ms fire) resolves immediately so we can
    // reason about subsequent edits; the next two calls are the slow/fast
    // pair under test.
    buildInline
      .mockResolvedValueOnce(fakeApiResponse("initial"))
      .mockReturnValueOnce(slow)
      .mockReturnValueOnce(fast);

    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    // Edit 1 → schedule slow request.
    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 80 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
    });
    expect(buildInline).toHaveBeenCalledTimes(1);

    // Edit 2 → schedule fast request (bumps requestId, slow's id is now stale).
    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 81 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
    });
    expect(buildInline).toHaveBeenCalledTimes(2);

    // Fast resolves first with "fresh".
    await act(async () => {
      resolveFast(fakeApiResponse("fresh"));
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(useBuildWorkspaceStore.getState().analysisResult?.primary_skill).toBe(
      "fresh",
    );

    // Slow resolves afterwards with "stale" — should be silently discarded.
    await act(async () => {
      resolveSlow(fakeApiResponse("stale"));
      await Promise.resolve();
      await Promise.resolve();
    });
    const s = useBuildWorkspaceStore.getState();
    expect(s.analysisResult?.primary_skill).toBe("fresh");
    expect(s.analysisStatus).toBe("success");
  });

  it("re-fires on a subsequent edit after a completed analysis", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 90 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 91 });
    });
    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(2);
  });

  it("does not fire when the build is not simulatable", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    // Empty skills — not simulatable.
    const b = makeSimulatableBuild();
    b.skills = [];
    seedStore(b);
    renderHook(() => useDebouncedAnalysis());

    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 77 });
      vi.advanceTimersByTime(1000);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).not.toHaveBeenCalled();
  });

  it("runAnalysisNow() fires immediately, bypassing the debounce", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());
    await flushInitialFire();

    await act(async () => {
      runAnalysisNow();
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);
  });
});

// ---------------------------------------------------------------------------
// Initial-load fast path (phase 2 step 5)
// ---------------------------------------------------------------------------

describe("useDebouncedAnalysis — initial load", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    buildInline.mockReset();
    useBuildWorkspaceStore.getState().reset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("fires the initial analysis immediately (0 ms) when mounted with a simulatable build", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());

    // No 400 ms wait — advance only the microtask queue and a trivial tick.
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);
  });

  it("uses the standard 400 ms debounce on subsequent edits", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    seedStore();
    renderHook(() => useDebouncedAnalysis());

    // Consume the initial 0 ms fire.
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);

    // Edit — flushes the state update so the effect re-runs BEFORE the
    // clock advances, so the new 400 ms timer is scheduled at t=0-rel.
    await act(async () => {
      useBuildWorkspaceStore.getState().setMeta({ level: 99 });
    });
    await act(async () => {
      vi.advanceTimersByTime(399);
    });
    expect(buildInline).toHaveBeenCalledTimes(1);

    await act(async () => {
      vi.advanceTimersByTime(1);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(2);
  });

  it("for /workspace/new the initial 0 ms fire is a no-op (not simulatable) and later edits use 400 ms", async () => {
    buildInline.mockResolvedValue(fakeApiResponse());
    // Store starts empty + not simulatable.
    useBuildWorkspaceStore.getState().initializeEmpty();
    renderHook(() => useDebouncedAnalysis());

    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });
    // No request fired — the 0 ms timer ran but runAnalysis bailed because
    // the empty build is not simulatable.
    expect(buildInline).not.toHaveBeenCalled();

    // User makes the build simulatable. The edit should use the normal
    // 400 ms debounce, not another 0 ms fire.
    await act(async () => {
      const s = useBuildWorkspaceStore.getState();
      s.setMeta({ character_class: "Mage", mastery: "Sorcerer" });
      s.setSkills([
        {
          id: "s1",
          slot: 0,
          skill_name: "Fireball",
          points_allocated: 20,
          spec_tree: [],
        } as BuildSkill,
      ]);
      vi.advanceTimersByTime(100);
    });
    expect(buildInline).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(400);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(buildInline).toHaveBeenCalledTimes(1);
  });
});
