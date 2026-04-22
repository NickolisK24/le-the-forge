/**
 * useDebouncedAnalysis — phase 2 of the unified build workspace.
 *
 * Subscribes to the build fields in `useBuildWorkspaceStore` that affect
 * analysis output, debounces changes by 400 ms, and posts the working copy
 * to `/api/simulate/build`. Successful responses populate `analysisResult`;
 * errors populate `analysisError`. All responses are tagged with a monotonic
 * requestId so slower-older responses never overwrite a fresher newer one.
 *
 * Mount this hook **once** at the page level — mounting it per-section would
 * fire the same request multiple times.
 *
 * See docs/unified-planner-phase2-notes.md for endpoint baseline details and
 * docs/unified-planner-design.md §2 for the "analysis is decoupled from
 * editing" architectural constraint this hook enforces.
 */

import { useCallback, useEffect, useRef } from "react";

import {
  simulateApi,
  type SimulateBuildInlinePayload,
} from "@/lib/api";
import { useBuildWorkspaceStore } from "@/store";
import type { BuildWorkspaceBuild } from "@/store/buildWorkspace";

const DEFAULT_DEBOUNCE_MS = 400;

// ---------------------------------------------------------------------------
// Pure helpers — exported for unit tests.
// ---------------------------------------------------------------------------

/**
 * A build is "simulatable" if it has enough data for the backend to return
 * a non-degenerate analysis. Below this threshold the panel shows the idle
 * empty-state message regardless of whether edits have occurred.
 *
 * Required:
 *  - non-empty character_class
 *  - non-empty mastery (the backend rejects missing/mismatched mastery)
 *  - at least one skill with a non-empty skill_name
 */
export function buildIsSimulatable(build: BuildWorkspaceBuild): boolean {
  if (!build.character_class) return false;
  if (!build.mastery) return false;
  if (!build.skills || build.skills.length === 0) return false;
  return build.skills.some(
    (s) => typeof s.skill_name === "string" && s.skill_name.length > 0,
  );
}

/**
 * Translate the workspace working copy into the stateless-endpoint payload.
 * The first skill slot with a non-empty name drives primary DPS (matching
 * build_analysis_service.analyze_build behaviour). Skill level clamps to
 * at least 1 because the schema validates `min=1`.
 */
export function buildAnalysisPayload(
  build: BuildWorkspaceBuild,
): SimulateBuildInlinePayload {
  const sortedSkills = [...build.skills].sort((a, b) => a.slot - b.slot);
  const primary = sortedSkills.find((s) => s.skill_name) ?? sortedSkills[0];
  const skillName = primary?.skill_name ?? "";
  const skillLevel = Math.max(1, primary?.points_allocated || 20);

  const gearAffixes: { name: string; tier: number }[] = [];
  for (const slot of build.gear ?? []) {
    for (const a of slot.affixes ?? []) {
      gearAffixes.push({ name: a.name, tier: a.tier });
    }
  }

  return {
    character_class: build.character_class,
    mastery: build.mastery,
    skill_name: skillName,
    skill_level: skillLevel,
    allocated_node_ids: [...(build.passive_tree ?? [])],
    gear_affixes: gearAffixes,
  };
}

// ---------------------------------------------------------------------------
// Imperative "run now" registry — used by the AnalysisPanel's retry button
// to bypass the debounce. A module-level ref is simpler than threading a
// callback through Context or a render prop, and because the hook is
// intended to be mounted exactly once at the page level there is no
// ambiguity about which instance holds the active runner.
// ---------------------------------------------------------------------------

let activeRunner: (() => void) | null = null;

/** Fire an analysis request immediately, bypassing the debounce. No-op if
 *  the hook is not currently mounted. */
export function runAnalysisNow(): void {
  activeRunner?.();
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export interface UseDebouncedAnalysisOptions {
  /** Override the 400 ms debounce window. Exposed for tests; product code
   *  should take the default. */
  debounceMs?: number;
}

export function useDebouncedAnalysis(
  opts: UseDebouncedAnalysisOptions = {},
): void {
  const debounceMs = opts.debounceMs ?? DEFAULT_DEBOUNCE_MS;

  // Narrow subscriptions — only the fields that change the analysis result.
  // (Name/description/flags/cycle/patch are UI metadata and are intentionally
  // excluded.)
  const characterClass = useBuildWorkspaceStore((s) => s.build.character_class);
  const mastery = useBuildWorkspaceStore((s) => s.build.mastery);
  const level = useBuildWorkspaceStore((s) => s.build.level);
  const skills = useBuildWorkspaceStore((s) => s.build.skills);
  const passiveTree = useBuildWorkspaceStore((s) => s.build.passive_tree);
  const gear = useBuildWorkspaceStore((s) => s.build.gear);
  const blessings = useBuildWorkspaceStore((s) => s.build.blessings);
  const workspaceStatus = useBuildWorkspaceStore((s) => s.status);

  const requestAnalysis = useBuildWorkspaceStore((s) => s.requestAnalysis);
  const setAnalysisResult = useBuildWorkspaceStore((s) => s.setAnalysisResult);
  const setAnalysisError = useBuildWorkspaceStore((s) => s.setAnalysisError);

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  // runAnalysis reads the latest build from the store rather than from a
  // captured closure — this is important because the module-level
  // `activeRunner` may be invoked long after its callback was last rebuilt.
  const runAnalysis = useCallback(async () => {
    const build = useBuildWorkspaceStore.getState().build;
    if (!buildIsSimulatable(build)) return;

    const id = requestAnalysis();
    try {
      const res = await simulateApi.buildInline(buildAnalysisPayload(build));
      if (!mountedRef.current) return;
      if (res.data) {
        setAnalysisResult(id, res.data);
      } else {
        const msg = res.errors?.[0]?.message ?? "Analysis failed";
        setAnalysisError(id, msg);
      }
    } catch (err) {
      if (!mountedRef.current) return;
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setAnalysisError(id, msg);
    }
  }, [requestAnalysis, setAnalysisResult, setAnalysisError]);

  // Publish the current runner for imperative callers (e.g. retry button).
  useEffect(() => {
    activeRunner = runAnalysis;
    return () => {
      if (activeRunner === runAnalysis) activeRunner = null;
    };
  }, [runAnalysis]);

  // Debounced trigger on any watched field change.
  useEffect(() => {
    if (workspaceStatus !== "ready") return;
    // Note: the simulatability check runs inside runAnalysis so that if the
    // build becomes simulatable mid-debounce we still fire. Before firing
    // we re-read the latest store state and bail if it is no longer
    // simulatable.

    if (timerRef.current !== null) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
      void runAnalysis();
    }, debounceMs);

    return () => {
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [
    characterClass,
    mastery,
    level,
    skills,
    passiveTree,
    gear,
    blessings,
    workspaceStatus,
    debounceMs,
    runAnalysis,
  ]);

  // Unmount cleanup — cancel the debounce and ensure any in-flight promise
  // that resolves after unmount is discarded via the mountedRef guard.
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);
}
