/**
 * PassiveTreeConnections — draws SVG lines between connected passive nodes.
 *
 * Three visual states per edge:
 *   - Allocated: both endpoints allocated → bright, thick
 *   - Highlighted: edge is on the hover path → amber, medium
 *   - Idle: default → dim, thin
 */

import { memo } from "react";

interface Position {
  sx: number;
  sy: number;
  masteryIndex: number;
}

const EDGE_IDLE: Record<number, string> = {
  0: "#252940", 1: "#152232", 2: "#2e2010", 3: "#200e32",
};

const EDGE_ACTIVE: Record<number, string> = {
  0: "#6670a0", 1: "#00a8c0", 2: "#c08018", 3: "#9050d8",
};

const EDGE_HIGHLIGHT = "#f0a020";

interface Edge {
  fromId: string;
  toId: string;
}

interface Props {
  edges: Edge[];
  positions: Map<string, Position>;
  allocatedIds: Set<string>;
  /** Set of "fromId-toId" edge keys that should be highlighted */
  highlightedEdges?: Set<string>;
  /** Idle stroke width in coord (viewBox) units. Scales with the tree. */
  strokeIdle?: number;
  /** Highlighted stroke width in coord units. */
  strokeHighlighted?: number;
  /** Allocated stroke width in coord units. */
  strokeAllocated?: number;
}

function PassiveTreeConnectionsInner({
  edges,
  positions,
  allocatedIds,
  highlightedEdges,
  strokeIdle = 3,
  strokeHighlighted = 4.2,
  strokeAllocated = 5.4,
}: Props) {
  return (
    <g>
      {edges.map(({ fromId, toId }) => {
        const from = positions.get(fromId);
        const to = positions.get(toId);
        if (!from || !to) return null;

        const bothAllocated = allocatedIds.has(fromId) && allocatedIds.has(toId);
        const isHighlighted = highlightedEdges?.has(`${fromId}-${toId}`) ||
                              highlightedEdges?.has(`${toId}-${fromId}`);
        const masteryIdx = to.masteryIndex ?? 0;

        let color: string;
        let width: number;
        let opacity: number;

        if (bothAllocated) {
          color = EDGE_ACTIVE[masteryIdx] ?? EDGE_ACTIVE[0];
          width = strokeAllocated;
          opacity = 0.85;
        } else if (isHighlighted) {
          color = EDGE_HIGHLIGHT;
          width = strokeHighlighted;
          opacity = 0.6;
        } else {
          color = EDGE_IDLE[masteryIdx] ?? EDGE_IDLE[0];
          width = strokeIdle;
          opacity = 0.4;
        }

        // Stroke widths are in coord space (no non-scaling-stroke) so
        // lines thicken/thin visually with the tree as the container
        // resizes — matching the node radii which also scale with it.
        return (
          <line
            key={`${fromId}-${toId}`}
            x1={from.sx} y1={from.sy} x2={to.sx} y2={to.sy}
            stroke={color} strokeWidth={width} opacity={opacity}
            strokeLinecap="round"
          />
        );
      })}
    </g>
  );
}

export default memo(PassiveTreeConnectionsInner);
