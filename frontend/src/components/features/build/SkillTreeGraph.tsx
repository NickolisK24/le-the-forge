import { useState, useMemo, useRef, useEffect } from "react";
import { clsx } from "clsx";
import type { SkillNode } from "@/data/skillTrees";
import { cleanNodeName, getSkillCode } from "@/data/skillTrees";
import iconSpriteMap from "@/data/iconSpriteMap.json";

// Sprite sheet from lastepochtools CDN
const SPRITE_URL =
  "https://www.lastepochtools.com/data/version140/planner/res/d285216918221e26ef5d5b32f3407c4a.webp";
const SPRITE_ICON_SIZE = 64;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const NODE_R: Record<string, number> = {
  core: 16,
  notable: 22,
  keystone: 30,
  "mastery-gate": 24,
};

// Flat-top hexagon points at radius r
function hexPoints(r: number): string {
  return Array.from({ length: 6 }, (_, i) => {
    const a = (i * 60) * Math.PI / 180;
    return `${(Math.cos(a) * r).toFixed(2)},${(Math.sin(a) * r).toFixed(2)}`;
  }).join(" ");
}

// Sprite icon rendered via foreignObject inside SVG
function SpriteIcon({ iconId, size }: { iconId: string | undefined; size: number }) {
  if (!iconId) return null;
  const pos = (iconSpriteMap as Record<string, [number, number]>)[iconId];
  if (!pos) return null;
  const [bx, by] = pos;
  const scaleFactor = size / SPRITE_ICON_SIZE;
  return (
    <foreignObject
      x={-size / 2}
      y={-size / 2}
      width={size}
      height={size}
      pointerEvents="none"
    >
      <div
        style={{
          width: size,
          height: size,
          backgroundImage: `url(${SPRITE_URL})`,
          backgroundPosition: `-${bx * scaleFactor}px -${by * scaleFactor}px`,
          backgroundSize: `${2387 * scaleFactor}px auto`,
          backgroundRepeat: "no-repeat",
          borderRadius: "50%",
          imageRendering: "auto",
        }}
      />
    </foreignObject>
  );
}

const DISPLAY_H = 520;
const MAX_SKILL_POINTS = 20;

// ---------------------------------------------------------------------------
// Layout — center nodes around midpoint
// ---------------------------------------------------------------------------
interface LayoutNode extends SkillNode {
  lx: number;
  ly: number;
}

