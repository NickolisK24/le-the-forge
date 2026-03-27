/**
 * PassiveTreeRenderer — SVG-based passive tree visualizer.
 *
 * - Nodes are circles positioned at their game-data x/y coordinates
 * - Edges are drawn between connected nodes (from `connections` parent IDs)
 * - Base class nodes: muted blue, mastery nodes: cyan / amber / purple by mastery_index
 * - Node radius: larger for single-point keystones (max_points === 1), standard for multi-point
 * - Hover tooltip: name, description, stats, mastery requirement
 * - Click: allocate one point; click at max: deallocate
 * - mastery_requirement > 0: node locked (dim) until enough total points spent
 */

import { useState, useMemo, useRef, useEffect } from "react";
import type { PassiveNode } from "@/services/passiveTreeService";

// ---------------------------------------------------------------------------
// Palette — indexed by mastery_index (0 = base, 1/2/3 = masteries)
// ---------------------------------------------------------------------------
const PALETTE: Record<
  number,
  { nodeFill: string; strokeIdle: string; strokeActive: string; edgeIdle: string; edgeActive: string; label: string }
> = {
  0: {
    nodeFill:    "#181c30",
    strokeIdle:  "#3a4070",
    strokeActive:"#8890b8",
    edgeIdle:    "#252940",
    edgeActive:  "#6670a0",
    label: "Base",
  },
  1: {
    nodeFill:    "#0a1e26",
    strokeIdle:  "#1a5570",
    strokeActive:"#00d4f5",
    edgeIdle:    "#152232",
    edgeActive:  "#00a8c0",
    label: "Mastery I",
  },
  2: {
    nodeFill:    "#221a08",
    strokeIdle:  "#664410",
    strokeActive:"#f0a020",
    edgeIdle:    "#2e2010",
    edgeActive:  "#c08018",
    label: "Mastery II",
  },
  3: {
    nodeFill:    "#180d2a",
    strokeIdle:  "#4c1880",
    strokeActive:"#b870ff",
    edgeIdle:    "#200e32",
    edgeActive:  "#9050d8",
    label: "Mastery III",
  },
};

// Base radii in world-unit space; scaled proportionally at render time
const R_STANDARD = 14; // max_points > 1  (repeatable core node)
const R_KEYSTONE  = 20; // max_points === 1 (single-invest keystone/notable)

const CANVAS_H = 560;

// ---------------------------------------------------------------------------
// Layout helpers
// ---------------------------------------------------------------------------
interface LayoutNode extends PassiveNode {
  lx: number; // centred world-space x
  ly: number; // centred world-space y
}

