/**
 * PassiveTreeConnections — draws SVG lines between connected passive nodes.
 *
 * Receives a pre-computed list of edges (fromId → toId) and a position lookup.
 * Renders each connection as a simple line with mastery-appropriate coloring.
 */

interface Position {
  sx: number;
  sy: number;
  masteryIndex: number;
}

// Mastery edge colors
const EDGE_COLORS: Record<number, string> = {
  0: "#252940",
  1: "#152232",
  2: "#2e2010",
  3: "#200e32",
};

interface Edge {
  fromId: string;
  toId: string;
}

interface Props {
  edges: Edge[];
  positions: Map<string, Position>;
}

export default function PassiveTreeConnections({ edges, positions }: Props) {
  return (
    <g>
      {edges.map(({ fromId, toId }) => {
        const from = positions.get(fromId);
        const to = positions.get(toId);
        if (!from || !to) return null;
        const color = EDGE_COLORS[to.masteryIndex ?? 0] ?? EDGE_COLORS[0];
        return (
          <line
            key={`${fromId}-${toId}`}
            x1={from.sx}
            y1={from.sy}
            x2={to.sx}
            y2={to.sy}
            stroke={color}
            strokeWidth={1}
            opacity={0.5}
          />
        );
      })}
    </g>
  );
}
