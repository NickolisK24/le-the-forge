/**
 * build.ts — Type definitions for persisted build data.
 *
 * Versioned for future compatibility. Version must be bumped
 * whenever the schema changes.
 */

/** Current schema version — increment on breaking changes */
export const BUILD_VERSION = 1;

/** A single node allocation: which node, how many points */
export interface PassiveAllocation {
  nodeId: string;
  points: number;
}

/** Complete serializable build state */
export interface BuildData {
  /** Schema version for migration support */
  version: number;
  /** Character class (e.g. "Acolyte") */
  classId: string;
  /** Selected mastery filter (e.g. "Lich", "__all__", "__base__") */
  masteryId?: string;
  /** Allocated passive nodes with point counts */
  passiveAllocations: PassiveAllocation[];
  /** ISO timestamp of when this build was saved */
  savedAt: string;
}
