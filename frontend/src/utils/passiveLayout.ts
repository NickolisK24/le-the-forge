/**
 * passiveLayout.ts — Layout computation for passive tree rendering.
 *
 * Positions nodes in tree-coordinate space (with Y flipped: game is Y-up,
 * SVG is Y-down) and returns the bounding box that encloses them plus a
 * small padding margin. Consumers use the bbox as the SVG viewBox, which
 * (together with preserveAspectRatio="xMidYMid meet") auto-fits the tree
 * into the container — filling ~90% with a centered, proportional layout.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

export interface LayoutResult {
  /** Positions in tree-coord space (Y flipped). */
  positions: Map<string, { sx: number; sy: number; masteryIndex: number }>;
  edges: Array<{ fromId: string; toId: string }>;
  /** Bounding box of all node positions, with ~5% padding on each side. */
  bbox: { x: number; y: number; width: number; height: number };
}

// Fraction of tree extent to add as padding on each side (5% → bbox is
// ~10% larger than the raw tree extent, so the tree fills ~90% of the
// container when preserveAspectRatio="xMidYMid meet" is used).
const PADDING_FRACTION = 0.05;

export function computeLayout(nodes: PassiveNode[]): LayoutResult {
  const positions = new Map<string, { sx: number; sy: number; masteryIndex: number }>();
  const edges: Array<{ fromId: string; toId: string }> = [];

  if (nodes.length === 0) {
    return { positions, edges, bbox: { x: 0, y: 0, width: 1, height: 1 } };
  }

  // Place each node at its tree coordinate, flipping Y (game is Y-up,
  // SVG is Y-down). Don't scale or recenter — the SVG viewBox handles that.
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;

  for (const node of nodes) {
    const sx = node.x;
    const sy = -node.y;
    positions.set(node.id, { sx, sy, masteryIndex: node.mastery_index });
    if (sx < minX) minX = sx;
    if (sx > maxX) maxX = sx;
    if (sy < minY) minY = sy;
    if (sy > maxY) maxY = sy;
  }

  const idSet = new Set(nodes.map((n) => n.id));
  for (const node of nodes) {
    for (const connId of node.connections) {
      if (idSet.has(connId)) edges.push({ fromId: connId, toId: node.id });
    }
  }

  const rawW = maxX - minX || 1;
  const rawH = maxY - minY || 1;
  const padX = rawW * PADDING_FRACTION;
  const padY = rawH * PADDING_FRACTION;

  return {
    positions,
    edges,
    bbox: {
      x: minX - padX,
      y: minY - padY,
      width: rawW + 2 * padX,
      height: rawH + 2 * padY,
    },
  };
}