function toLayoutNodes(nodes: SkillNode[]): LayoutNode[] {
  if (nodes.length === 0) return [];
  const xs = nodes.map(n => n.x);
  const ys = nodes.map(n => n.y);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  return nodes.map(n => ({ ...n, lx: n.x - midX, ly: n.y - midY }));
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface AllocMap {
  [nodeId: number]: number;
}

interface Props {
  nodes: SkillNode[];
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
  skillName?: string;
}

interface TooltipInfo {
  node: SkillNode;
  screenX: number;
  screenY: number;
}

// ---------------------------------------------------------------------------
// SkillTreeGraph
// ---------------------------------------------------------------------------
export default function SkillTreeGraph({ nodes, allocated, onAllocate, readOnly, skillName }: Props) {
  const layoutNodes = useMemo(() => toLayoutNodes(nodes), [nodes]);
  const byId = useMemo(
    () => new Map(layoutNodes.map(n => [n.id, n])),
    [layoutNodes],
  );

  // Auto-allocate root node (mastery-gate with maxPoints=0): always treated as allocated
  const effectiveAllocated = useMemo(() => {
    const map = { ...allocated };
    for (const node of layoutNodes) {
      if (node.parentId == null && (node.maxPoints ?? 1) === 0) {
        map[node.id] = 1; // always considered allocated
      }
    }
    return map;
  }, [allocated, layoutNodes]);

  const totalPoints = Object.entries(effectiveAllocated).reduce((s, [id, v]) => {
    // Don't count auto-allocated root node towards point budget
    const node = byId.get(Number(id));
    if (node && node.parentId == null && (node.maxPoints ?? 1) === 0) return s;
    return s + v;
  }, 0);
  const pointsLeft = MAX_SKILL_POINTS - totalPoints;

  const containerRef = useRef<HTMLDivElement>(null);
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

  // Compute scale + offset to fit all nodes
  const { scale, offsetX, offsetY } = useMemo(() => {
    if (layoutNodes.length === 0) return { scale: 1, offsetX: 0, offsetY: 0 };
    const pad = 48;
    const xs = layoutNodes.map(n => n.lx);
    const ys = layoutNodes.map(n => n.ly);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const treeW = maxX - minX || 1;
    const treeH = maxY - minY || 1;
    const sx = (containerSize.w - pad * 2) / treeW;
    const sy = (containerSize.h - pad * 2) / treeH;
    const s = Math.min(sx, sy);
    const ox = (containerSize.w - treeW * s) / 2 - minX * s;
    const oy = (containerSize.h - treeH * s) / 2 - minY * s;
    return { scale: s, offsetX: ox, offsetY: oy };
  }, [layoutNodes, containerSize]);

  const worldToScreen = (lx: number, ly: number) => ({
    sx: lx * scale + offsetX,
    sy: ly * scale + offsetY,
  });

  const scaledR = (base: number) => Math.max(4, base * scale);

  // Check parent chain unlock
  function isUnlocked(nodeId: number): boolean {
    const node = byId.get(nodeId);
    if (!node || node.parentId == null) return true;
    const parentPts = effectiveAllocated[node.parentId] ?? 0;
    return parentPts >= 1 && isUnlocked(node.parentId);
  }

  // Check if deallocating a node would orphan any children
  function hasAllocatedChild(nodeId: number): boolean {
    return layoutNodes.some(
      n => n.parentId === nodeId && (effectiveAllocated[n.id] ?? 0) > 0,
    );
  }

  const handleAllocate = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.stopPropagation();
    // Root node with maxPoints=0 is auto-allocated, skip
    if (node.parentId == null && (node.maxPoints ?? 1) === 0) return;
    const pts = effectiveAllocated[node.id] ?? 0;
    const max = node.maxPoints ?? 1;
    if (pts < max && isUnlocked(node.id) && pointsLeft > 0) {
      onAllocate(node.id, pts + 1);
    }
  };

  const handleDeallocate = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.preventDefault();
    e.stopPropagation();
    // Root node with maxPoints=0 is auto-allocated, skip
    if (node.parentId == null && (node.maxPoints ?? 1) === 0) return;
    const pts = effectiveAllocated[node.id] ?? 0;
    if (pts <= 0) return;
    if (!hasAllocatedChild(node.id)) {
      onAllocate(node.id, pts - 1);
    }
  };

  // Build edges from parentId
  const edges = useMemo(() => {
    const result: Array<{ from: number; to: number }> = [];
    for (const node of layoutNodes) {
      if (node.parentId != null && byId.has(node.parentId)) {
        result.push({ from: node.parentId, to: node.id });
      }
    }
    return result;
  }, [layoutNodes, byId]);

  return (
    <div className="flex flex-col gap-0 rounded border border-forge-border bg-forge-surface overflow-hidden">

      {/* Point budget bar */}
      <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-3 py-1.5 shrink-0">
        <div className="flex items-center gap-3 font-mono text-[10px]">
          <span className="text-forge-dim uppercase tracking-widest">Skill Points</span>
          <span className={clsx("font-bold", totalPoints > 0 ? "text-forge-amber" : "text-forge-dim")}>
            {totalPoints} spent
          </span>
          <span className="text-forge-dim">·</span>
          <span className={clsx("font-bold", pointsLeft < 3 ? "text-red-400" : "text-forge-text")}>
            {pointsLeft} remaining
          </span>
          <span className="text-forge-dim">/ {MAX_SKILL_POINTS}</span>
        </div>
        {!readOnly && pointsLeft === 0 && (
          <span className="font-mono text-[9px] text-red-400/80">All points spent</span>
        )}
      </div>

      {/* SVG canvas */}
      <div
        ref={containerRef}
        className="relative overflow-hidden select-none"
        style={{ height: DISPLAY_H, background: "#0b0e1a" }}
      >
        <svg
          width={containerSize.w}
          height={containerSize.h}
          style={{ display: "block", position: "absolute", inset: 0 }}
        >
          <defs>
            <filter id="sk-stone-texture" x="0%" y="0%" width="100%" height="100%">
              <feTurbulence type="fractalNoise" baseFrequency="0.65 0.45" numOctaves="4" seed="8" stitchTiles="stitch" result="noise"/>
              <feColorMatrix type="matrix" result="tinted"
                values="0.06 0 0 0 0.04   0 0.04 0 0 0.02   0 0 0.03 0 0.01   0 0 0 0.35 0"/>
              <feComposite in="tinted" in2="SourceGraphic" operator="over"/>
            </filter>
            <filter id="sk-glow" x="-80%" y="-80%" width="260%" height="260%">
              <feGaussianBlur stdDeviation="5" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="sk-line-glow" x="-20%" y="-300%" width="140%" height="700%">
              <feGaussianBlur stdDeviation="2" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <radialGradient id="sk-vignette" cx="50%" cy="50%" r="70%">
              <stop offset="0%" stopColor="transparent"/>
              <stop offset="100%" stopColor="#000000" stopOpacity="0.55"/>
            </radialGradient>
            <radialGradient id="sk-node-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#3a3228"/><stop offset="100%" stopColor="#1a1410"/>
            </radialGradient>
            <radialGradient id="sk-node-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#e8c060"/><stop offset="60%" stopColor="#c8902a"/><stop offset="100%" stopColor="#7a5010"/>
            </radialGradient>
            <radialGradient id="sk-node-notable-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#2a2e40"/><stop offset="100%" stopColor="#141620"/>
            </radialGradient>
            <radialGradient id="sk-node-notable-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#90c0f0"/><stop offset="60%" stopColor="#4a80c0"/><stop offset="100%" stopColor="#1a3060"/>
            </radialGradient>
            <radialGradient id="sk-node-gate-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#342010"/><stop offset="100%" stopColor="#1a1008"/>
            </radialGradient>
            <radialGradient id="sk-node-gate-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#ffa060"/><stop offset="60%" stopColor="#d04020"/><stop offset="100%" stopColor="#701008"/>
            </radialGradient>
          </defs>

          <rect width={containerSize.w} height={containerSize.h} fill="#0b0e1a"/>
          <rect width={containerSize.w} height={containerSize.h} filter="url(#sk-stone-texture)" fill="#0b0e1a"/>
          <rect width={containerSize.w} height={containerSize.h} fill="url(#sk-vignette)"/>

          {/* Edges */}
          <g>
            {edges.map(({ from, to }) => {
              const fromNode = byId.get(from);
              const toNode = byId.get(to);
              if (!fromNode || !toNode) return null;
              const bothActive = (effectiveAllocated[from] ?? 0) >= 1 && (effectiveAllocated[to] ?? 0) >= 1;
              const toUnlocked = isUnlocked(to);
              const { sx: x1, sy: y1 } = worldToScreen(fromNode.lx, fromNode.ly);
              const { sx: x2, sy: y2 } = worldToScreen(toNode.lx, toNode.ly);
              return (
                <line key={`e-${from}-${to}`}
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke={bothActive ? "#c8902a" : toUnlocked ? "#7a6a40" : "#3a3020"}
                  strokeWidth={bothActive ? Math.max(2, 3 * scale) : Math.max(1, 2 * scale)}
                  opacity={bothActive ? 1 : toUnlocked ? 0.8 : 0.4}
                  filter={bothActive ? "url(#sk-line-glow)" : undefined}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {layoutNodes.map(node => {
              const type = node.type ?? "core";
              const isRoot = node.parentId == null && (node.maxPoints ?? 1) === 0;
              const r = scaledR(NODE_R[type] ?? 16);
              const outerR = r + Math.max(2, 4 * scale);
              const max = node.maxPoints ?? 1;
              const pts = effectiveAllocated[node.id] ?? 0;
              const active = pts >= 1;
              const unlocked = isUnlocked(node.id);
              const { sx: scx, sy: scy } = worldToScreen(node.lx, node.ly);

              let fillGrad = active ? "url(#sk-node-active)" : "url(#sk-node-idle)";
              if (type === "notable") fillGrad = active ? "url(#sk-node-notable-active)" : "url(#sk-node-notable-idle)";
              else if (type === "mastery-gate") fillGrad = active ? "url(#sk-node-gate-active)" : "url(#sk-node-gate-idle)";

              const borderCol = active
                ? (type === "notable" ? "#70a8e0" : type === "mastery-gate" ? "#d06030" : "#d4a030")
                : unlocked
                  ? (type === "notable" ? "#3a5080" : type === "mastery-gate" ? "#7a3010" : "#5a4820")
                  : "#1e1a12";

              const hexPts = hexPoints(r);
              const outerPts = hexPoints(outerR);
              const fontSize = Math.max(7, 11 * scale);
              const labelSize = Math.max(6, 9 * scale);

              return (
                <g key={node.id}
                  transform={`translate(${scx},${scy})`}
                  opacity={unlocked || active ? 1 : 0.22}
                  style={{ cursor: readOnly || isRoot ? "default" : unlocked ? "pointer" : "not-allowed" }}
                  onClick={e => handleAllocate(node, e)}
                  onContextMenu={e => handleDeallocate(node, e)}
                  onMouseEnter={e => setTooltip({ node, screenX: e.clientX, screenY: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, screenX: e.clientX, screenY: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {active && <polygon points={outerPts} fill={borderCol} opacity={0.22} filter="url(#sk-glow)"/>}
                  <polygon points={outerPts} fill="none" stroke={borderCol} strokeWidth={active ? 2 : 1} opacity={active ? 0.9 : 0.45}/>
                  <polygon points={hexPts} fill={fillGrad}/>
                  <polygon points={hexPoints(r * 0.72)} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>

                  {/* Node icon from sprite sheet */}
                  <SpriteIcon iconId={node.iconId} size={r * 1.6} />

                  {/* Point counter (skip for auto-allocated root) */}
                  {!isRoot && (
                    <text
                      y={outerR + fontSize * 0.3}
                      textAnchor="middle"
                      fontSize={fontSize}
                      fill={active ? "#d4a030" : unlocked ? "#6a5c40" : "#3a3020"}
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {pts}/{max}
                    </text>
                  )}

                  {/* Node name for notables and root */}
                  {node.name && (type === "notable" || type === "mastery-gate") && scale >= 0.35 && (
                    <text
                      y={isRoot ? outerR + fontSize * 0.3 : outerR + fontSize * 0.3 + labelSize + 2}
                      textAnchor="middle"
                      fontSize={labelSize}
                      fill={active ? "#e8c060" : unlocked ? "#8a7a58" : "#3a3020"}
                      fontFamily="serif"
                      fontStyle="italic"
                      pointerEvents="none"
                    >
                      {(() => {
                        const label = cleanNodeName(node.name);
                        return label.length > 20 ? label.slice(0, 19) + "…" : label;
                      })()}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Tooltip */}
        {tooltip && (() => {
          const n = tooltip.node;
          const isRoot = n.parentId == null && (n.maxPoints ?? 1) === 0;
          const max = n.maxPoints ?? 1;
          const pts = effectiveAllocated[n.id] ?? 0;
          const locked = !isUnlocked(n.id);
          const containerRect = containerRef.current?.getBoundingClientRect();
          if (!containerRect) return null;
          const tx = tooltip.screenX - containerRect.left + 16;
          const ty = tooltip.screenY - containerRect.top - 12;

          // Parse description: text before "|" is flavor, after "|" is structured stats
          const raw = n.description ?? "";
          const pipeIdx = raw.indexOf("|");
          const flavorText = pipeIdx >= 0 ? raw.slice(0, pipeIdx).trim() : raw.trim();
          const statsText = pipeIdx >= 0 ? raw.slice(pipeIdx + 1).trim() : "";
          const statEntries = statsText
            ? statsText.split(";").map(s => s.trim()).filter(Boolean)
            : [];

          return (
            <div
              className="pointer-events-none absolute z-20 w-72 rounded border border-forge-amber/50 bg-forge-bg/95 p-3 shadow-2xl"
              style={{ left: Math.min(tx, containerSize.w - 296), top: Math.max(4, ty) }}
            >
              <div className="font-display text-sm font-bold text-forge-amber leading-tight">
                {cleanNodeName(n.name) || "Node"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                {isRoot ? "Skill Entry — auto-granted" : `${n.type} · ${pts}/${max} pts`}
              </div>
              {flavorText && (
                <div className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text/90">
                  {flavorText}
                </div>
              )}
              {statEntries.length > 0 && (
                <div className="mt-2 border-t border-forge-border/50 pt-1.5 flex flex-col gap-0.5">
                  {statEntries.map((entry, i) => {
                    const isDownside = entry.toLowerCase().includes("(downside)");
                    const display = entry.replace(/\s*\(downside\)\s*/i, "").trim();
                    return (
                      <div key={i} className="font-mono text-[10px] flex justify-between gap-2">
                        <span className={isDownside ? "text-red-400/80" : "text-forge-dim"}>{display}</span>
                        {isDownside && <span className="text-red-400/60 text-[9px] shrink-0">penalty</span>}
                      </div>
                    );
                  })}
                  {max > 1 && (
                    <div className="mt-1 font-mono text-[9px] text-forge-dim/60 italic">
                      Values shown are per point ({max} pts max)
                    </div>
                  )}
                </div>
              )}
              {!readOnly && locked && !isRoot && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">
                  ⚠ Requires parent node(s)
                </div>
              )}
              {!readOnly && !locked && !isRoot && pts < max && pointsLeft === 0 && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">No skill points remaining</div>
              )}
            </div>
          );
        })()}
      </div>

      {/* Footer legend */}
      <div className="flex flex-wrap items-center gap-4 border-t border-forge-border px-3 py-1.5 text-[10px] font-mono text-forge-dim bg-forge-surface2 shrink-0">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#342010] border border-[#7a3010]" />
          Entry
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#28201a] border border-[#5a4a28]" />
          Core
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-[#1a1e2e] border border-[#3a5a90]" />
          Notable
        </span>
        {!readOnly && (
          <span className="ml-auto">Left-click invest · Right-click refund</span>
        )}
      </div>
    </div>
  );
}
