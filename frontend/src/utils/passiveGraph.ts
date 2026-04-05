/**
 * passiveGraph.ts — Graph utilities for the passive tree allocation system.
 *
 * Uses BFS traversal for:
 *   - Computing which nodes are available for allocation
 *   - Validating that deallocation won't break graph connectivity
 *   - Finding all reachable nodes from start positions
 *
 * All functions are pure — no mutation of input Sets or Maps.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

// ---------------------------------------------------------------------------
// Adjacency builder
// ---------------------------------------------------------------------------

/**
 * Build a bidirectional adjacency map from the node list.
 *
 * The API `connections` field lists a node's PARENTS. We need bidirectional
 * edges so that traversal works in both directions (parent→child, child→parent).
 */
export function buildAdjacency(nodes: PassiveNode[]): Map<string, Set<string>> {
  const adj = new Map<string, Set<string>>();

  // Initialize all nodes
  for (const node of nodes) {
    if (!adj.has(node.id)) adj.set(node.id, new Set());
  }

  // Add bidirectional edges from connections (connections = parent IDs)
  for (const node of nodes) {
    for (const parentId of node.connections) {
      adj.get(node.id)?.add(parentId);
      adj.get(parentId)?.add(node.id);
    }
  }

  return adj;
}

// ---------------------------------------------------------------------------
// Start node detection
// ---------------------------------------------------------------------------

/**
 * Find starting nodes for a set of passive nodes.
 *
 * Starting nodes are base class nodes (mastery === null) with
 * mastery_requirement === 0. These are always selectable when
 * the mastery_requirement gate is met (which is trivially true for req=0).
 *
 * Additionally, any node whose mastery_requirement is met AND has no
 * parent connections is a "tier root" — selectable without needing
 * an allocated neighbor.
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
 * Get all nodes reachable from a set of start IDs via allocated nodes.
 *
 * Traverses only through nodes present in `allocatedIds`.
 * Returns the set of all reachable allocated node IDs.
 */
export function getReachableNodes(
  startIds: Set<string>,
  allocatedIds: Set<string>,
  adjacency: Map<string, Set<string>>,
): Set<string> {
  const visited = new Set<string>();
  const queue: string[] = [];

  // Seed BFS from allocated start nodes
  for (const startId of startIds) {
    if (allocatedIds.has(startId)) {
      visited.add(startId);
      queue.push(startId);
    }
  }

  // BFS through allocated neighbors
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

/**
 * Check whether a specific node is reachable from start nodes through allocated nodes.
 */
export function isNodeReachable(
  targetId: string,
  startIds: Set<string>,
  allocatedIds: Set<string>,
  adjacency: Map<string, Set<string>>,
): boolean {
  return getReachableNodes(startIds, allocatedIds, adjacency).has(targetId);
}

// ---------------------------------------------------------------------------
// Available nodes computation
// ---------------------------------------------------------------------------

/**
 * Compute which nodes are currently available for allocation.
 *
 * A node is available if:
 *   1. mastery_requirement <= totalBasePointsSpent (tier gate met)
 *   2. AND one of:
 *      a. Node has no parent connections (tier root — freely selectable)
 *      b. At least one parent connection is already allocated
 */
export function computeAvailableNodes(
  nodes: PassiveNode[],
  allocatedIds: Set<string>,
  _startIds: Set<string>,
  adjacency: Map<string, Set<string>>,
  totalBasePointsSpent: number,
): Set<string> {
  const available = new Set<string>();

  for (const node of nodes) {
    // Skip already allocated nodes
    if (allocatedIds.has(node.id)) continue;

    // Check mastery requirement gate
    if (totalBasePointsSpent < node.mastery_requirement) continue;

    // Nodes with no parent connections are tier roots — always available
    // when their mastery_requirement is met
    if (node.connections.length === 0) {
      available.add(node.id);
      continue;
    }

    // Check if any parent (connection) is allocated
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
 * from their start nodes.
 *
 * Uses FULL BFS reachability validation:
 *   1. Simulate removal (clone allocated set, delete target)
 *   2. Find all tier-root nodes in remaining set (no parent connections)
 *   3. BFS outward from tier roots through bidirectional adjacency
 *   4. If every remaining allocated node is visited → safe to remove
 *   5. If any remaining node is unreachable → removal blocked
 *
 * This guarantees no allocated node becomes disconnected from a valid
 * root, even in complex multi-path graph topologies.
 *
 * Returns true if removal is safe.
 */
export function canRemoveNode(
  nodeId: string,
  allocatedIds: Set<string>,
  startIds: Set<string>,
  adjacency: Map<string, Set<string>>,
  nodes?: PassiveNode[],
): boolean {
  if (!allocatedIds.has(nodeId)) return false;

  // Simulate removal
  const remaining = new Set(allocatedIds);
  remaining.delete(nodeId);

  if (remaining.size === 0) return true;

  // Find all valid roots in the remaining set:
  // - Start nodes (req=0, no connections) that are still allocated
  // - Tier root nodes (no parent connections) that are still allocated
  const roots = new Set<string>();

  if (nodes) {
    for (const node of nodes) {
      if (!remaining.has(node.id)) continue;
      if (node.connections.length === 0) {
        roots.add(node.id);
      }
    }
  } else {
    // Fallback: use startIds
    for (const sid of startIds) {
      if (remaining.has(sid)) roots.add(sid);
    }
  }

  // BFS from all roots through remaining allocated nodes via bidirectional adjacency
  const visited = new Set<string>();
  const queue: string[] = [];

  for (const rootId of roots) {
    visited.add(rootId);
    queue.push(rootId);
  }

  while (queue.length > 0) {
    const current = queue.shift()!;
    const neighbors = adjacency.get(current);
    if (!neighbors) continue;

    for (const neighborId of neighbors) {
      if (remaining.has(neighborId) && !visited.has(neighborId)) {
        visited.add(neighborId);
        queue.push(neighborId);
      }
    }
  }

  // Safe only if every remaining allocated node was reached
  return visited.size === remaining.size;
}
