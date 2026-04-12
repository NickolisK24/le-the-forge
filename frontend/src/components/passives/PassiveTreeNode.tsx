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

import { memo, useState } from "react";
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
  /** Whether this node is part of the currently highlighted path */
  highlighted?: boolean;
  /** Whether this node is a dependency blocker (shown with red outline) */
  blocked?: boolean;
}

function PassiveTreeNodeInner({
  node, sx, sy, radius, state, allocatedPoints, onNodeClick, onNodeRightClick, onHover, onLeave, highlighted, blocked,
}: Props) {
  const pal = PALETTE[node.mastery_index ?? 0] ?? PALETTE[0];
  const isNotable = node.node_type === "notable" || node.max_points === 1;

  const isAllocated = state === NodeState.ALLOCATED;
  const isAvailable = state === NodeState.AVAILABLE;
  const isLocked = state === NodeState.LOCKED;
  const isMasteryLocked = state === NodeState.MASTERY_LOCKED;
  const isAnyLocked = isLocked || isMasteryLocked;

  // ALLOCATED vs AVAILABLE vs LOCKED distinction:
  //   ALLOCATED     — bright class color fill + glow halo, thick border
  //   AVAILABLE     — dark fill, colored border, full opacity
  //   LOCKED        — very dark fill, dim border, 40% opacity
  //   MASTERY_LOCKED — locked styling + lock icon overlay
  const stroke = isAllocated
    ? pal.strokeAllocated
    : isAvailable
      ? pal.strokeAvailable
      : pal.strokeIdle;

  const fill = isAllocated ? pal.strokeAllocated : pal.fill;

  // Strokes and labels scale with the node radius so they stay visually
  // proportional at any on-screen size (our canvas guarantees the screen
  // radius is ≥ MIN_SCREEN_NODE_R by inflating the coord-space radius).
  const strokeWidth = isAllocated
    ? radius * 0.2
    : highlighted
      ? radius * 0.15
      : radius * 0.1;
  const opacity = isMasteryLocked ? 0.4 : isLocked ? (highlighted ? 0.6 : 0.4) : 1;
  const cursor = isAnyLocked ? "not-allowed" : "pointer";

  // Icon sits inside the node shape. User-facing target is 1.6× diameter
  // of the base radius (so the art fills more of the node).
  const iconSize = radius * 1.6;
  // Points label scales with the node so it stays legible. Ratio 0.55
  // matches ~10 unit font at the 18-unit base radius.
  const labelFontSize = radius * 0.55;
  const labelGap = radius * 0.2;

  // Hover scale — applied via CSS transform so the browser animates
  // smoothly. Outer <g> handles the SVG translate (viewBox coords);
  // inner <g> handles the scale so we do not fight the attribute.
  const [hovered, setHovered] = useState(false);

  return (
    <g transform={`translate(${sx},${sy})`}>
      <g
        onClick={(e) => onNodeClick(node.id, e.shiftKey)}
        onContextMenu={(e) => { e.preventDefault(); onNodeRightClick(node.id, e.shiftKey); }}
        onMouseEnter={(e) => { setHovered(true); onHover(node, e.clientX, e.clientY); }}
        onMouseMove={(e) => onHover(node, e.clientX, e.clientY)}
        onMouseLeave={() => { setHovered(false); onLeave(); }}
        style={{
          cursor,
          opacity,
          transform: hovered && !isAnyLocked ? "scale(1.2)" : "scale(1)",
          transition: "transform 150ms ease-out",
          transformBox: "fill-box",
          transformOrigin: "center",
        }}
      >
        {/* Glow halo when allocated — bright bloom that signals the
            node is active. Grows proportionally with radius. */}
        {isAllocated && (
          isNotable ? (
            <rect
              x={-(radius + radius * 0.35)}
              y={-(radius + radius * 0.35)}
              width={(radius + radius * 0.35) * 2}
              height={(radius + radius * 0.35) * 2}
              rx={radius * 0.25}
              transform="rotate(45)"
              fill={pal.strokeAllocated}
              opacity={0.22}
              pointerEvents="none"
            />
          ) : (
            <circle
              r={radius * 1.45}
              fill={pal.strokeAllocated}
              opacity={0.22}
              pointerEvents="none"
            />
          )
        )}

        {/* Path highlight ring (when node is on the hover path) */}
        {highlighted && !isAllocated && (
          <circle
            r={radius + radius * 0.2}
            fill="none"
            stroke="#f0a020"
            strokeWidth={radius * 0.08}
            opacity={0.55}
            pointerEvents="none"
          />
        )}

        {/* Blocking indicator (red outline when this node is a dependency blocker) */}
        {blocked && (
          <circle
            r={radius + radius * 0.3}
            fill="none"
            stroke="#ef4444"
            strokeWidth={radius * 0.12}
            opacity={0.75}
            pointerEvents="none"
          />
        )}

        {/* Node shape — filled with class color when allocated (so the
            node reads as "active" at a glance), dark with colored border
            otherwise. */}
        {isNotable ? (
          <rect
            x={-radius}
            y={-radius}
            width={radius * 2}
            height={radius * 2}
            rx={radius * 0.2}
            transform="rotate(45)"
            fill={fill}
            stroke={stroke}
            strokeWidth={strokeWidth}
          />
        ) : (
          <circle
            r={radius}
            fill={fill}
            stroke={stroke}
            strokeWidth={strokeWidth}
          />
        )}

        {/* Icon — sized to 1.6× the base radius so the art fills the
            node while still leaving a visible rim. */}
        <TreeIcon iconId={node.icon} size={iconSize} nodeName={node.name} />

        {/* Points label — scales with the node so "X/Y" stays legible. */}
        {node.max_points > 1 && (
          <text
            textAnchor="middle"
            dominantBaseline="hanging"
            y={radius + labelGap}
            fontSize={labelFontSize}
            fill={isAllocated ? pal.strokeAllocated : stroke}
            fontFamily="monospace"
            fontWeight="bold"
            pointerEvents="none"
            opacity={0.9}
          >
            {allocatedPoints}/{node.max_points}
          </text>
        )}

        {/* Lock icon for mastery-locked nodes — scales with radius so
            the glyph stays visible at any zoom level. */}
        {isMasteryLocked && (
          <g pointerEvents="none" opacity={0.95}>
            <rect
              x={-radius * 0.35}
              y={-radius * 0.15}
              width={radius * 0.7}
              height={radius * 0.55}
              rx={radius * 0.08}
              fill="#ef4444"
              opacity={0.85}
            />
            <path
              d={`M${-radius * 0.22},${-radius * 0.15} L${-radius * 0.22},${-radius * 0.35} A${radius * 0.22},${radius * 0.22} 0 0,1 ${radius * 0.22},${-radius * 0.35} L${radius * 0.22},${-radius * 0.15}`}
              fill="none"
              stroke="#ef4444"
              strokeWidth={radius * 0.12}
              opacity={0.85}
            />
          </g>
        )}
      </g>
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
    prev.allocatedPoints === next.allocatedPoints &&
    prev.highlighted === next.highlighted &&
    prev.blocked === next.blocked
  );
});
