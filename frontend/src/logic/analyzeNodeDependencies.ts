/**
 * analyzeNodeDependencies.ts — Read-only dependency analysis for passive nodes.
 *
 * Explains WHY a node is locked, available, or cannot be removed.
 * Never mutates graph state or allocations.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

export interface DependencyReport {
  nodeId: string;
  nodeName: string;
  /** Whether this node is reachable from a start via the full graph (not just allocated) */
  reachableFromStart: boolean;
  /** Parent nodes (from connections[]) */
  parentIds: string[];
  /** Which parents are currently allocated */
  allocatedParents: string[];
  /** Which parents are NOT allocated (blocking prerequisites) */
  missingParents: string[];
  /** Child nodes that depend on this node (list this node in their connections) */
  childIds: string[];
  /** Allocated children that would be orphaned if this node were removed */
  blockingChildren: string[];
  /** Whether the tier requirement is met */
  tierRequirementMet: boolean;
  /** Current base points vs required */
  tierPoints: { current: number; required: number };
  /** Whether the node is a tier root (no parent connections) */
  isTierRoot: boolean;
  /** Whether this node is currently allocated */
  isAllocated: boolean;
  /** Whether this node can be removed without breaking the tree */
  canRemove: boolean;
  /** Human-readable explanation of the node's current state */
  reason: string;
}

/**
 * Analyze all dependency information for a single node.
 *
 * This is a READ-ONLY analysis — it does not modify any state.
 */
export function analyzeNodeDependencies(
  nodeId: string,
  nodes: PassiveNode[],
  allocatedIds: Set<string>,
  allocatedPoints: Map<string, number>,
  adjacency: Map<string, Set<string>>,
  startIds: Set<string>,
  basePointsSpent: number,
): DependencyReport {
  const node = nodes.find((n) => n.id === nodeId);
  if (!node) {
    return emptyReport(nodeId, "Node not found in tree data");
  }

  const isAllocated = allocatedIds.has(nodeId);
  const isTierRoot = node.connections.length === 0;
  const tierRequirementMet = basePointsSpent >= node.mastery_requirement;

  // Parents: nodes listed in this node's connections[]
  const parentIds = [...node.connections];
  const allocatedParents = parentIds.filter((pid) => allocatedIds.has(pid));
  const missingParents = parentIds.filter((pid) => !allocatedIds.has(pid));

  // Children: nodes that list THIS node in their connections[]
  const childIds: string[] = [];
  for (const n of nodes) {
    if (n.connections.includes(nodeId)) {
      childIds.push(n.id);
    }
  }
  const blockingChildren = childIds.filter((cid) => allocatedIds.has(cid));

  // Reachability: can we reach this node from any start via adjacency?
  const reachableFromStart = isReachable(nodeId, adjacency, startIds);

  // Can remove: simulate removal and check connectivity
  let canRemove = false;
  if (isAllocated) {
    canRemove = checkRemovalSafe(nodeId, allocatedIds, nodes, adjacency);
  }

  // Build explanation
  const reason = buildExplanation(
    node, isAllocated, isTierRoot, tierRequirementMet,
    basePointsSpent, allocatedParents, missingParents,
    blockingChildren, canRemove,
  );

  return {
    nodeId,
    nodeName: node.name,
    reachableFromStart,
    parentIds,
    allocatedParents,
    missingParents,
    childIds,
    blockingChildren,
    tierRequirementMet,
    tierPoints: { current: basePointsSpent, required: node.mastery_requirement },
    isTierRoot,
    isAllocated,
    canRemove,
    reason,
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function emptyReport(nodeId: string, reason: string): DependencyReport {
  return {
    nodeId, nodeName: "Unknown", reachableFromStart: false,
    parentIds: [], allocatedParents: [], missingParents: [],
    childIds: [], blockingChildren: [],
    tierRequirementMet: false, tierPoints: { current: 0, required: 0 },
    isTierRoot: false, isAllocated: false, canRemove: false, reason,
  };
}

function isReachable(
  targetId: string,
  adjacency: Map<string, Set<string>>,
  startIds: Set<string>,
): boolean {
  const visited = new Set<string>();
  const queue = [...startIds];
  for (const id of startIds) visited.add(id);
  while (queue.length > 0) {
    const current = queue.shift()!;
    if (current === targetId) return true;
    const neighbors = adjacency.get(current);
    if (!neighbors) continue;
    for (const next of neighbors) {
      if (!visited.has(next)) {
        visited.add(next);
        queue.push(next);
      }
    }
  }
  return false;
}

function checkRemovalSafe(
  nodeId: string,
  allocatedIds: Set<string>,
  nodes: PassiveNode[],
  adjacency: Map<string, Set<string>>,
): boolean {
  const remaining = new Set(allocatedIds);
  remaining.delete(nodeId);
  if (remaining.size === 0) return true;

  // Find roots: remaining nodes with no connections
  const roots = new Set<string>();
  for (const n of nodes) {
    if (remaining.has(n.id) && n.connections.length === 0) {
      roots.add(n.id);
    }
  }

  // BFS from roots
  const visited = new Set<string>();
  const queue = [...roots];
  for (const r of roots) visited.add(r);
  while (queue.length > 0) {
    const current = queue.shift()!;
    const neighbors = adjacency.get(current);
    if (!neighbors) continue;
    for (const next of neighbors) {
      if (remaining.has(next) && !visited.has(next)) {
        visited.add(next);
        queue.push(next);
      }
    }
  }
  return visited.size === remaining.size;
}

function buildExplanation(
  node: PassiveNode,
  isAllocated: boolean,
  isTierRoot: boolean,
  tierMet: boolean,
  basePoints: number,
  allocatedParents: string[],
  missingParents: string[],
  blockingChildren: string[],
  canRemove: boolean,
): string {
  if (isAllocated) {
    if (canRemove) return "Allocated — can be safely removed";
    if (blockingChildren.length > 0)
      return `Cannot remove — ${blockingChildren.length} child node(s) depend on this`;
    return "Cannot remove — removing would disconnect other nodes";
  }

  // Not allocated — explain why it might be locked
  if (!tierMet) {
    const needed = node.mastery_requirement - basePoints;
    return `Locked — requires ${needed} more base points (need ${node.mastery_requirement}, have ${basePoints})`;
  }

  if (isTierRoot) return "Available — tier root (no prerequisites)";

  if (missingParents.length === node.connections.length)
    return `Locked — no parent nodes allocated (needs one of: ${node.connections.join(", ")})`;

  if (allocatedParents.length > 0)
    return "Available — parent requirement met";

  return "Locked — prerequisites not met";
}
