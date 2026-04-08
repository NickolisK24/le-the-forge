/**
 * exportBuild.ts — Encode BuildData into a shareable string.
 *
 * Format: base64-encoded JSON.
 * Future: could add compression (e.g. pako/deflate) if strings get large.
 */

import type { BuildData } from "@/types/build";

/**
 * Encode a BuildData object into a base64 string.
 * Returns null if encoding fails.
 */
export function exportBuildToString(build: BuildData): string | null {
  try {
    const json = JSON.stringify(build);
    return btoa(json);
  } catch {
    return null;
  }
}

/**
 * Copy build string to clipboard. Returns true on success.
 */
export async function copyBuildToClipboard(build: BuildData): Promise<boolean> {
  const encoded = exportBuildToString(build);
  if (!encoded) return false;
  try {
    await navigator.clipboard.writeText(encoded);
    return true;
  } catch {
    return false;
  }
}
