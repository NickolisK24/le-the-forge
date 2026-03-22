import { useState, useMemo } from "react";
import { clsx } from "clsx";
import type { PassiveNode } from "@/lib/gameData";
import { PASSIVE_TREES } from "@/data/passiveTrees";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const CANVAS_W = 620;
const CANVAS_H = 900;

const NODE_R: Record<string, number> = {
  core: 13,
  notable: 19,
  keystone: 26,
  "mastery-gate": 16,
};

const COLORS = {
  core:          { idle: "#2a2218", active: "#c8902a", border: "#5a4a28" },
  notable:       { idle: "#1e2230", active: "#5c8fd6", border: "#3a5a90" },
  keystone:      { idle: "#1a2a1a", active: "#2e7d32", border: "#3a6a3a" },
  "mastery-gate":{ idle: "#2a1a1a", active: "#9b3030", border: "#6a2a2a" },
} as const;

// Region display names
const REGION_LABELS: Record<string, string> = {
  base: "Base",
  necromancer: "Necromancer",
  lich: "Lich",
  warlock: "Warlock",
  runemaster: "Runemaster",
  sorcerer: "Sorcerer",
  spellblade: "Spellblade",
  beastmaster: "Beastmaster",
  druid: "Druid",
  shaman: "Shaman",
  "forge-guard": "Forge Guard",
  paladin: "Paladin",
  "void-knight": "Void Knight",
  bladedancer: "Bladedancer",
  marksman: "Marksman",
  falconer: "Falconer",
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type AllocMap = Record<number, number>;

interface Props {
  characterClass: string;
  mastery: string;
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
}

// ---------------------------------------------------------------------------
// PassiveTreeGraph
// ---------------------------------------------------------------------------
export default function PassiveTreeGraph({
  characterClass,
  mastery,
  allocated,
  onAllocate,
  readOnly = false,
}: Props) {
  const regionMap = PASSIVE_TREES[characterClass] ?? {};
  const regionKeys = Object.keys(regionMap);

  // Default to the mastery region if it matches, otherwise base
  const masteryKey = mastery.toLowerCase().replace(/\s+/g, "-");
  const defaultRegion = regionKeys.includes(masteryKey) ? masteryKey : "base";
  const [activeRegion, setActiveRegion] = useState(defaultRegion);

  const nodes: PassiveNode[] = useMemo(
    () => regionMap[activeRegion] ?? [],
    [regionMap, activeRegion]
  );

  const [hovered, setHovered] = useState<number | null>(null);

  const byId = useMemo(
    () => Object.fromEntries(nodes.map((n) => [n.id, n])),
    [nodes]
  );

  function isUnlocked(nodeId: number): boolean {
    const node = byId[nodeId];
    if (!node || node.parentId == null) return true;
    const parent = byId[node.parentId];
    if (!parent) return true;
    return (allocated[parent.id] ?? 0) >= 1 && isUnlocked(parent.id);
  }

  function handleClick(node: PassiveNode) {
    if (readOnly) return;
    if (!isUnlocked(node.id)) return;
    const max = node.maxPoints ?? 1;
    const current = allocated[node.id] ?? 0;
    if (current >= max) {
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

  // Scale to fit a 560px wide view
  const viewW = 560;
  const viewH = Math.round(viewW * (CANVAS_H / CANVAS_W));
  const scale = viewW / CANVAS_W;
  function cx(x: number) { return x * scale; }
  function cy(y: number) { return y * scale; }

  // Total points allocated across all regions
  const totalPoints = Object.values(allocated).reduce((s, v) => s + v, 0);
  const regionPoints = nodes.reduce((s, n) => s + (allocated[n.id] ?? 0), 0);

  return (
    <div className="flex flex-col gap-0 rounded border border-forge-border bg-forge-surface overflow-hidden">
      {/* Region tabs */}
      <div className="flex items-center gap-0 border-b border-forge-border bg-forge-surface2 overflow-x-auto shrink-0">
        {regionKeys.map((key) => {
          const regionNodes = regionMap[key] ?? [];
          const pts = regionNodes.reduce((s, n) => s + (allocated[n.id] ?? 0), 0);
          return (
            <button
              key={key}
              onClick={() => setActiveRegion(key)}
              className={clsx(
                "px-3 py-2 font-mono text-[10px] uppercase tracking-widest whitespace-nowrap border-r border-forge-border transition-colors",
                activeRegion === key
                  ? "bg-forge-surface text-forge-amber border-b-2 border-b-forge-amber -mb-px"
                  : "text-forge-dim hover:text-forge-text"
              )}
            >
              {REGION_LABELS[key] ?? key}
              {pts > 0 && (
                <span className="ml-1.5 text-forge-amber">{pts}</span>
              )}
            </button>
          );
        })}
        <span className="ml-auto px-3 font-mono text-[10px] text-forge-dim whitespace-nowrap">
          {totalPoints} pts total
        </span>
      </div>

      {/* Tree SVG */}
      <div className="overflow-auto bg-forge-bg">
        <svg
          width={viewW}
          height={viewH}
          viewBox={`0 0 ${viewW} ${viewH}`}
          style={{ display: "block" }}
        >
          {/* Edges */}
          {nodes.map((node) => {
            if (node.parentId == null) return null;
            const parent = byId[node.parentId];
            if (!parent) return null;
            const active =
              (allocated[node.id] ?? 0) >= 1 &&
              (allocated[parent.id] ?? 0) >= 1;
            return (
              <line
                key={`e-${node.id}`}
                x1={cx(parent.x)} y1={cy(parent.y)}
                x2={cx(node.x)}  y2={cy(node.y)}
                stroke={active ? "#c8902a" : "#2a2218"}
                strokeWidth={active ? 2 : 1.5}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const type = node.type ?? "core";
            const r = (NODE_R[type] ?? 13) * scale;
            const max = node.maxPoints ?? 1;
            const pts = allocated[node.id] ?? 0;
            const active = pts >= 1;
            const unlocked = isUnlocked(node.id);
            const colors = COLORS[type as keyof typeof COLORS] ?? COLORS.core;
            const fill = active ? colors.active : colors.idle;
            const stroke = active ? "#e8b040" : colors.border;
            const isHov = hovered === node.id;

            return (
              <g
                key={node.id}
                transform={`translate(${cx(node.x)},${cy(node.y)})`}
                style={{ cursor: readOnly || !unlocked ? "default" : "pointer" }}
                onClick={() => handleClick(node)}
                onMouseEnter={() => setHovered(node.id)}
                onMouseLeave={() => setHovered(null)}
              >
                {/* Keystone diamond outline */}
                {type === "keystone" && (
                  <polygon
                    points={`0,${-(r + 5)} ${r + 5},0 0,${r + 5} ${-(r + 5)},0`}
                    fill="none"
                    stroke={active ? "#e8b040" : "#3a5a3a"}
                    strokeWidth={1}
                    opacity={unlocked ? 1 : 0.3}
                  />
                )}

                <circle
                  r={r + (isHov ? 2 : 0)}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={type === "keystone" ? 2.5 : 1.5}
                  opacity={unlocked || active ? 1 : 0.35}
                />

                {/* Multi-point counter */}
                {max > 1 && (
                  <text
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize={r * 0.75}
                    fill={active ? "#1a1208" : "#888"}
                    fontFamily="monospace"
                    fontWeight="bold"
                  >
                    {pts}/{max}
                  </text>
                )}

                {/* Node name label */}
                {node.name && (
                  <text
                    y={r + 11 * scale}
                    textAnchor="middle"
                    fontSize={9 * scale}
                    fill={active ? "#e8b040" : "#666"}
                    fontFamily="monospace"
                  >
                    {node.name}
                  </text>
                )}

                {/* Hover tooltip */}
                {isHov && node.name && (
                  <g>
                    <rect
                      x={-55 * scale}
                      y={-r - 30 * scale}
                      width={110 * scale}
                      height={20 * scale}
                      rx={3 * scale}
                      fill="#1a1208"
                      stroke="#c8902a"
                      strokeWidth={0.8}
                    />
                    <text
                      y={-r - 20 * scale}
                      textAnchor="middle"
                      fontSize={8 * scale}
                      fill="#e8b040"
                      fontFamily="monospace"
                    >
                      {node.name}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Footer: legend + hint */}
      <div className="flex items-center gap-4 border-t border-forge-border px-3 py-1.5 text-[10px] font-mono text-forge-dim bg-forge-surface2 shrink-0">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#2a2218] border border-[#5a4a28]" />
          Core
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#1e2230] border border-[#3a5a90]" />
          Notable
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#1a2a1a] border border-[#3a6a3a]" />
          Keystone
        </span>
        {regionPoints > 0 && (
          <span className="ml-2 text-forge-amber">{regionPoints} in this region</span>
        )}
        {!readOnly && (
          <span className="ml-auto">Click to invest · click again to refund</span>
        )}
      </div>
    </div>
  );
}
