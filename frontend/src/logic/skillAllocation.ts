/**
 * skillAllocation.ts — Allocation logic for skill tree nodes.
 *
 * Mirrors the passive allocation pattern but adapts for skill-specific rules:
 *   - Requirements can specify minimum points in parent (not just allocated/not)
 *   - Max 20 total points per skill tree
 *   - Root node (id=0) has maxPoints=0 and is always "allocated"
 *   - BFS connectivity check reuses the same pattern as passives
 */

import type { SkillNode, SkillAllocationMap } from "@/types/skillTree";
import { MAX_SKILL_POINTS } from "@/types/skillTree";

// ---------------------------------------------------------------------------
// Point calculation
// ---------------------------------------------------------------------------

/** Sum all allocated points in a skill tree. */
export function calculateSkillPointsSpent(allocated: SkillAllocationMap): number {
  let total = 0;
  for (const pts of allocated.values()) {
    if (pts > 0 && Number.isFinite(pts)) total += pts;
  }
  return total;
}

// ---------------------------------------------------------------------------
// Availability
// ---------------------------------------------------------------------------

/**
 * Check if a skill node can be allocated.
 *
 * Requirements:
 *   1. Total points spent < MAX_SKILL_POINTS
 *   2. Current points < node.maxPoints
 *   3. All parent requirements met (parent has >= required points)
 *   4. Node is reachable from root via allocated parents
 */
export function canAllocateSkillNode(
  nodeId: number,
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
): boolean {
  const node = nodes.find((n) => n.id === nodeId);
  if (!node) return false;
  if (node.maxPoints === 0) return false; // Root node can't be allocated

  const currentPts = allocated.get(nodeId) ?? 0;
  if (currentPts >= node.maxPoints) return false;

  const totalSpent = calculateSkillPointsSpent(allocated);
  if (totalSpent >= MAX_SKILL_POINTS) return false;

  // Check parent requirements
  for (const req of node.requirements) {
    const parentPts = allocated.get(req.node) ?? 0;
    if (parentPts < req.requirement) return false;
  }

  return true;
}

/**
 * Compute all available (allocatable) nodes in a skill tree.
 */
export function computeAvailableSkillNodes(
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
): Set<number> {
  const available = new Set<number>();
  for (const node of nodes) {
    if (canAllocateSkillNode(node.id, nodes, allocated)) {
      available.add(node.id);
    }
  }
  return available;
}

// ---------------------------------------------------------------------------
// Allocation
// ---------------------------------------------------------------------------

/**
 * Allocate a point into a skill node. Returns new maps or null if invalid.
 */
export function allocateSkillNode(
  nodeId: number,
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
  shiftKey: boolean = false,
): SkillAllocationMap | null {
  const node = nodes.find((n) => n.id === nodeId);
  if (!node) return null;

  if (!canAllocateSkillNode(nodeId, nodes, allocated)) return null;

  const next = new Map(allocated);
  const current = next.get(nodeId) ?? 0;
  const totalSpent = calculateSkillPointsSpent(allocated);
  const maxAdd = Math.min(
    node.maxPoints - current,
    MAX_SKILL_POINTS - totalSpent,
  );

  if (maxAdd <= 0) return null;

  const add = shiftKey ? maxAdd : 1;
  next.set(nodeId, current + add);
  return next;
}

// ---------------------------------------------------------------------------
// Deallocation
// ---------------------------------------------------------------------------

/**
 * Check if a skill node can be safely deallocated.
 *
 * A node can be removed only if no other allocated node
 * has a requirement that depends on this node's points.
 */
export function canDeallocateSkillNode(
  nodeId: number,
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
): boolean {
  const currentPts = allocated.get(nodeId) ?? 0;
  if (currentPts <= 0) return false;

  // Simulate removing one point
  const testPts = currentPts - 1;

  // Check if any allocated node's requirements would break
  for (const node of nodes) {
    if (!allocated.has(node.id) || (allocated.get(node.id) ?? 0) <= 0) continue;
    for (const req of node.requirements) {
      if (req.node === nodeId && testPts < req.requirement) {
        return false; // This child needs more points in our node
      }
    }
  }

  // If removing to 0: also check BFS reachability
  if (testPts === 0) {
    return canFullyRemoveSkillNode(nodeId, nodes, allocated);
  }

  return true;
}

/**
 * Check if fully removing a node (to 0 points) maintains graph connectivity.
 */
function canFullyRemoveSkillNode(
  nodeId: number,
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
): boolean {
  const remaining = new Map(allocated);
  remaining.delete(nodeId);

  if (remaining.size === 0) return true;

  // BFS from root (node 0) through nodes that have allocated parents
  const visited = new Set<number>();
  const queue: number[] = [0]; // Root is always reachable
  visited.add(0);

  // Build adjacency: parent → children
  const children = new Map<number, number[]>();
  for (const node of nodes) {
    for (const req of node.requirements) {
      if (!children.has(req.node)) children.set(req.node, []);
      children.get(req.node)!.push(node.id);
    }
  }

  while (queue.length > 0) {
    const current = queue.shift()!;
    for (const childId of children.get(current) ?? []) {
      if (remaining.has(childId) && !visited.has(childId)) {
        visited.add(childId);
        queue.push(childId);
      }
    }
  }

  // All remaining allocated nodes must be visited
  for (const nid of remaining.keys()) {
    if (!visited.has(nid)) return false;
  }
  return true;
}

/**
 * Deallocate a point from a skill node. Returns new map or null if blocked.
 */
export function deallocateSkillNode(
  nodeId: number,
  nodes: SkillNode[],
  allocated: SkillAllocationMap,
  shiftKey: boolean = false,
): SkillAllocationMap | null {
  if (!canDeallocateSkillNode(nodeId, nodes, allocated)) return null;

  const next = new Map(allocated);
  const current = next.get(nodeId) ?? 0;

  if (shiftKey) {
    // Remove all points (if safe)
    // Check each level down to find the safe minimum
    let safePts = current;
    for (let test = 0; test <= current; test++) {
      // Check if any child requires more than test points
      let blocked = false;
      for (const node of nodes) {
        if (!allocated.has(node.id) || (allocated.get(node.id) ?? 0) <= 0) continue;
        for (const req of node.requirements) {
          if (req.node === nodeId && test < req.requirement) {
            blocked = true;
            break;
          }
        }
        if (blocked) break;
      }
      if (!blocked) {
        safePts = test;
        break;
      }
    }

    if (safePts === 0) {
      // Check full removal safety
      if (canFullyRemoveSkillNode(nodeId, nodes, allocated)) {
        next.delete(nodeId);
      } else {
        next.set(nodeId, 1); // Keep minimum to maintain connectivity
      }
    } else {
      next.set(nodeId, safePts);
    }
  } else {
    // Remove one point
    if (current <= 1) {
      next.delete(nodeId);
    } else {
      next.set(nodeId, current - 1);
    }
  }

  return next;
}
