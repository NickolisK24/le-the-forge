/**
 * PassiveTreeNode — renders a single passive node in the SVG tree.
 *
 * Responsibilities:
 *   - Render a positioned circle/diamond at the node's scaled coordinates
 *   - Display the TreeIcon inside the shape
 *   - Show a tooltip on hover with name, description, stats
 *   - Color by mastery_index (base vs mastery tiers)
 */

import TreeIcon from "@/components/TreeIcon";
import type { PassiveNode } from "@/services/passiveTreeService";

// Mastery palette — index 0 = base, 1/2/3 = masteries
const PALETTE: Record<number, { fill: string; stroke: string; label: string }> = {
  0: { fill: "#181c30", stroke: "#3a4070", label: "Base" },
  1: { fill: "#0a1e26", stroke: "#1a5570", label: "Mastery I" },
  2: { fill: "#221a08", stroke: "#664410", label: "Mastery II" },
  3: { fill: "#180d2a", stroke: "#4c1880", label: "Mastery III" },
};

interface Props {
  node: PassiveNode;
  sx: number;  // screen X (already scaled)
  sy: number;  // screen Y (already scaled)
  radius: number;
  onHover: (node: PassiveNode, screenX: number, screenY: number) => void;
  onLeave: () => void;
}

export default function PassiveTreeNode({ node, sx, sy, radius, onHover, onLeave }: Props) {
  const pal = PALETTE[node.mastery_index ?? 0] ?? PALETTE[0];
  const isNotable = node.node_type === "notable" || node.max_points === 1;

  return (
    <g
      transform={`translate(${sx},${sy})`}
      onMouseEnter={(e) => onHover(node, e.clientX, e.clientY)}
      onMouseMove={(e) => onHover(node, e.clientX, e.clientY)}
      onMouseLeave={onLeave}
      style={{ cursor: "default" }}
    >
      {/* Node shape */}
      {isNotable ? (
        <rect
          x={-radius}
          y={-radius}
          width={radius * 2}
          height={radius * 2}
          rx={3}
          transform="rotate(45)"
          fill={pal.fill}
          stroke={pal.stroke}
          strokeWidth={1}
        />
      ) : (
        <circle
          r={radius}
          fill={pal.fill}
          stroke={pal.stroke}
          strokeWidth={1}
        />
      )}

      {/* Icon */}
      <TreeIcon iconId={node.icon} size={radius * 1.5} nodeName={node.name} />

      {/* Points label for multi-point nodes */}
      {node.max_points > 1 && (
        <text
          textAnchor="middle"
          dominantBaseline="hanging"
          y={radius + 3}
          fontSize={8}
          fill={pal.stroke}
          fontFamily="monospace"
          fontWeight="bold"
          pointerEvents="none"
          opacity={0.7}
        >
          0/{node.max_points}
        </text>
      )}
    </g>
  );
}
