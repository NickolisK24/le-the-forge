/**
 * loadBuild.ts — Deserialize and validate persisted build data.
 */

import { BUILD_VERSION, type BuildData } from "@/types/build";
import type { PassiveNode } from "@/services/passiveTreeService";

/** Result of a build load attempt */
export interface LoadResult {
  success: boolean;
  allocatedIds: Set<string>;
  allocatedPoints: Map<string, number>;
  classId: string;
  masteryId?: string;
  warnings: string[];
}

/**
 * Deserialize a BuildData object into allocation state.
 *
 * Validates:
 *   - Version compatibility
 *   - Node IDs exist in the provided node set
 *   - Point counts are within valid range (1..max_points)
 *   - No NaN or negative values
 *
 * Invalid nodes are skipped with warnings, not rejected entirely.
 */
export function deserializeBuild(
  build: BuildData,
  availableNodes: PassiveNode[],
): LoadResult {
  const warnings: string[] = [];

  // Version check
  if (build.version !== BUILD_VERSION) {
    warnings.push(`Build version ${build.version} differs from current ${BUILD_VERSION}`);
  }

  // Build node lookup
  const nodeById = new Map<string, PassiveNode>();
  for (const n of availableNodes) nodeById.set(n.id, n);

  const allocatedIds = new Set<string>();
  const allocatedPoints = new Map<string, number>();

  for (const alloc of build.passiveAllocations) {
    // Skip invalid entries
    if (!alloc.nodeId || typeof alloc.nodeId !== "string") {
      warnings.push(`Skipped allocation with invalid nodeId`);
      continue;
    }

    if (!Number.isFinite(alloc.points) || alloc.points <= 0) {
      warnings.push(`Skipped ${alloc.nodeId}: invalid points (${alloc.points})`);
      continue;
    }

    // Verify node exists
    const node = nodeById.get(alloc.nodeId);
    if (!node) {
      warnings.push(`Skipped ${alloc.nodeId}: node not found in tree`);
      continue;
    }

    // Clamp points to max
    const clamped = Math.min(Math.round(alloc.points), node.max_points);
    if (clamped !== alloc.points) {
      warnings.push(`Clamped ${alloc.nodeId} from ${alloc.points} to ${clamped}`);
    }

    allocatedIds.add(alloc.nodeId);
    allocatedPoints.set(alloc.nodeId, clamped);
  }

  return {
    success: true,
    allocatedIds,
    allocatedPoints,
    classId: build.classId,
    masteryId: build.masteryId,
    warnings,
  };
}

// ---------------------------------------------------------------------------
// LocalStorage
// ---------------------------------------------------------------------------

const STORAGE_KEY = "lastEpochBuild";

/**
 * Load build from localStorage. Returns null if nothing saved or data is corrupt.
 */
export function loadBuildFromLocalStorage(): BuildData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);

    // Basic shape validation
    if (
      typeof parsed !== "object" ||
      parsed === null ||
      typeof parsed.version !== "number" ||
      typeof parsed.classId !== "string" ||
      !Array.isArray(parsed.passiveAllocations)
    ) {
      return null;
    }

    return parsed as BuildData;
  } catch {
    return null;
  }
}
