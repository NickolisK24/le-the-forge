/**
 * PassiveTreeNode — renders a single passive node in the SVG tree.
 *
 * Visual states via NodeState enum:
 *   ALLOCATED  — bright highlight + glow halo
 *   AVAILABLE  — normal appearance, pointer cursor
 *   LOCKED     — dimmed (0.35 opacity), not-allowed cursor
 *
 * Click events forward shiftKey for max-allocate / full-remove.
 * Wrapped in React.memo with custom comparator for performance.
 */

import { memo } from "react";
import TreeIcon from "@/components/TreeIcon";
import type { PassiveNode } from "@/services/passiveTreeService";
import { NodeState } from "@/utils/passiveGraph";

// Re-export for consumers that import from this file
export { NodeState };

// Mastery palette — index 0 = base, 1/2/3 = masteries
const PALETTE: Record<number, {
  fill: string;
  strokeIdle: string;
  strokeAllocated: string;
  strokeAvailable: string;
}> = {
  0: { fill: "#181c30", strokeIdle: "#3a4070", strokeAllocated: "#8890b8", strokeAvailable: "#5a6090" },
  1: { fill: "#0a1e26", strokeIdle: "#1a5570", strokeAllocated: "#00d4f5", strokeAvailable: "#0a8aaa" },
  2: { fill: "#221a08", strokeIdle: "#664410", strokeAllocated: "#f0a020", strokeAvailable: "#a07018" },
  3: { fill: "#180d2a", strokeIdle: "#4c1880", strokeAllocated: "#b870ff", strokeAvailable: "#7040b0" },
};

interface Props {
  node: PassiveNode;
  sx: number;
  sy: number;
  radius: number;
  state: NodeState;
  allocatedPoints: number;
  onNodeClick: (nodeId: string, shiftKey: boolean) => void;
  onNodeRightClick: (nodeId: string, shiftKey: boolean) => void;
  onHover: (node: PassiveNode, screenX: number, screenY: number) => void;
  onLeave: () => void;
  /** Dev-only: render a red dot at the exact node center coordinate */
  showDebugCenter?: boolean;
}

function PassiveTreeNodeInner({
  node, sx, sy, radius, state, allocatedPoints, onNodeClick, onNodeRightClick, onHover, onLeave, showDebugCenter,
}: Props) {
  const pal = PALETTE[node.mastery_index ?? 0] ?? PALETTE[0];
  const isNotable = node.node_type === "notable" || node.max_points === 1;

  const isAllocated = state === NodeState.ALLOCATED;
  const isAvailable = state === NodeState.AVAILABLE;
  const isLocked = state === NodeState.LOCKED;

  const stroke = isAllocated
    ? pal.strokeAllocated
    : isAvailable
      ? pal.strokeAvailable
      : pal.strokeIdle;

  const strokeWidth = isAllocated ? 2 : 1;
  const opacity = isLocked ? 0.35 : 1;
  const cursor = isLocked ? "not-allowed" : "pointer";

  return (
    <g
      transform={`translate(${sx},${sy})`}
      onClick={(e) => onNodeClick(node.id, e.shiftKey)}
      onContextMenu={(e) => { e.preventDefault(); onNodeRightClick(node.id, e.shiftKey); }}
      onMouseEnter={(e) => onHover(node, e.clientX, e.clientY)}
      onMouseMove={(e) => onHover(node, e.clientX, e.clientY)}
      onMouseLeave={onLeave}
      style={{ cursor }}
      opacity={opacity}
    >
      {/* Glow halo when allocated */}
      {isAllocated && (
        isNotable ? (
          <rect
            x={-(radius + 4)}
            y={-(radius + 4)}
            width={(radius + 4) * 2}
            height={(radius + 4) * 2}
            rx={3}
            transform="rotate(45)"
            fill={pal.strokeAllocated}
            opacity={0.15}
            pointerEvents="none"
          />
        ) : (
          <circle
            r={radius + 4}
            fill={pal.strokeAllocated}
            opacity={0.15}
            pointerEvents="none"
          />
        )
      )}

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
          stroke={stroke}
          strokeWidth={strokeWidth}
        />
      ) : (
        <circle
          r={radius}
          fill={pal.fill}
          stroke={stroke}
          strokeWidth={strokeWidth}
        />
      )}

      {/* Icon */}
      <TreeIcon iconId={node.icon} size={radius * 1.5} nodeName={node.name} />

      {/* Debug center marker — red dot at exact (0,0) of this node's coordinate */}
      {showDebugCenter && (
        <circle r={2} fill="#ff0000" opacity={0.9} pointerEvents="none" />
      )}

      {/* Points label */}
      {node.max_points > 1 && (
        <text
          textAnchor="middle"
          dominantBaseline="hanging"
          y={radius + 3}
          fontSize={8}
          fill={isAllocated ? pal.strokeAllocated : stroke}
          fontFamily="monospace"
          fontWeight="bold"
          pointerEvents="none"
          opacity={0.85}
        >
          {allocatedPoints}/{node.max_points}
        </text>
      )}
    </g>
  );
}

export default memo(PassiveTreeNodeInner, (prev, next) => {
  return (
    prev.node.id === next.node.id &&
    prev.sx === next.sx &&
    prev.sy === next.sy &&
    prev.radius === next.radius &&
    prev.state === next.state &&
    prev.allocatedPoints === next.allocatedPoints
  );
});
