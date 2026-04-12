/**
 * findPassivePath.ts — BFS shortest path finder for the passive tree.
 *
 * Finds the shortest path from any start node to a target node
 * through the bidirectional adjacency graph. Pure function, no mutation.
 *
 * Used for:
 *   - Hover path highlighting
 *   - Allocated path visualization
 *   - Debugging unreachable nodes
 */

/**
 * Find the shortest path from any start node to the target node.
 *
 * Uses BFS through the FULL adjacency graph (not just allocated nodes).
 * Returns an ordered array [start, ..., target] or [] if unreachable.
 *
 * @param targetNodeId — the node to find a path to
 * @param adjacency — bidirectional adjacency map (all nodes, not just allocated)
 * @param startNodeIds — set of valid BFS starting points
 */
export function findPathToNode(
  targetNodeId: string,
  adjacency: Map<string, Set<string>>,
  startNodeIds: Set<string>,
): string[] {
  // Target is a start node — path is just itself
  if (startNodeIds.has(targetNodeId)) return [targetNodeId];

  // BFS from all start nodes simultaneously. Head-pointer dequeue keeps this
  // O(n + e); array.shift() was dropping it to O(n²).
  const visited = new Map<string, string | null>(); // nodeId → parent nodeId
  const queue: string[] = [];

  for (const startId of startNodeIds) {
    visited.set(startId, null);
    queue.push(startId);
  }

  let head = 0;
  while (head < queue.length) {
    const current = queue[head++];

    if (current === targetNodeId) {
      // Reconstruct path
      const path: string[] = [];
      let node: string | null = current;
      while (node !== null) {
        path.unshift(node);
        node = visited.get(node) ?? null;
        if (node !== null && visited.get(node) === undefined) break;
      }
      return path;
    }

    const neighbors = adjacency.get(current);
    if (!neighbors) continue;

    for (const next of neighbors) {
      if (!visited.has(next)) {
        visited.set(next, current);
        queue.push(next);
      }
    }
  }

  return []; // Unreachable
}

/**
 * Find paths from start nodes to ALL allocated nodes.
 *
 * Returns a Map of nodeId → path (string[]).
 * Uses BFS from starts, building a spanning tree.
 */
export function findAllAllocatedPaths(
  allocatedIds: Set<string>,
  adjacency: Map<string, Set<string>>,
  startNodeIds: Set<string>,
): Map<string, string[]> {
  if (allocatedIds.size === 0) return new Map();

  // BFS spanning tree from start nodes — head-pointer dequeue, O(n + e).
  const parent = new Map<string, string | null>();
  const queue: string[] = [];

  for (const startId of startNodeIds) {
    parent.set(startId, null);
    queue.push(startId);
  }

  let head = 0;
  while (head < queue.length) {
    const current = queue[head++];
    const neighbors = adjacency.get(current);
    if (!neighbors) continue;

    for (const next of neighbors) {
      if (!parent.has(next)) {
        parent.set(next, current);
        queue.push(next);
      }
    }
  }

  // Reconstruct path for each allocated node
  const paths = new Map<string, string[]>();
  for (const nodeId of allocatedIds) {
    const path: string[] = [];
    let current: string | null = nodeId;
    while (current !== null && parent.has(current)) {
      path.unshift(current);
      current = parent.get(current) ?? null;
    }
    if (path.length > 0) {
      paths.set(nodeId, path);
    }
  }

  return paths;
}

/**
 * Collect all unique node IDs that appear in any path.
 * Used to determine which nodes to highlight.
 */
export function collectPathNodes(paths: Map<string, string[]>): Set<string> {
  const nodeSet = new Set<string>();
  for (const path of paths.values()) {
    for (const nodeId of path) {
      nodeSet.add(nodeId);
    }
  }
  return nodeSet;
}

/**
 * Collect all edges that appear in any path.
 * Returns a Set of "fromId-toId" strings for fast lookup.
 */
export function collectPathEdges(paths: Map<string, string[]>): Set<string> {
  const edgeSet = new Set<string>();
  for (const path of paths.values()) {
    for (let i = 0; i < path.length - 1; i++) {
      const a = path[i], b = path[i + 1];
      // Add both directions for bidirectional matching
      edgeSet.add(`${a}-${b}`);
      edgeSet.add(`${b}-${a}`);
    }
  }
  return edgeSet;
}
