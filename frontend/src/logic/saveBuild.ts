/**
 * saveBuild.ts — Serialize passive tree allocation state for persistence.
 */

import { BUILD_VERSION, type BuildData, type PassiveAllocation } from "@/types/build";

/**
 * Convert current allocation state into a serializable BuildData object.
 *
 * - Filters out zero-point entries
 * - Sorts by nodeId for deterministic output
 * - Stamps with current version and timestamp
 */
export function serializeBuild(
  allocatedPoints: Map<string, number>,
  classId: string,
  masteryId?: string,
): BuildData {
  const allocations: PassiveAllocation[] = [];

  for (const [nodeId, points] of allocatedPoints) {
    if (points > 0 && Number.isFinite(points)) {
      allocations.push({ nodeId, points });
    }
  }

  allocations.sort((a, b) => a.nodeId.localeCompare(b.nodeId));

  return {
    version: BUILD_VERSION,
    classId,
    masteryId,
    passiveAllocations: allocations,
    savedAt: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// LocalStorage
// ---------------------------------------------------------------------------

const STORAGE_KEY = "lastEpochBuild";

/** Save build to localStorage. Returns true on success. */
export function saveBuildToLocalStorage(build: BuildData): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(build));
    return true;
  } catch {
    return false;
  }
}

/** Clear saved build from localStorage. */
export function clearBuildFromLocalStorage(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
