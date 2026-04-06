/**
 * validateSkillTree.ts — Legality validation for skill tree allocations.
 *
 * Validates:
 *   - Total points ≤ MAX_SKILL_POINTS (20)
 *   - Per-node points ≤ maxPoints
 *   - Parent requirement satisfaction
 *   - Graph reachability from root
 */

import type { SkillNode, SkillAllocationMap } from "@/types/skillTree";
import { MAX_SKILL_POINTS } from "@/types/skillTree";
import { calculateSkillPointsSpent } from "@/logic/skillAllocation";

export interface SkillTreeValidationResult {
  valid: boolean;
  pointsSpent: number;
  pointsRemaining: number;
  errors: string[];
}

/**
 * Validate a complete skill tree allocation.
 */
export function validateSkillTree(
  allocated: SkillAllocationMap,
  nodes: SkillNode[],
): SkillTreeValidationResult {
  const errors: string[] = [];
  const nodeById = new Map<number, SkillNode>();
  for (const n of nodes) nodeById.set(n.id, n);

  const pointsSpent = calculateSkillPointsSpent(allocated);

  // Point limit
  if (pointsSpent > MAX_SKILL_POINTS) {
    errors.push(`Point limit exceeded: ${pointsSpent}/${MAX_SKILL_POINTS}`);
  }

  // Per-node caps
  for (const [nodeId, pts] of allocated) {
    const node = nodeById.get(nodeId);
    if (!node) {
      errors.push(`Unknown node ${nodeId}`);
      continue;
    }
    if (pts > node.maxPoints) {
      errors.push(`${node.name} has ${pts}/${node.maxPoints} points`);
    }
  }

  // Requirement validation
  for (const [nodeId, pts] of allocated) {
    if (pts <= 0) continue;
    const node = nodeById.get(nodeId);
    if (!node) continue;

    for (const req of node.requirements) {
      const parentPts = allocated.get(req.node) ?? 0;
      if (parentPts < req.requirement) {
        const parentNode = nodeById.get(req.node);
        errors.push(
          `${node.name} requires ${req.requirement} points in ${parentNode?.name ?? `node ${req.node}`}, has ${parentPts}`,
        );
      }
    }
  }

  // Reachability from root (node 0)
  if (allocated.size > 0) {
    const children = new Map<number, number[]>();
    for (const node of nodes) {
      for (const req of node.requirements) {
        if (!children.has(req.node)) children.set(req.node, []);
        children.get(req.node)!.push(node.id);
      }
    }

    const visited = new Set<number>();
    const queue: number[] = [0];
    visited.add(0);

    while (queue.length > 0) {
      const current = queue.shift()!;
      for (const childId of children.get(current) ?? []) {
        if (allocated.has(childId) && !visited.has(childId)) {
          visited.add(childId);
          queue.push(childId);
        }
      }
    }

    for (const nid of allocated.keys()) {
      if (!visited.has(nid)) {
        const node = nodeById.get(nid);
        errors.push(`${node?.name ?? `node ${nid}`} is unreachable from root`);
      }
    }
  }

  return {
    valid: errors.length === 0,
    pointsSpent,
    pointsRemaining: MAX_SKILL_POINTS - pointsSpent,
    errors,
  };
}
