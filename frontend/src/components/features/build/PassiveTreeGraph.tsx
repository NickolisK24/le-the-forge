import { useState, useMemo, useRef } from "react";
import { clsx } from "clsx";
import type { PassiveNode } from "@/lib/gameData";
import { PASSIVE_TREES } from "@/data/passiveTrees";

// ---------------------------------------------------------------------------
// Constants — match the layout used in the data generator
// ---------------------------------------------------------------------------
const CANVAS_W = 1200;
const CANVAS_H = 900;

const NODE_R: Record<string, number> = {
  core: 12,
  notable: 18,
  keystone: 26,
  "mastery-gate": 15,
};

const COLORS = {
  core:          { idle: "#28201a", active: "#c8902a", border: "#5a4a28" },
  notable:       { idle: "#1c2030", active: "#5c8fd6", border: "#3a5a90" },
  keystone:      { idle: "#18281a", active: "#2e8032", border: "#3a6a3a" },
  "mastery-gate":{ idle: "#2a1818", active: "#9b3030", border: "#6a2a2a" },
} as const;

const REGION_LABELS: Record<string, string> = {
  base:         "Base",
  necromancer:  "Necromancer",
  lich:         "Lich",
  warlock:      "Warlock",
  runemaster:   "Runemaster",
  sorcerer:     "Sorcerer",
  spellblade:   "Spellblade",
  beastmaster:  "Beastmaster",
  druid:        "Druid",
  shaman:       "Shaman",
  "forge-guard":"Forge Guard",
  paladin:      "Paladin",
  "void-knight":"Void Knight",
  bladedancer:  "Bladedancer",
  marksman:     "Marksman",
  falconer:     "Falconer",
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

interface TooltipState {
  node: PassiveNode;
  svgX: number;
  svgY: number;
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

  // Default to mastery region if it exists, otherwise base
  const masteryKey = mastery.toLowerCase().replace(/\s+/g, "-");
  const defaultRegion = regionKeys.includes(masteryKey) ? masteryKey : (regionKeys[0] ?? "base");
  const [activeRegion, setActiveRegion] = useState(defaultRegion);

  const nodes: PassiveNode[] = useMemo(
    () => regionMap[activeRegion] ?? [],
    [regionMap, activeRegion]
  );

  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

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
      const hasChild = nodes.some(
        (n) => n.parentId === node.id && (allocated[n.id] ?? 0) > 0
      );
      if (!hasChild) onAllocate(node.id, current - 1);
    } else {
      onAllocate(node.id, current + 1);
    }
  }

  // Scale so CANVAS_W fits in 100% width (container handles overflow-x)
  // We render the SVG at full canvas scale so nodes look sharp
  const DISPLAY_H = 520; // fixed display height in pixels
  const scale = DISPLAY_H / CANVAS_H;
  const displayW = CANVAS_W * scale;

  function sx(x: number) { return x * scale; }
  function sy(y: number) { return y * scale; }

  const totalPoints = Object.values(allocated).reduce((s, v) => s + v, 0);
  const regionPoints = nodes.reduce((s, n) => s + (allocated[n.id] ?? 0), 0);

  return (
    <div className="flex flex-col gap-0 rounded border border-forge-border bg-forge-surface overflow-hidden">

      {/* Region tabs */}
      <div className="flex items-stretch border-b border-forge-border bg-forge-surface2 overflow-x-auto shrink-0">
        {regionKeys.map((key) => {
          const pts = (regionMap[key] ?? []).reduce(
            (s: number, n: PassiveNode) => s + (allocated[n.id] ?? 0), 0
          );
          return (
            <button
              key={key}
              onClick={() => setActiveRegion(key)}
              className={clsx(
                "px-4 py-2 font-mono text-[10px] uppercase tracking-widest whitespace-nowrap border-r border-forge-border transition-colors shrink-0",
                activeRegion === key
                  ? "bg-forge-bg text-forge-amber border-b-0 border-b-2 border-b-forge-amber"
                  : "text-forge-dim hover:text-forge-text"
              )}
            >
              {REGION_LABELS[key] ?? key}
              {pts > 0 && <span className="ml-1.5 text-forge-amber opacity-80">{pts}</span>}
            </button>
          );
        })}
        <div className="ml-auto flex items-center px-3 font-mono text-[10px] text-forge-dim whitespace-nowrap">
          {totalPoints > 0 && <span className="text-forge-amber mr-2">{totalPoints} pts total</span>}
          {nodes.length} nodes
        </div>
      </div>

      {/* SVG canvas — scrollable horizontally */}
      <div className="relative overflow-auto bg-forge-bg" style={{ height: DISPLAY_H }}>
        <svg
          ref={svgRef}
          width={displayW}
          height={DISPLAY_H}
          viewBox={`0 0 ${displayW} ${DISPLAY_H}`}
          style={{ display: "block" }}
        >
          {/* Background grid lines (subtle) */}
          {Array.from({ length: 8 }, (_, i) => (
            <line
              key={`hg-${i}`}
              x1={0} y1={sy(100 + i * 100)}
              x2={displayW} y2={sy(100 + i * 100)}
              stroke="#1a1610" strokeWidth={0.5}
            />
          ))}

          {/* Edges */}
          {nodes.map((node) => {
            if (node.parentId == null) return null;
            const parent = byId[node.parentId];
            if (!parent) return null;
            const active =
              (allocated[node.id] ?? 0) >= 1 &&
              (allocated[parent.id] ?? 0) >= 1;
            const unlocked = isUnlocked(node.id);
            return (
              <line
                key={`e-${node.id}`}
                x1={sx(parent.x)} y1={sy(parent.y)}
                x2={sx(node.x)}  y2={sy(node.y)}
                stroke={active ? "#c8902a" : unlocked ? "#3a3020" : "#1e1c18"}
                strokeWidth={active ? 2.5 * scale : 1.5 * scale}
                strokeDasharray={active ? undefined : "none"}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const type = node.type ?? "core";
            const r = (NODE_R[type] ?? 12) * scale;
            const max = node.maxPoints ?? 1;
            const pts = allocated[node.id] ?? 0;
            const active = pts >= 1;
            const unlocked = isUnlocked(node.id);
            const colors = COLORS[type as keyof typeof COLORS] ?? COLORS.core;
            const fill = active ? colors.active : colors.idle;
            const stroke = active ? "#e8b040" : unlocked ? colors.border : "#2a2218";

            return (
              <g
                key={node.id}
                transform={`translate(${sx(node.x)},${sy(node.y)})`}
                style={{ cursor: readOnly || !unlocked ? "default" : "pointer" }}
                onClick={() => handleClick(node)}
                onMouseEnter={() => setTooltip({ node, svgX: node.x, svgY: node.y })}
                onMouseLeave={() => setTooltip(null)}
              >
                {/* Keystone diamond ring */}
                {type === "keystone" && (
                  <polygon
                    points={`0,${-(r + 6 * scale)} ${r + 6 * scale},0 0,${r + 6 * scale} ${-(r + 6 * scale)},0`}
                    fill="none"
                    stroke={active ? "#e8b040" : "#3a5a3a"}
                    strokeWidth={1.5 * scale}
                    opacity={unlocked ? 1 : 0.25}
                  />
                )}

                {/* Node circle */}
                <circle
                  r={r}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={(type === "keystone" ? 2.5 : 1.5) * scale}
                  opacity={unlocked || active ? 1 : 0.3}
                />

                {/* Multi-point counter */}
                {max > 1 && (
                  <text
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize={r * 0.8}
                    fill={active ? "#1a1208" : "#777"}
                    fontFamily="monospace"
                    fontWeight="bold"
                    pointerEvents="none"
                  >
                    {pts}/{max}
                  </text>
                )}

                {/* Node name label (only for named non-core nodes) */}
                {node.name && (type === "notable" || type === "keystone") && (
                  <text
                    y={r + 11 * scale}
                    textAnchor="middle"
                    fontSize={8.5 * scale}
                    fill={active ? "#e8b040" : unlocked ? "#9a8870" : "#555"}
                    fontFamily="monospace"
                    pointerEvents="none"
                  >
                    {node.name.length > 16 ? node.name.slice(0, 15) + "…" : node.name}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Tooltip overlay (positioned absolutely inside the scroll container) */}
        {tooltip && (() => {
          const n = tooltip.node;
          const max = n.maxPoints ?? 1;
          const pts = allocated[n.id] ?? 0;
          const x = sx(tooltip.svgX) + 16;
          const y = sy(tooltip.svgY) - 12;
          return (
            <div
              className="pointer-events-none absolute z-10 max-w-[220px] rounded border border-forge-amber/60 bg-forge-bg/95 p-3 shadow-xl"
              style={{ left: x, top: Math.max(4, y) }}
            >
              <div className="font-display text-sm font-bold text-forge-amber leading-tight">
                {n.name || "Unnamed Node"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                {n.type} · {pts}/{max} pts
              </div>
              {n.description && (
                <div className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text">
                  {n.description}
                </div>
              )}
              {!readOnly && !isUnlocked(n.id) && (
                <div className="mt-1.5 font-mono text-[10px] text-red-400/80">
                  Requires parent node
                </div>
              )}
            </div>
          );
        })()}
      </div>

      {/* Footer: legend + instructions */}
      <div className="flex flex-wrap items-center gap-4 border-t border-forge-border px-3 py-1.5 text-[10px] font-mono text-forge-dim bg-forge-surface2 shrink-0">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#28201a] border border-[#5a4a28]" />
          Core
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#1c2030] border border-[#3a5a90]" />
          Notable
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full bg-[#18281a] border border-[#3a6a3a]" />
          Keystone
        </span>
        {regionPoints > 0 && (
          <span className="text-forge-amber">{regionPoints} pts in region</span>
        )}
        {!readOnly && (
          <span className="ml-auto">Hover to inspect · click to invest · click again to refund</span>
        )}
        <span className={readOnly ? "ml-auto" : ""}>Scroll to navigate</span>
      </div>
    </div>
  );
}
