import { useState } from "react";
import type { SkillNode } from "@/data/skillTrees";
import { cleanNodeName } from "@/data/skillTrees";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PADDING = 48; // px of breathing room around node bounds

const NODE_R: Record<SkillNode["type"], number> = {
  core: 14,
  notable: 20,
  keystone: 28,
  "mastery-gate": 22,  // skill entry node
};

const COLORS: Record<SkillNode["type"], { idle: string; active: string; border: string }> = {
  core:           { idle: "#3a3020", active: "#c8902a", border: "#5a4a28" },
  notable:        { idle: "#2a2a3a", active: "#7b5ea7", border: "#4a3a7a" },
  keystone:       { idle: "#1a2a1a", active: "#2e7d32", border: "#3a6a3a" },
  "mastery-gate": { idle: "#3a1a08", active: "#d06020", border: "#8a4010" },
} as const;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface AllocMap {
  [nodeId: number]: number; // points invested
}

interface Props {
  nodes: SkillNode[];
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
}

// ---------------------------------------------------------------------------
// SkillTreeGraph
// ---------------------------------------------------------------------------
export default function SkillTreeGraph({ nodes, allocated, onAllocate, readOnly }: Props) {
  const [hovered, setHovered] = useState<number | null>(null);

  // Build a map for quick lookup
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));

  // Compute node bounds so the viewBox always contains all nodes
  const maxR = Math.max(...Object.values(NODE_R));
  const minX = nodes.length ? Math.min(...nodes.map((n) => n.x)) - maxR - PADDING : 0;
  const minY = nodes.length ? Math.min(...nodes.map((n) => n.y)) - maxR - PADDING : 0;
  const maxX = nodes.length ? Math.max(...nodes.map((n) => n.x)) + maxR + PADDING : 100;
  const maxY = nodes.length ? Math.max(...nodes.map((n) => n.y)) + maxR + PADDING : 100;
  const rawW = maxX - minX;
  const rawH = maxY - minY;

  // Translate node coords so (minX, minY) maps to (0, 0) in SVG space
  function cx(x: number) { return x - minX; }
  function cy(y: number) { return y - minY; }

  // Check if a node's parent chain is allocated (all ancestors have ≥1 point)
  function isUnlocked(nodeId: number): boolean {
    const node = byId[nodeId];
    if (!node || node.parentId == null) return true; // root always unlocked
    const parent = byId[node.parentId];
    if (!parent) return true;
    return (allocated[parent.id] ?? 0) >= 1 && isUnlocked(parent.id);
  }

  function handleClick(node: SkillNode) {
    if (readOnly) return;
    if (!isUnlocked(node.id)) return;
    const current = allocated[node.id] ?? 0;
    if (current >= node.maxPoints) {
      const hasAllocatedChild = nodes.some(
        (n) => n.parentId === node.id && (allocated[n.id] ?? 0) > 0
      );
      if (!hasAllocatedChild) {
        onAllocate(node.id, current - 1);
      }
    } else {
      onAllocate(node.id, current + 1);
    }
  }

  return (
    <div className="relative overflow-hidden rounded-sm border border-forge-border bg-forge-bg">
      <svg
        width="100%"
        viewBox={`0 0 ${rawW} ${rawH}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ display: "block", touchAction: "none" }}
      >
        {/* Edges */}
        {nodes.map((node) => {
          if (node.parentId == null) return null;
          const parent = byId[node.parentId];
          if (!parent) return null;
          const active = (allocated[node.id] ?? 0) >= 1 && (allocated[parent.id] ?? 0) >= 1;
          return (
            <line
              key={`edge-${node.id}`}
              x1={cx(parent.x)}
              y1={cy(parent.y)}
              x2={cx(node.x)}
              y2={cy(node.y)}
              stroke={active ? "#c8902a" : "#2a2218"}
              strokeWidth={active ? 2 : 1.5}
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const r = NODE_R[node.type];
          const pts = allocated[node.id] ?? 0;
          const active = pts >= 1;
          const unlocked = isUnlocked(node.id);
          const colors = COLORS[node.type];
          const fill = active ? colors.active : colors.idle;
          const stroke = active ? "#e8b040" : colors.border;
          const isHov = hovered === node.id;

          return (
            <g
              key={node.id}
              transform={`translate(${cx(node.x)}, ${cy(node.y)})`}
              style={{ cursor: readOnly || !unlocked ? "default" : "pointer" }}
              onClick={() => handleClick(node)}
              onMouseEnter={() => setHovered(node.id)}
              onMouseLeave={() => setHovered(null)}
            >
              <circle
                r={r + (isHov ? 2 : 0)}
                fill={fill}
                stroke={stroke}
                strokeWidth={node.type === "keystone" ? 2.5 : 1.5}
                opacity={unlocked || active ? 1 : 0.4}
              />
              {/* Outer ring for mastery-gate (skill entry node) */}
              {node.type === "mastery-gate" && (
                <circle
                  r={r + 5}
                  fill="none"
                  stroke={active ? "#e8b040" : "#8a4010"}
                  strokeWidth={1.5}
                  strokeDasharray={active ? "none" : "4 2"}
                  opacity={0.8}
                />
              )}
              {/* Diamond shape for keystones */}
              {node.type === "keystone" && (
                <polygon
                  points={`0,${-r - 4} ${r + 4},0 0,${r + 4} ${-r - 4},0`}
                  fill="none"
                  stroke={active ? "#e8b040" : "#3a5a3a"}
                  strokeWidth={1}
                  opacity={unlocked ? 1 : 0.3}
                />
              )}
              {/* Point counter */}
              {(node.maxPoints ?? 1) > 1 && (
                <text
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={r * 0.85}
                  fill={active ? "#1a1208" : "#888"}
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {pts}/{node.maxPoints}
                </text>
              )}
              {/* Play icon on inactive entry node */}
              {node.type === "mastery-gate" && !active && (
                <text
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={r * 0.7}
                  fill="#d06020"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  ▶
                </text>
              )}
              {/* Labels for named non-entry nodes */}
              {node.name && node.type !== "mastery-gate" && (
                <text
                  y={r + 14}
                  textAnchor="middle"
                  fontSize={10}
                  fill={active ? "#e8b040" : "#888"}
                  fontFamily="monospace"
                >
                  {cleanNodeName(node.name)}
                </text>
              )}
              {/* Hover tooltip */}
              {isHov && (
                <g>
                  <rect
                    x={-55}
                    y={-r - 32}
                    width={110}
                    height={20}
                    rx={3}
                    fill="#1a1208"
                    stroke="#c8902a"
                    strokeWidth={0.8}
                  />
                  <text
                    y={-r - 22}
                    textAnchor="middle"
                    fontSize={9}
                    fill="#e8b040"
                    fontFamily="monospace"
                  >
                    {node.type === "mastery-gate"
                      ? "Skill Entry — allocate first"
                      : cleanNodeName(node.name)}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex items-center gap-4 border-t border-forge-border px-3 py-1.5 text-[10px] font-mono text-forge-dim">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#3a1a08] border border-[#8a4010]" />
          Entry
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#3a3020] border border-[#5a4a28]" />
          Core
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#2a2a3a] border border-[#4a3a7a]" />
          Notable
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#1a2a1a] border border-[#3a6a3a]" />
          Keystone
        </span>
        {!readOnly && (
          <span className="ml-auto">Click to allocate · Click again to refund</span>
        )}
      </div>
    </div>
  );
}
