/**
 * importBuild.ts — Decode a build string back into BuildData.
 *
 * Validates structure before returning. Never trusts input directly —
 * callers must still run deserializeBuild() for node-level validation.
 */

import type { BuildData } from "@/types/build";

/**
 * Decode a base64-encoded build string into BuildData.
 * Returns null if the string is invalid, corrupt, or fails validation.
 */
export function importBuildFromString(encoded: string): BuildData | null {
  try {
    const trimmed = encoded.trim();
    if (!trimmed) return null;

    const json = atob(trimmed);
    const parsed = JSON.parse(json);

    // Shape validation
    if (typeof parsed !== "object" || parsed === null) return null;
    if (typeof parsed.version !== "number") return null;
    if (typeof parsed.classId !== "string" || !parsed.classId) return null;
    if (!Array.isArray(parsed.passiveAllocations)) return null;

    // Validate each allocation entry
    for (const alloc of parsed.passiveAllocations) {
      if (typeof alloc.nodeId !== "string") return null;
      if (typeof alloc.points !== "number") return null;
    }

    return parsed as BuildData;
  } catch {
    return null;
  }
}
