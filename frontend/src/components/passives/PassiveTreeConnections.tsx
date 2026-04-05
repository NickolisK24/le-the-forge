/**
 * PassiveTreeConnections — draws SVG lines between connected passive nodes.
 *
 * Supports edge highlighting: connections where both endpoints are allocated
 * render brighter and thicker than idle connections.
 */

import { memo } from "react";

interface Position {
  sx: number;
  sy: number;
  masteryIndex: number;
}

// Mastery edge colors — idle vs active (both endpoints allocated)
const EDGE_IDLE: Record<number, string> = {
  0: "#252940",
  1: "#152232",
  2: "#2e2010",
  3: "#200e32",
};

const EDGE_ACTIVE: Record<number, string> = {
  0: "#6670a0",
  1: "#00a8c0",
  2: "#c08018",
  3: "#9050d8",
};

interface Edge {
  fromId: string;
  toId: string;
}

interface Props {
  edges: Edge[];
  positions: Map<string, Position>;
  allocatedIds: Set<string>;
}

function PassiveTreeConnectionsInner({ edges, positions, allocatedIds }: Props) {
  return (
    <g>
      {edges.map(({ fromId, toId }) => {
        const from = positions.get(fromId);
        const to = positions.get(toId);
        if (!from || !to) return null;

        const bothAllocated = allocatedIds.has(fromId) && allocatedIds.has(toId);
        const masteryIdx = to.masteryIndex ?? 0;
        const color = bothAllocated
          ? (EDGE_ACTIVE[masteryIdx] ?? EDGE_ACTIVE[0])
          : (EDGE_IDLE[masteryIdx] ?? EDGE_IDLE[0]);

        return (
          <line
            key={`${fromId}-${toId}`}
            x1={from.sx}
            y1={from.sy}
            x2={to.sx}
            y2={to.sy}
            stroke={color}
            strokeWidth={bothAllocated ? 2 : 1}
            opacity={bothAllocated ? 0.85 : 0.4}
          />
        );
      })}
    </g>
  );
}

export default memo(PassiveTreeConnectionsInner);
