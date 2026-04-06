/**
 * PassiveTreeNode — renders a single passive node in the SVG tree.
 *
 * The PNG icons include their own dark backgrounds (they're sprite cell crops).
 * We render the PNG AS the node visual, then add a stroke border around it.
 * This matches the Last Epoch visual style where icons include their frame.
 */

import { memo } from "react";
import TreeIcon from "@/components/TreeIcon";
import type { PassiveNode } from "@/services/passiveTreeService";
import { NodeState } from "@/utils/passiveGraph";

export { NodeState };

const PALETTE: Record<number, {
  strokeIdle: string;
  strokeAllocated: string;
  strokeAvailable: string;
}> = {
  0: { strokeIdle: "#3a4070", strokeAllocated: "#8890b8", strokeAvailable: "#5a6090" },
  1: { strokeIdle: "#1a5570", strokeAllocated: "#00d4f5", strokeAvailable: "#0a8aaa" },
  2: { strokeIdle: "#664410", strokeAllocated: "#f0a020", strokeAvailable: "#a07018" },
  3: { strokeIdle: "#4c1880", strokeAllocated: "#b870ff", strokeAvailable: "#7040b0" },
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
  showDebugCenter?: boolean;
}

function PassiveTreeNodeInner({
  node, sx, sy, radius, state, allocatedPoints, onNodeClick, onNodeRightClick, onHover, onLeave, showDebugCenter,
}: Props) {
  const pal = PALETTE[node.mastery_index ?? 0] ?? PALETTE[0];

  const isAllocated = state === NodeState.ALLOCATED;
  const isAvailable = state === NodeState.AVAILABLE;
  const isLocked = state === NodeState.LOCKED;

  const stroke = isAllocated
    ? pal.strokeAllocated
    : isAvailable
      ? pal.strokeAvailable
      : pal.strokeIdle;

  const borderWidth = isAllocated ? 2.5 : 1.5;
  const opacity = isLocked ? 0.35 : 1;
  const cursor = isLocked ? "not-allowed" : "pointer";

  // The icon IS the node — render it at full node size
  const iconSize = radius * 2;

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
        <circle
          r={radius + 5}
          fill={pal.strokeAllocated}
          opacity={0.12}
          pointerEvents="none"
        />
      )}

      {/* Border ring — visible frame around the icon */}
      <circle
        r={radius + borderWidth / 2}
        fill="none"
        stroke={stroke}
        strokeWidth={borderWidth}
      />

      {/* Icon PNG — this IS the node visual (includes dark background + icon art) */}
      <clipPath id={`clip-${node.id}`}>
        <circle r={radius} />
      </clipPath>
      <g clipPath={`url(#clip-${node.id})`}>
        <TreeIcon iconId={node.icon} size={iconSize} nodeName={node.name} />
      </g>

      {/* Debug center marker */}
      {showDebugCenter && (
        <circle r={2} fill="#ff0000" opacity={0.9} pointerEvents="none" />
      )}

      {/* Points label */}
      {node.max_points > 1 && (
        <text
          textAnchor="middle"
          dominantBaseline="hanging"
          y={radius + 4}
          fontSize={Math.max(7, radius * 0.5)}
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
