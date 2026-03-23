import { useState, useMemo, useRef, useCallback, useEffect } from "react";
import { clsx } from "clsx";
import type { PassiveNode } from "@/lib/gameData";
import { PASSIVE_TREES } from "@/data/passiveTrees";
import { PASSIVE_TREE_META } from "@/data/passiveTrees/edges";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const NODE_R: Record<string, number> = {
  core: 10,
  notable: 16,
  keystone: 24,
  "mastery-gate": 14,
};

const COLORS = {
  core:          { idle: "#28201a", active: "#c8902a", border: "#5a4a28", glow: "#c8902a" },
  notable:       { idle: "#1a1e2e", active: "#5c8fd6", border: "#3a5a90", glow: "#5c8fd6" },
  keystone:      { idle: "#1a2a1c", active: "#3ca040", border: "#3a7a3e", glow: "#3ca040" },
  "mastery-gate":{ idle: "#2a1818", active: "#c04040", border: "#7a2a2a", glow: "#c04040" },
} as const;

const REGION_LABELS: Record<string, string> = {
  base:          "Base",
  necromancer:   "Necromancer",
  lich:          "Lich",
  warlock:       "Warlock",
  runemaster:    "Runemaster",
  sorcerer:      "Sorcerer",
  spellblade:    "Spellblade",
  beastmaster:   "Beastmaster",
  druid:         "Druid",
  shaman:        "Shaman",
  "forge-guard": "Forge Guard",
  paladin:       "Paladin",
  "void-knight": "Void Knight",
  bladedancer:   "Bladedancer",
  marksman:      "Marksman",
  falconer:      "Falconer",
};

// Maximum passive points per class (Last Epoch: 1 per level, levels 1-100)
const MAX_PASSIVE_POINTS = 113; // ~113 by end-game with all sources

const DISPLAY_H = 560;    // fixed display area height

// ---------------------------------------------------------------------------
// Layout — use real game x,y, centered around the canvas midpoint
// ---------------------------------------------------------------------------
interface LayoutNode extends PassiveNode {
  lx: number; // world x (origin at canvas center)
  ly: number; // world y (origin at canvas center)
}

function toLayoutNodes(nodes: PassiveNode[]): LayoutNode[] {
  if (nodes.length === 0) return [];
  // Data x,y are already in screen-space pixels (canvas ~1170×601).
  // Compute canvas center from bounding box so the tree is centered at (0,0).
  const xs = nodes.map(n => n.x);
  const ys = nodes.map(n => n.y);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  return nodes.map(n => ({ ...n, lx: n.x - midX, ly: n.y - midY }));
}

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
  /** Total passive points the character has earned (defaults to MAX_PASSIVE_POINTS) */
  totalPassivePoints?: number;
}

