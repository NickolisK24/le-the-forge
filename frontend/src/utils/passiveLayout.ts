/**
 * passiveLayout.ts — Layout computation for passive tree rendering.
 *
 * Converts game-coordinate nodes into screen-space positions with
 * Y-axis flipped (game is Y-up, SVG is Y-down), centered in the canvas.
 */

import type { PassiveNode } from "@/services/passiveTreeService";

export interface LayoutResult {
  positions: Map<string, { sx: number; sy: number; masteryIndex: number }>;
  edges: Array<{ fromId: string; toId: string }>;
  scale: number;
}

export function computeLayout(
  nodes: PassiveNode[],
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions = new Map<string, { sx: number; sy: number; masteryIndex: number }>();
  const edges: Array<{ fromId: string; toId: string }> = [];

  if (nodes.length === 0) return { positions, edges, scale: 1 };

  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const midX = (minX + maxX) / 2;
  const midY = (minY + maxY) / 2;
  const treeW = maxX - minX || 1;
  const treeH = maxY - minY || 1;
  const pad = 60;
  const scale = Math.min((canvasW - pad * 2) / treeW, (canvasH - pad * 2) / treeH);

  const idSet = new Set(nodes.map((n) => n.id));
  for (const node of nodes) {
    const lx = node.x - midX;
    const ly = -(node.y - midY); // flip Y
    positions.set(node.id, {
      sx: lx * scale + canvasW / 2,
      sy: ly * scale + canvasH / 2,
      masteryIndex: node.mastery_index,
    });
  }
  for (const node of nodes) {
    for (const connId of node.connections) {
      if (idSet.has(connId)) edges.push({ fromId: connId, toId: node.id });
    }
  }
  return { positions, edges, scale };
}
