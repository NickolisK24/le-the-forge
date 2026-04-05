/**
 * passiveGraph.ts — Graph utilities for the passive tree allocation system.
 *
 * Uses BFS traversal for:
 *   - Computing which nodes are available for allocation
 *   - Validating that deallocation won't break graph connectivity
 *   - Finding all reachable nodes from start positions
 *   - Dev-mode integrity validation
 *
 * All functions are pure — no mutation of input Sets or Maps.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

// ---------------------------------------------------------------------------
// Node state enum — used by PassiveTreeNode for visual states
// ---------------------------------------------------------------------------

export const enum NodeState {
  LOCKED = 0,
  AVAILABLE = 1,
  ALLOCATED = 2,
}

// ---------------------------------------------------------------------------
// Bidirectional adjacency builder
// ---------------------------------------------------------------------------

/**
 * Build a bidirectional adjacency map from the node list.
 * Computed once per tree load via useMemo in the page.
 *
 * The API `connections` field lists a node's PARENTS. We add edges in
 * both directions so BFS can traverse parent→child and child→parent.
 */
export function buildBidirectionalAdjacency(nodes: PassiveNode[]): Map<string, Set<string>> {
  const adj = new Map<string, Set<string>>();

  for (const node of nodes) {
    if (!adj.has(node.id)) adj.set(node.id, new Set());
  }

  for (const node of nodes) {
    for (const parentId of node.connections) {
      if (!adj.has(parentId)) adj.set(parentId, new Set());
      adj.get(node.id)!.add(parentId);
      adj.get(parentId)!.add(node.id);
    }
  }

  return adj;
}

// Keep old name as alias for backwards compat
export const buildAdjacency = buildBidirectionalAdjacency;

// ---------------------------------------------------------------------------
// Start node detection
// ---------------------------------------------------------------------------

/**
 * Find starting nodes — the true graph roots.
 *
 * Start nodes: mastery_requirement === 0 AND no parent connections.
 * These are the BFS seeds for reachability checks.
 */
export function findStartNodes(nodes: PassiveNode[]): Set<string> {
  const starts = new Set<string>();
  for (const node of nodes) {
    if (node.mastery_requirement === 0 && node.connections.length === 0) {
      starts.add(node.id);
    }
  }
  return starts;
}

// ---------------------------------------------------------------------------
// BFS traversal
// ---------------------------------------------------------------------------

/**
 * Get all nodes reachable from startIds via allocated nodes using BFS.
 */
export function getReachableNodes(
  startIds: Set<string>,
  allocatedIds: Set<string>,
  adjacency: Map<string, Set<string>>,
): Set<string> {
  const visited = new Set<string>();
  const queue: string[] = [];

  for (const startId of startIds) {
    if (allocatedIds.has(startId)) {
      visited.add(startId);
      queue.push(startId);
    }
  }

  while (queue.length > 0) {
    const current = queue.shift()!;
    const neighbors = adjacency.get(current);
    if (!neighbors) continue;

    for (const neighborId of neighbors) {
      if (allocatedIds.has(neighborId) && !visited.has(neighborId)) {
        visited.add(neighborId);
        queue.push(neighborId);
      }
    }
  }

  return visited;
}

// ---------------------------------------------------------------------------
// Available nodes computation
// ---------------------------------------------------------------------------

/**
 * Compute which unallocated nodes are currently available for allocation.
 *
 * A node is available if:
 *   1. mastery_requirement <= totalBasePointsSpent (tier gate met)
 *   2. AND one of:
 *      a. No parent connections (tier root — freely selectable at this tier)
 *      b. At least one parent connection is already allocated
 */
export function computeAvailableNodes(
  nodes: PassiveNode[],
  allocatedIds: Set<string>,
  totalBasePointsSpent: number,
): Set<string> {
  const available = new Set<string>();

  for (const node of nodes) {
    if (allocatedIds.has(node.id)) continue;
    if (totalBasePointsSpent < node.mastery_requirement) continue;

    if (node.connections.length === 0) {
      available.add(node.id);
      continue;
    }

    for (const parentId of node.connections) {
      if (allocatedIds.has(parentId)) {
        available.add(node.id);
        break;
      }
    }
  }

  return available;
}

// ---------------------------------------------------------------------------
// Safe deallocation check
// ---------------------------------------------------------------------------

/**
 * Check whether removing a node would disconnect other allocated nodes
 * from the start nodes.
 *
 * Algorithm:
 *   1. Simulate removal (clone set, delete target)
 *   2. If nothing remains → safe
 *   3. BFS from startIds (NOT tier roots) through remaining allocated nodes
 *   4. Safe only if every remaining node was visited
 *
 * IMPORTANT: BFS roots are ONLY nodes in startIds — not all connectionless
 * nodes. Tier roots at higher mastery_requirements are not valid BFS seeds.
 */
export function canRemoveNode(
  nodeId: string,
  allocatedIds: Set<string>,
  startIds: Set<string>,
  adjacency: Map<string, Set<string>>,
): boolean {
  if (!allocatedIds.has(nodeId)) return false;

  const remaining = new Set(allocatedIds);
  remaining.delete(nodeId);

  // Part 2: empty removal is always safe
  if (remaining.size === 0) return true;

  // Part 1: BFS ONLY from real start nodes that are still allocated
  const reachable = getReachableNodes(startIds, remaining, adjacency);

  return reachable.size === remaining.size;
}

// ---------------------------------------------------------------------------
// Dev-mode integrity check
// ---------------------------------------------------------------------------

/**
 * Validate that all allocated nodes are reachable from start nodes.
 * Logs console.error if the tree is in an invalid state.
 *
 * Only runs in development — no-op in production.
 */
export function validateTreeIntegrity(
  allocatedIds: Set<string>,
  startIds: Set<string>,
  adjacency: Map<string, Set<string>>,
): void {
  if (process.env.NODE_ENV === "production") return;
  if (allocatedIds.size === 0) return;

  const reachable = getReachableNodes(startIds, allocatedIds, adjacency);
  if (reachable.size !== allocatedIds.size) {
    const orphans = [...allocatedIds].filter((id) => !reachable.has(id));
    console.error(
      "[PassiveTree] Invalid tree state detected — orphaned nodes:",
      orphans,
      `(${reachable.size} reachable / ${allocatedIds.size} allocated)`,
    );
  }
}