function toLayout(nodes: PassiveNode[]): LayoutNode[] {
  if (!nodes.length) return [];
  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  return nodes.map((n) => ({ ...n, lx: n.x - midX, ly: -(n.y - midY) }));
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export type AllocMap = Record<string, number>;

interface TooltipInfo {
  node: PassiveNode;
  screenX: number;
  screenY: number;
}

interface Props {
  nodes: PassiveNode[];
  allocated: AllocMap;
  onAllocate: (nodeId: string, points: number) => void;
  readOnly?: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function PassiveTreeRenderer({
  nodes,
  allocated,
  onAllocate,
  readOnly = false,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ w: 800, h: CANVAS_H });
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  // Track container size for responsive scaling
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setCanvasSize({ w: width, h: height });
    });
    ro.observe(el);
    setCanvasSize({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  // Centre & compute auto-fit scale
  const layout = useMemo(() => toLayout(nodes), [nodes]);
  const byId   = useMemo(() => new Map(layout.map((n) => [n.id, n])), [layout]);

  const { scale, ox, oy } = useMemo(() => {
    if (!layout.length) return { scale: 1, ox: 0, oy: 0 };
    const pad = 60;
    const xs = layout.map((n) => n.lx);
    const ys = layout.map((n) => n.ly);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const tW = maxX - minX || 1;
    const tH = maxY - minY || 1;
    const s   = Math.min(
      (canvasSize.w - pad * 2) / tW,
      (canvasSize.h - pad * 2) / tH,
    );
    return {
      scale: s,
      ox: (canvasSize.w - tW * s) / 2 - minX * s,
      oy: (canvasSize.h - tH * s) / 2 - minY * s,
    };
  }, [layout, canvasSize]);

  const sc = (lx: number, ly: number) => ({
    sx: lx * scale + ox,
    sy: ly * scale + oy,
  });

  // Total points spent (for mastery requirement checks)
  const totalSpent = useMemo(
    () => Object.values(allocated).reduce((a, b) => a + b, 0),
    [allocated],
  );

  const isUnlocked = (node: PassiveNode) =>
    totalSpent >= node.mastery_requirement;

  // Build edge list from connections (connections = parent IDs → draw line to this node)
  const edges = useMemo(() => {
    const result: Array<{ fromId: string; toId: string }> = [];
    for (const node of layout) {
      for (const connId of node.connections) {
        if (byId.has(connId)) {
          result.push({ fromId: connId, toId: node.id });
        }
      }
    }
    return result;
  }, [layout, byId]);

  // Legend: unique masteries present in the current node set
  const legendEntries = useMemo(() => {
    const seen = new Map<number, string>(); // mastery_index → mastery name (or "Base")
    for (const n of nodes) {
      if (!seen.has(n.mastery_index)) {
        seen.set(n.mastery_index, n.mastery ?? "Base");
      }
    }
    return Array.from(seen.entries()).sort(([a], [b]) => a - b);
  }, [nodes]);

  const handleClick = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.stopPropagation();
    const pts = allocated[node.id] ?? 0;
    if (pts >= node.max_points) {
      onAllocate(node.id, pts - 1);
    } else if (isUnlocked(node)) {
      onAllocate(node.id, pts + 1);
    }
  };

  return (
    <div className="flex flex-col overflow-hidden" style={{ background: "#0b0e1a" }}>
      {/* SVG canvas */}
      <div
        ref={containerRef}
        className="relative overflow-hidden select-none"
        style={{ height: CANVAS_H }}
      >
        <svg
          width={canvasSize.w}
          height={canvasSize.h}
          style={{ display: "block", position: "absolute", inset: 0 }}
        >
          <defs>
            <radialGradient id="pt-vignette" cx="50%" cy="50%" r="70%">
              <stop offset="0%"   stopColor="transparent" />
              <stop offset="100%" stopColor="#000000" stopOpacity="0.50" />
            </radialGradient>
            <filter id="pt-glow" x="-60%" y="-60%" width="220%" height="220%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background */}
          <rect width={canvasSize.w} height={canvasSize.h} fill="#0b0e1a" />
          <rect width={canvasSize.w} height={canvasSize.h} fill="url(#pt-vignette)" />

          {/* Edges */}
          <g>
            {edges.map(({ fromId, toId }) => {
              const from = byId.get(fromId);
              const to   = byId.get(toId);
              if (!from || !to) return null;
              const bothActive =
                (allocated[fromId] ?? 0) >= 1 && (allocated[toId] ?? 0) >= 1;
              const pal = PALETTE[to.mastery_index ?? 0] ?? PALETTE[0];
              const { sx: x1, sy: y1 } = sc(from.lx, from.ly);
              const { sx: x2, sy: y2 } = sc(to.lx, to.ly);
              return (
                <line
                  key={`e-${fromId}-${toId}`}
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke={bothActive ? pal.edgeActive : pal.edgeIdle}
                  strokeWidth={bothActive
                    ? Math.max(1.5, 2.5 * scale)
                    : Math.max(0.5, 1.0 * scale)}
                  opacity={bothActive ? 0.85 : 0.45}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {layout.map((node) => {
              const baseR   = node.max_points === 1 ? R_KEYSTONE : R_STANDARD;
              const r       = Math.max(5, baseR * scale);
              const pts     = allocated[node.id] ?? 0;
              const active  = pts >= 1;
              const unlocked = isUnlocked(node);
              const pal     = PALETTE[node.mastery_index ?? 0] ?? PALETTE[0];
              const { sx, sy } = sc(node.lx, node.ly);

              return (
                <g
                  key={node.id}
                  transform={`translate(${sx},${sy})`}
                  opacity={unlocked || active ? 1 : 0.22}
                  style={{
                    cursor: readOnly ? "default" : unlocked ? "pointer" : "not-allowed",
                  }}
                  onClick={(e) => handleClick(node, e)}
                  onMouseEnter={(e) =>
                    setTooltip({ node, screenX: e.clientX, screenY: e.clientY })
                  }
                  onMouseMove={(e) =>
                    setTooltip((t) =>
                      t ? { ...t, screenX: e.clientX, screenY: e.clientY } : null,
                    )
                  }
                  onMouseLeave={() => setTooltip(null)}
                >
                  {/* Glow halo when active */}
                  {active && (
                    <circle
                      r={r + 4 * scale}
                      fill={pal.strokeActive}
                      opacity={0.16}
                      filter="url(#pt-glow)"
                      pointerEvents="none"
                    />
                  )}
                  {/* Outer ring */}
                  <circle
                    r={r + Math.max(1.5, 2 * scale)}
                    fill="none"
                    stroke={active ? pal.strokeActive : pal.strokeIdle}
                    strokeWidth={active ? 1.5 : 0.8}
                    opacity={active ? 0.9 : 0.45}
                    pointerEvents="none"
                  />
                  {/* Node body */}
                  <circle
                    r={r}
                    fill={pal.nodeFill}
                    stroke={active ? pal.strokeActive : pal.strokeIdle}
                    strokeWidth={active ? 1.5 : 1}
                  />
                  {/* Points label (only for multi-point core nodes) */}
                  {node.max_points > 1 && (
                    <text
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize={Math.max(7, 10 * scale)}
                      fill={active ? pal.strokeActive : pal.strokeIdle}
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                      opacity={0.9}
                    >
                      {pts}/{node.max_points}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Tooltip */}
        {tooltip &&
          (() => {
            const n   = tooltip.node;
            const pts = allocated[n.id] ?? 0;
            const locked = !isUnlocked(n);
            const rect   = containerRef.current?.getBoundingClientRect();
            if (!rect) return null;
            const tx  = tooltip.screenX - rect.left + 16;
            const ty  = tooltip.screenY - rect.top  - 12;
            const pal = PALETTE[n.mastery_index ?? 0] ?? PALETTE[0];
            return (
              <div
                className="pointer-events-none absolute z-20 w-64 rounded border bg-forge-bg/96 p-3 shadow-2xl"
                style={{
                  left: Math.min(tx, canvasSize.w - 272),
                  top:  Math.max(4, Math.min(ty, canvasSize.h - 220)),
                  borderColor: pal.strokeActive + "80",
                }}
              >
                <div
                  className="font-display text-sm font-bold leading-tight"
                  style={{ color: pal.strokeActive }}
                >
                  {n.name || "Passive Node"}
                </div>
                <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                  {n.node_type} · {pts}/{n.max_points} pts
                  {n.mastery && (
                    <span className="text-forge-dim"> · {n.mastery}</span>
                  )}
                </div>

                {n.description && (
                  <p className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text/90 whitespace-pre-line">
                    {n.description}
                  </p>
                )}

                {n.stats.length > 0 && (
                  <ul className="mt-1.5 space-y-0.5">
                    {n.stats.map((s, i) => (
                      <li key={i} className="font-mono text-[10px] text-forge-cyan/80">
                        {s.key}: {s.value}
                      </li>
                    ))}
                  </ul>
                )}

                {n.ability_granted && (
                  <div className="mt-1 font-mono text-[10px] text-forge-amber/80">
                    Grants: {n.ability_granted}
                  </div>
                )}

                {n.mastery_requirement > 0 && (
                  <div
                    className={`mt-1.5 font-mono text-[10px] ${
                      totalSpent >= n.mastery_requirement
                        ? "text-forge-dim"
                        : "text-yellow-400/80"
                    }`}
                  >
                    ⬡ Requires {n.mastery_requirement} total points (
                    {totalSpent}/{n.mastery_requirement})
                  </div>
                )}

                {locked && !readOnly && (
                  <div className="mt-1 font-mono text-[10px] text-red-400/80">
                    ⚠ Invest{" "}
                    {n.mastery_requirement - totalSpent} more point
                    {n.mastery_requirement - totalSpent !== 1 ? "s" : ""} first
                  </div>
                )}
              </div>
            );
          })()}
      </div>

      {/* Legend + hint */}
      <div className="flex flex-wrap items-center gap-4 border-t border-forge-border bg-forge-surface2 px-3 py-1.5">
        {legendEntries.map(([idx, name]) => {
          const pal = PALETTE[idx] ?? PALETTE[0];
          return (
            <span key={idx} className="flex items-center gap-1.5 font-mono text-[10px] text-forge-dim">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full border"
                style={{ background: pal.nodeFill, borderColor: pal.strokeActive }}
              />
              {name}
            </span>
          );
        })}
        {!readOnly && (
          <span className="ml-auto font-mono text-[10px] text-forge-dim/60">
            click to invest · click again to refund
          </span>
        )}
      </div>
    </div>
  );
}
