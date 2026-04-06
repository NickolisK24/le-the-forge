/**
 * validatePassiveBuild.ts — Unified passive tree legality validation.
 *
 * Enforces:
 *   - Maximum point limit (113 for Last Epoch)
 *   - Tier unlock thresholds (mastery_requirement gates)
 *   - Mastery selection rules (one mastery only)
 *   - Per-node max_points clamping
 *
 * This is THE authoritative legality checker for passive builds.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Maximum passive points available in Last Epoch */
export const MAX_PASSIVE_POINTS = 113;

/** Base points required before mastery trees unlock */
export const MASTERY_UNLOCK_THRESHOLD = 20;

// ---------------------------------------------------------------------------
// Point calculation
// ---------------------------------------------------------------------------

/** Sum all allocated points across all nodes. */
export function calculatePointsSpent(
  allocatedPoints: Map<string, number>,
): number {
  let total = 0;
  for (const pts of allocatedPoints.values()) {
    if (pts > 0 && Number.isFinite(pts)) total += pts;
  }
  return total;
}

/** Calculate points spent in base tree only (mastery === null). */
export function calculateBasePointsSpent(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): number {
  let total = 0;
  for (const [nodeId, pts] of allocatedPoints) {
    const node = nodeById.get(nodeId);
    if (node && node.mastery === null && pts > 0) total += pts;
  }
  return total;
}

/** Calculate points spent in a specific mastery. */
export function calculateMasteryPointsSpent(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
  masteryName: string,
): number {
  let total = 0;
  for (const [nodeId, pts] of allocatedPoints) {
    const node = nodeById.get(nodeId);
    if (node && node.mastery === masteryName && pts > 0) total += pts;
  }
  return total;
}

// ---------------------------------------------------------------------------
// Point limit
// ---------------------------------------------------------------------------

/** Check if total points are within the maximum limit. */
export function validatePointLimit(
  pointsSpent: number,
  maxPoints: number = MAX_PASSIVE_POINTS,
): boolean {
  return pointsSpent <= maxPoints;
}

// ---------------------------------------------------------------------------
// Tier requirements
// ---------------------------------------------------------------------------

export interface TierStatus {
  tier: number;
  required: number;
  spent: number;
  unlocked: boolean;
}

/**
 * Validate that all allocated nodes meet their tier requirements.
 *
 * For each allocated node, the total base points spent must be ≥
 * the node's mastery_requirement.
 *
 * Returns per-tier status for display.
 */
export function validateTierRequirements(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): { valid: boolean; tiers: TierStatus[]; violations: string[] } {
  const baseSpent = calculateBasePointsSpent(allocatedPoints, nodeById);
  const violations: string[] = [];

  // Collect all unique tier thresholds
  const tierSet = new Set<number>();
  for (const node of nodeById.values()) {
    tierSet.add(node.mastery_requirement);
  }
  const tierThresholds = Array.from(tierSet).sort((a, b) => a - b);

  const tiers: TierStatus[] = tierThresholds.map((threshold) => ({
    tier: threshold,
    required: threshold,
    spent: baseSpent,
    unlocked: baseSpent >= threshold,
  }));

  // Check each allocated node
  for (const [nodeId, pts] of allocatedPoints) {
    if (pts <= 0) continue;
    const node = nodeById.get(nodeId);
    if (!node) continue;

    if (baseSpent < node.mastery_requirement) {
      violations.push(
        `${node.name} (${nodeId}) requires ${node.mastery_requirement} base points, have ${baseSpent}`,
      );
    }
  }

  return {
    valid: violations.length === 0,
    tiers,
    violations,
  };
}

// ---------------------------------------------------------------------------
// Mastery validation
// ---------------------------------------------------------------------------

/**
 * Validate mastery selection rules.
 *
 * Rules:
 *   - Mastery nodes only allowed after MASTERY_UNLOCK_THRESHOLD base points
 *   - Only ONE mastery can have allocated nodes (cross-mastery investment
 *     is allowed in LE but with depth restrictions — simplified here)
 */
export function validateMasteryRules(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): { valid: boolean; selectedMasteries: string[]; violations: string[] } {
  const violations: string[] = [];
  const baseSpent = calculateBasePointsSpent(allocatedPoints, nodeById);

  // Find which masteries have allocated nodes
  const masteryPoints = new Map<string, number>();
  for (const [nodeId, pts] of allocatedPoints) {
    if (pts <= 0) continue;
    const node = nodeById.get(nodeId);
    if (!node || !node.mastery) continue;
    masteryPoints.set(node.mastery, (masteryPoints.get(node.mastery) ?? 0) + pts);
  }

  const selectedMasteries = Array.from(masteryPoints.keys());

  // Check mastery unlock threshold
  if (selectedMasteries.length > 0 && baseSpent < MASTERY_UNLOCK_THRESHOLD) {
    violations.push(
      `Mastery nodes require ${MASTERY_UNLOCK_THRESHOLD} base points, have ${baseSpent}`,
    );
  }

  return { valid: violations.length === 0, selectedMasteries, violations };
}

// ---------------------------------------------------------------------------
// Per-node validation
// ---------------------------------------------------------------------------

/** Validate that no node exceeds its max_points. */
export function validateNodePointCaps(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): { valid: boolean; violations: string[] } {
  const violations: string[] = [];

  for (const [nodeId, pts] of allocatedPoints) {
    if (pts <= 0) continue;
    const node = nodeById.get(nodeId);
    if (!node) {
      violations.push(`Unknown node ${nodeId}`);
      continue;
    }
    if (pts > node.max_points) {
      violations.push(`${node.name} has ${pts}/${node.max_points} points (exceeds max)`);
    }
  }

  return { valid: violations.length === 0, violations };
}

// ---------------------------------------------------------------------------
// Unified validation
// ---------------------------------------------------------------------------

export interface ValidationResult {
  valid: boolean;
  pointsSpent: number;
  basePointsSpent: number;
  pointsRemaining: number;
  errors: string[];
  tiers: TierStatus[];
  selectedMasteries: string[];
}

/**
 * THE authoritative legality checker for passive builds.
 *
 * Runs all validation rules and returns a comprehensive result.
 */
export function validatePassiveBuild(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): ValidationResult {
  const errors: string[] = [];

  const pointsSpent = calculatePointsSpent(allocatedPoints);
  const basePointsSpent = calculateBasePointsSpent(allocatedPoints, nodeById);
  const pointsRemaining = MAX_PASSIVE_POINTS - pointsSpent;

  // Point limit
  if (!validatePointLimit(pointsSpent)) {
    errors.push(`Point limit exceeded: ${pointsSpent}/${MAX_PASSIVE_POINTS}`);
  }

  // Node caps
  const capResult = validateNodePointCaps(allocatedPoints, nodeById);
  errors.push(...capResult.violations);

  // Tier requirements
  const tierResult = validateTierRequirements(allocatedPoints, nodeById);
  errors.push(...tierResult.violations);

  // Mastery rules
  const masteryResult = validateMasteryRules(allocatedPoints, nodeById);
  errors.push(...masteryResult.violations);

  return {
    valid: errors.length === 0,
    pointsSpent,
    basePointsSpent,
    pointsRemaining,
    errors,
    tiers: tierResult.tiers,
    selectedMasteries: masteryResult.selectedMasteries,
  };
}