interface TooltipInfo {
  node: PassiveNode;
  screenX: number;
  screenY: number;
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
  totalPassivePoints = MAX_PASSIVE_POINTS,
}: Props) {
  const cls = characterClass.toLowerCase();
  const regionMap = PASSIVE_TREES[cls] ?? {};
  const regionKeys = Object.keys(regionMap);
  const classMeta = PASSIVE_TREE_META[cls] ?? {};

  const masteryKey = mastery.toLowerCase().replace(/\s+/g, "-");
  const defaultRegion = regionKeys.includes(masteryKey) ? masteryKey : (regionKeys[0] ?? "base");
  const [activeRegion, setActiveRegion] = useState(defaultRegion);

  const rawNodes: PassiveNode[] = useMemo(
    () => regionMap[activeRegion] ?? [],
    [regionMap, activeRegion]
  );

  const layoutNodes = useMemo(() => toLayoutNodes(rawNodes), [rawNodes]);

  const byId = useMemo(
    () => new Map(layoutNodes.map(n => [n.id, n])),
    [layoutNodes]
  );

  // Build edge list for the current region: [{fromId, toId}]
  // An edge exists for every parentId in PASSIVE_TREE_META for nodes in this region
  const edges = useMemo(() => {
    const result: Array<{ from: number; to: number }> = [];
    for (const node of layoutNodes) {
      const meta = classMeta[node.id];
      if (!meta) continue;
      for (const pid of meta.parentIds) {
        if (byId.has(pid)) {
          result.push({ from: pid, to: node.id });
        }
      }
    }
    return result;
  }, [layoutNodes, byId, classMeta]);

  // Total points spent across ALL regions
  const totalSpent = Object.values(allocated).reduce((s, v) => s + v, 0);
  const pointsLeft = totalPassivePoints - totalSpent;

  // Pan / zoom state
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1.0);
  const dragging = useRef(false);
  const lastMouse = useRef({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Reset pan/zoom when region changes
  useEffect(() => {
    setPan({ x: 0, y: 0 });
    setZoom(1.0);
  }, [activeRegion]);

  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);
  const [containerSize, setContainerSize] = useState({ w: 800, h: DISPLAY_H });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setContainerSize({ w: width, h: height });
    });
    ro.observe(el);
    setContainerSize({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  // Mouse handlers for pan
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    dragging.current = true;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current) return;
    const dx = e.clientX - lastMouse.current.x;
    const dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    setPan(p => ({ x: p.x + dx, y: p.y + dy }));
  }, []);

  const handleMouseUp = useCallback(() => {
    dragging.current = false;
  }, []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom(z => Math.max(0.3, Math.min(3.0, z * factor)));
  }, []);

  /**
   * A node is unlocked if:
   * 1. It has no parent requirements (free), OR
   *    ALL parents have at least 1 point allocated
   * 2. The total points spent in the tree >= masteryRequirement
   */
  function isUnlocked(nodeId: number): boolean {
    const meta = classMeta[nodeId];
    if (!meta) return true;
    // Check mastery point threshold
    if (meta.masteryRequirement > 0 && totalSpent < meta.masteryRequirement) return false;
    // Check parent requirements — all parents must be allocated
    if (meta.parentIds.length === 0) return true;
    return meta.parentIds.every(pid => (allocated[pid] ?? 0) >= 1);
  }

  function handleNodeClick(node: LayoutNode, e: React.MouseEvent) {
    e.stopPropagation();
    if (readOnly) return;
    const max = node.maxPoints ?? 1;
    const current = allocated[node.id] ?? 0;

    if (current >= max) {
      // Refund: only allowed if no allocated child depends on this node
      const meta = classMeta[node.id];
      const hasAllocChild = layoutNodes.some(n => {
        const nm = classMeta[n.id];
        return nm?.parentIds.includes(node.id) && (allocated[n.id] ?? 0) > 0;
      });
      if (!hasAllocChild) onAllocate(node.id, current - 1);
    } else {
      if (!isUnlocked(node.id)) return;
      if (pointsLeft <= 0) return; // no points remaining
      onAllocate(node.id, current + 1);
    }
  }

  // "Double-click to reset view" helper
  const handleSvgDoubleClick = useCallback(() => {
    setPan({ x: 0, y: 0 });
    setZoom(1.0);
  }, []);

  const regionPoints = layoutNodes.reduce((s, n) => s + (allocated[n.id] ?? 0), 0);

  // Center of SVG viewport
  const cx = containerSize.w / 2;
  const cy = containerSize.h / 2;
  // World→screen: screen = (world * zoom) + pan + center
  const worldToScreen = (wx: number, wy: number) => ({
    sx: wx * zoom + pan.x + cx,
    sy: wy * zoom + pan.y + cy,
  });

  return (
    <div className="flex flex-col gap-0 rounded border border-forge-border bg-forge-surface overflow-hidden">

      {/* Point budget bar */}
      <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-3 py-1.5 shrink-0">
        <div className="flex items-center gap-3 font-mono text-[10px]">
          <span className="text-forge-dim uppercase tracking-widest">Passive Points</span>
          <span className={clsx("font-bold", totalSpent > 0 ? "text-forge-amber" : "text-forge-dim")}>
            {totalSpent} spent
          </span>
          <span className="text-forge-dim">·</span>
          <span className={clsx("font-bold", pointsLeft < 10 ? "text-red-400" : "text-forge-text")}>
            {pointsLeft} remaining
          </span>
          <span className="text-forge-dim">/ {totalPassivePoints}</span>
        </div>
        {!readOnly && pointsLeft === 0 && (
          <span className="font-mono text-[9px] text-red-400/80">All points spent</span>
        )}
      </div>

      {/* Region tabs */}
      <div className="flex items-stretch border-b border-forge-border bg-forge-surface2 overflow-x-auto shrink-0">
        {regionKeys.map(key => {
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
                  ? "bg-forge-bg text-forge-amber"
                  : "text-forge-dim hover:text-forge-text"
              )}
            >
              {REGION_LABELS[key] ?? key}
              {pts > 0 && <span className="ml-1.5 text-forge-amber opacity-80">{pts}</span>}
            </button>
          );
        })}
        <div className="ml-auto flex items-center px-3 font-mono text-[10px] text-forge-dim whitespace-nowrap">
          {layoutNodes.length} nodes · {edges.length} connections
        </div>
      </div>

      {/* SVG canvas — pan + zoom */}
      <div
        ref={containerRef}
        className="relative overflow-hidden bg-forge-bg select-none"
        style={{ height: DISPLAY_H, cursor: dragging.current ? "grabbing" : "grab" }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onDoubleClick={handleSvgDoubleClick}
      >
        <svg
          ref={svgRef}
          width={containerSize.w}
          height={containerSize.h}
          style={{ display: "block", position: "absolute", inset: 0 }}
        >
          <defs>
            {/* Glow filter for active nodes */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            {/* Background radial gradient */}
            <radialGradient id="bg-grad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#1a1612" />
              <stop offset="100%" stopColor="#0e0c0a" />
            </radialGradient>
          </defs>

          {/* Background */}
          <rect width={containerSize.w} height={containerSize.h} fill="url(#bg-grad)" />

          {/* Edges — rendered from full edge list extracted from game metadata */}
          <g>
            {edges.map(({ from, to }) => {
              const fromNode = byId.get(from);
              const toNode = byId.get(to);
              if (!fromNode || !toNode) return null;
              const bothActive =
                (allocated[from] ?? 0) >= 1 &&
                (allocated[to] ?? 0) >= 1;
              const toUnlocked = isUnlocked(to);
              const { sx: x1, sy: y1 } = worldToScreen(fromNode.lx, fromNode.ly);
              const { sx: x2, sy: y2 } = worldToScreen(toNode.lx, toNode.ly);
              return (
                <line
                  key={`e-${from}-${to}`}
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke={bothActive ? "#c8902a" : toUnlocked ? "#3a3020" : "#181614"}
                  strokeWidth={bothActive ? 2.5 : 1.5}
                  opacity={bothActive ? 1 : toUnlocked ? 0.6 : 0.2}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {layoutNodes.map(node => {
              const type = node.type ?? "core";
              const r = (NODE_R[type] ?? 10) * Math.max(0.6, zoom);
              const max = node.maxPoints ?? 1;
              const pts = allocated[node.id] ?? 0;
              const active = pts >= 1;
              const unlocked = isUnlocked(node.id);
              const colors = COLORS[type as keyof typeof COLORS] ?? COLORS.core;
              const fill = active ? colors.active : colors.idle;
              const stroke = active ? "#e8b040" : unlocked ? colors.border : "#222018";
              const { sx: scx, sy: scy } = worldToScreen(node.lx, node.ly);

              return (
                <g
                  key={node.id}
                  transform={`translate(${scx},${scy})`}
                  style={{ cursor: readOnly || !unlocked ? "default" : "pointer" }}
                  onClick={e => handleNodeClick(node, e)}
                  onMouseEnter={e => setTooltip({ node, screenX: e.clientX, screenY: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, screenX: e.clientX, screenY: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {/* Glow ring for active nodes */}
                  {active && (
                    <circle
                      r={r + 4}
                      fill={colors.glow}
                      opacity={0.2}
                      filter="url(#glow)"
                    />
                  )}

                  {/* Keystone outer diamond */}
                  {type === "keystone" && (
                    <polygon
                      points={`0,${-(r + 7)} ${r + 7},0 0,${r + 7} ${-(r + 7)},0`}
                      fill="none"
                      stroke={active ? "#e8b040" : unlocked ? colors.border : "#2a2218"}
                      strokeWidth={1.5}
                      opacity={unlocked ? 1 : 0.2}
                    />
                  )}

                  {/* Mastery-gate outer square */}
                  {type === "mastery-gate" && (
                    <rect
                      x={-(r + 5)} y={-(r + 5)}
                      width={(r + 5) * 2} height={(r + 5) * 2}
                      fill="none"
                      stroke={active ? "#e84040" : unlocked ? colors.border : "#2a1818"}
                      strokeWidth={1}
                      opacity={unlocked ? 1 : 0.2}
                      rx={2}
                    />
                  )}

                  {/* Node body */}
                  <circle
                    r={r}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={active ? 2 : 1}
                    opacity={unlocked || active ? 1 : 0.25}
                  />

                  {/* Multi-point fill arcs */}
                  {max > 1 && pts > 0 && pts < max && (
                    <text
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize={Math.max(7, r * 0.7)}
                      fill={active ? "#1a1208" : "#888"}
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {pts}/{max}
                    </text>
                  )}
                  {max > 1 && pts === max && (
                    <text
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize={Math.max(7, r * 0.7)}
                      fill="#1a1208"
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {pts}/{max}
                    </text>
                  )}

                  {/* Node name — notable & keystone only, shown when zoomed in */}
                  {node.name && (type === "notable" || type === "keystone") && zoom >= 0.7 && (
                    <text
                      y={r + Math.max(9, 11 * zoom)}
                      textAnchor="middle"
                      fontSize={Math.max(7, 9 * zoom)}
                      fill={active ? "#e8b040" : unlocked ? "#9a8870" : "#444"}
                      fontFamily="monospace"
                      pointerEvents="none"
                    >
                      {node.name.length > 18 ? node.name.slice(0, 17) + "…" : node.name}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Tooltip — follows the mouse cursor */}
        {tooltip && (() => {
          const n = tooltip.node;
          const max = n.maxPoints ?? 1;
          const pts = allocated[n.id] ?? 0;
          const nodeMeta = classMeta[n.id];
          const mr = nodeMeta?.masteryRequirement ?? 0;
          const locked = !isUnlocked(n.id);
          const containerRect = containerRef.current?.getBoundingClientRect();
          if (!containerRect) return null;
          const tx = tooltip.screenX - containerRect.left + 16;
          const ty = tooltip.screenY - containerRect.top - 12;
          return (
            <div
              className="pointer-events-none absolute z-20 w-64 rounded border border-forge-amber/50 bg-forge-bg/95 p-3 shadow-2xl"
              style={{ left: Math.min(tx, containerSize.w - 272), top: Math.max(4, ty) }}
            >
              <div className="font-display text-sm font-bold text-forge-amber leading-tight">
                {n.name || "Node"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                {n.type} · {pts}/{max} pts
              </div>
              {n.description && (
                <div className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text/90 whitespace-pre-line">
                  {n.description.replace(/\s{2,}/g, "\n")}
                </div>
              )}
              {mr > 0 && (
                <div className={clsx(
                  "mt-1.5 font-mono text-[10px]",
                  totalSpent >= mr ? "text-forge-dim" : "text-yellow-400/80"
                )}>
                  ⬡ Requires {mr} total points ({totalSpent}/{mr})
                </div>
              )}
              {!readOnly && locked && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">
                  ⚠ {mr > 0 && totalSpent < mr
                    ? `Invest ${mr - totalSpent} more point${mr - totalSpent > 1 ? "s" : ""} first`
                    : "Requires parent node(s)"}
                </div>
              )}
              {!readOnly && !locked && pts < max && pointsLeft === 0 && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">
                  No passive points remaining
                </div>
              )}
            </div>
          );
        })()}

        {/* Mini HUD */}
        <div className="pointer-events-none absolute bottom-2 right-2 font-mono text-[9px] text-forge-dim/50">
          {Math.round(zoom * 100)}% · drag to pan · scroll to zoom · dbl-click to reset
        </div>
      </div>

      {/* Footer legend */}
      <div className="flex flex-wrap items-center gap-4 border-t border-forge-border px-3 py-1.5 text-[10px] font-mono text-forge-dim bg-forge-surface2 shrink-0">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#28201a] border border-[#5a4a28]" />
          Core
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#1a1e2e] border border-[#3a5a90]" />
          Notable
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#1a2a1c] border border-[#3a7a3e]" />
          Keystone
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#2a1818] border border-[#7a2a2a]" />
          Mastery Gate
        </span>
        {regionPoints > 0 && (
          <span className="text-forge-amber">{regionPoints} pts in region</span>
        )}
        {!readOnly && (
          <span className="ml-auto text-forge-dim/60">click to invest · click again to refund</span>
        )}
      </div>
    </div>
  );
}
