/**
 * SkillTreeRenderer — SVG-based skill tree node graph from API data.
 *
 * Renders the community_skill_trees data (with transform.x/y, requirements, stats).
 * Nodes are hexagons (core) or diamonds (notable/scale>=1.2). Root is larger.
 * Pan & zoom via viewBox transforms. Click to allocate, right-click to deallocate.
 */

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { clsx } from "clsx";
import type { SkillNode, SkillNodeRequirement } from "@/types";
import TreeIcon from "@/components/TreeIcon";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DISPLAY_H = 520;
const MAX_SKILL_POINTS = 20;

const BASE_NODE_R = 22;
const ROOT_NODE_R = 34;
const NOTABLE_NODE_R = 28;

// ---------------------------------------------------------------------------
// Shape helpers
// ---------------------------------------------------------------------------

function hexPoints(r: number): string {
  return Array.from({ length: 6 }, (_, i) => {
    const a = (i * 60) * Math.PI / 180;
    return `${(Math.cos(a) * r).toFixed(2)},${(Math.sin(a) * r).toFixed(2)}`;
  }).join(" ");
}

function diamondPoints(r: number): string {
  return `0,${-r} ${r},0 0,${r} ${-r},0`;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AllocMap {
  [nodeId: number]: number;
}

interface Props {
  nodes: SkillNode[];
  rootNodeId: number;
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
// Node classification
// ---------------------------------------------------------------------------

function getNodeType(node: SkillNode, rootId: number): "root" | "notable" | "core" {
  if (node.id === rootId) return "root";
  const s = node.transform?.scale ?? 1;
  if (s >= 1.2 || node.maxPoints === 1) return "notable";
  return "core";
}

function getNodeR(type: "root" | "notable" | "core"): number {
  if (type === "root") return ROOT_NODE_R;
  if (type === "notable") return NOTABLE_NODE_R;
  return BASE_NODE_R;
}

// ---------------------------------------------------------------------------
// Layout — center nodes around midpoint
// ---------------------------------------------------------------------------

interface LayoutNode extends SkillNode {
  lx: number;
  ly: number;
  nodeType: "root" | "notable" | "core";
}

function toLayoutNodes(nodes: SkillNode[], rootId: number): LayoutNode[] {
  if (nodes.length === 0) return [];
  const xs = nodes.map(n => n.transform?.x ?? 0);
  const ys = nodes.map(n => n.transform?.y ?? 0);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  return nodes.map(n => ({
    ...n,
    lx: (n.transform?.x ?? 0) - midX,
    ly: (n.transform?.y ?? 0) - midY,
    nodeType: getNodeType(n, rootId),
  }));
}

// ---------------------------------------------------------------------------
// BFS reachability (mirrors backend logic)
// ---------------------------------------------------------------------------

function isReachable(
  nodeId: number,
  nodeMap: Map<number, SkillNode>,
  allocated: AllocMap,
  rootId: number,
  visited: Set<number> = new Set(),
): boolean {
  if (visited.has(nodeId)) return false;
  visited.add(nodeId);

  const node = nodeMap.get(nodeId);
  if (!node) return false;

  // Root node is always reachable
  if (node.id === rootId) return true;

  const reqs = node.requirements ?? [];
  if (reqs.length === 0) return node.maxPoints === 0;

  for (const req of reqs) {
    const reqId = req.node;
    const reqPts = req.requirement ?? 0;
    const pts = reqId === rootId ? 1 : (allocated[reqId] ?? 0);
    if (pts < Math.max(reqPts, 1)) return false;
    if (!isReachable(reqId, nodeMap, allocated, rootId, new Set(visited))) return false;
  }
  return true;
}

function hasAllocatedDependent(
  nodeId: number,
  nodes: SkillNode[],
  allocated: AllocMap,
): boolean {
  for (const node of nodes) {
    if ((allocated[node.id] ?? 0) <= 0) continue;
    for (const req of node.requirements ?? []) {
      if (req.node === nodeId) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------------------
// SkillTreeRenderer
// ---------------------------------------------------------------------------

export default function SkillTreeRenderer({
  nodes,
  rootNodeId,
  allocated,
  onAllocate,
  readOnly,
  skillName,
}: Props) {
  const layoutNodes = useMemo(() => toLayoutNodes(nodes, rootNodeId), [nodes, rootNodeId]);
  const byId = useMemo(
    () => new Map(layoutNodes.map(n => [n.id, n as SkillNode])),
    [layoutNodes],
  );

  // Auto-allocate root
  const effectiveAllocated = useMemo(() => {
    const map = { ...allocated };
    map[rootNodeId] = 1;
    return map;
  }, [allocated, rootNodeId]);

  const totalPoints = Object.entries(effectiveAllocated).reduce((s, [id, v]) => {
    if (Number(id) === rootNodeId) return s;
    return s + v;
  }, 0);
  const pointsLeft = MAX_SKILL_POINTS - totalPoints;

  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);
  const [containerSize, setContainerSize] = useState({ w: 800, h: DISPLAY_H });

  // Pan & zoom state
  const [viewBox, setViewBox] = useState({ x: 0, y: 0, w: 800, h: DISPLAY_H });
  const [isPanning, setIsPanning] = useState(false);
  const panStart = useRef({ x: 0, y: 0, vx: 0, vy: 0 });

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

  // Auto-fit viewBox to contain all nodes
  useEffect(() => {
    if (layoutNodes.length === 0) return;
    const pad = 60;
    const xs = layoutNodes.map(n => n.lx);
    const ys = layoutNodes.map(n => n.ly);
    const minX = Math.min(...xs) - pad;
    const maxX = Math.max(...xs) + pad;
    const minY = Math.min(...ys) - pad;
    const maxY = Math.max(...ys) + pad;
    const w = maxX - minX || 1;
    const h = maxY - minY || 1;
    // Fit while maintaining aspect ratio
    const aspect = containerSize.w / containerSize.h;
    const treeAspect = w / h;
    let vw: number, vh: number;
    if (treeAspect > aspect) {
      vw = w;
      vh = w / aspect;
    } else {
      vh = h;
      vw = h * aspect;
    }
    setViewBox({
      x: (minX + maxX) / 2 - vw / 2,
      y: (minY + maxY) / 2 - vh / 2,
      w: vw,
      h: vh,
    });
  }, [layoutNodes, containerSize]);

  // Zoom with mouse wheel
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 1.1 : 0.9;
    setViewBox(vb => {
      const nw = vb.w * factor;
      const nh = vb.h * factor;
      return {
        x: vb.x + (vb.w - nw) / 2,
        y: vb.y + (vb.h - nh) / 2,
        w: nw,
        h: nh,
      };
    });
  }, []);

  // Pan with mouse drag
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    panStart.current = { x: e.clientX, y: e.clientY, vx: viewBox.x, vy: viewBox.y };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  }, [viewBox]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isPanning) return;
    const dx = e.clientX - panStart.current.x;
    const dy = e.clientY - panStart.current.y;
    const scale = viewBox.w / containerSize.w;
    setViewBox(vb => ({
      ...vb,
      x: panStart.current.vx - dx * scale,
      y: panStart.current.vy - dy * scale,
    }));
  }, [isPanning, viewBox.w, containerSize.w]);

  const handlePointerUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Scale for node sizes relative to viewBox
  const nodeScale = viewBox.w / containerSize.w;

  const handleAllocateNode = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.stopPropagation();
    if (node.id === rootNodeId) return;
    const pts = effectiveAllocated[node.id] ?? 0;
    const max = node.maxPoints ?? 1;
    if (pts < max && isReachable(node.id, byId, effectiveAllocated, rootNodeId) && pointsLeft > 0) {
      onAllocate(node.id, pts + 1);
    }
  };

  const handleDeallocateNode = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.preventDefault();
    e.stopPropagation();
    if (node.id === rootNodeId) return;
    const pts = effectiveAllocated[node.id] ?? 0;
    if (pts <= 0) return;
    if (!hasAllocatedDependent(node.id, nodes, effectiveAllocated)) {
      onAllocate(node.id, pts - 1);
    }
  };

  // Build edges from requirements
  const edges = useMemo(() => {
    const result: { from: number; to: number }[] = [];
    for (const node of layoutNodes) {
      for (const req of node.requirements ?? []) {
        if (byId.has(req.node)) {
          result.push({ from: req.node, to: node.id });
        }
      }
    }
    return result;
  }, [layoutNodes, byId]);

  if (!nodes.length) {
    return (
      <div
        className="flex items-center justify-center rounded border border-forge-border bg-forge-surface"
        style={{ height: DISPLAY_H, background: "#0b0e1a" }}
      >
        <p className="font-mono text-sm text-forge-dim">No skill tree data available.</p>
      </div>
    );
  }

  const vbStr = `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`;

  return (
    <div className="flex flex-col gap-0 rounded border border-forge-border bg-forge-surface overflow-hidden">
      {/* Point budget bar */}
      <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-3 py-1.5 shrink-0">
        <div className="flex items-center gap-3 font-mono text-[10px]">
          {skillName && (
            <span className="text-forge-amber font-bold uppercase tracking-widest">{skillName}</span>
          )}
          <span className="text-forge-dim uppercase tracking-widest">Skill Points</span>
          <span className={clsx("font-bold", totalPoints > 0 ? "text-forge-amber" : "text-forge-dim")}>
            {totalPoints} spent
          </span>
          <span className="text-forge-dim">/</span>
          <span className={clsx("font-bold", pointsLeft < 3 ? "text-red-400" : "text-forge-text")}>
            {pointsLeft} remaining
          </span>
        </div>
      </div>

      {/* SVG canvas */}
      <div
        ref={containerRef}
        className="relative overflow-hidden select-none"
        style={{ height: DISPLAY_H, background: "#0b0e1a", cursor: isPanning ? "grabbing" : "grab" }}
        onWheel={handleWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
      >
        <svg
          width={containerSize.w}
          height={containerSize.h}
          viewBox={vbStr}
          style={{ display: "block", position: "absolute", inset: 0 }}
        >
          <defs>
            <filter id="str-stone" x="0%" y="0%" width="100%" height="100%">
              <feTurbulence type="fractalNoise" baseFrequency="0.65 0.45" numOctaves="4" seed="8" stitchTiles="stitch" result="noise"/>
              <feColorMatrix type="matrix" result="tinted"
                values="0.06 0 0 0 0.04   0 0.04 0 0 0.02   0 0 0.03 0 0.01   0 0 0 0.35 0"/>
              <feComposite in="tinted" in2="SourceGraphic" operator="over"/>
            </filter>
            <filter id="str-glow" x="-80%" y="-80%" width="260%" height="260%">
              <feGaussianBlur stdDeviation="5" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="str-line-glow" x="-20%" y="-300%" width="140%" height="700%">
              <feGaussianBlur stdDeviation="2" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <radialGradient id="str-vignette" cx="50%" cy="50%" r="70%">
              <stop offset="0%" stopColor="transparent"/>
              <stop offset="100%" stopColor="#000000" stopOpacity="0.55"/>
            </radialGradient>
            <radialGradient id="str-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#3a3228"/><stop offset="100%" stopColor="#1a1410"/>
            </radialGradient>
            <radialGradient id="str-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#e8c060"/><stop offset="60%" stopColor="#c8902a"/><stop offset="100%" stopColor="#7a5010"/>
            </radialGradient>
            <radialGradient id="str-notable-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#2a2e40"/><stop offset="100%" stopColor="#141620"/>
            </radialGradient>
            <radialGradient id="str-notable-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#90c0f0"/><stop offset="60%" stopColor="#4a80c0"/><stop offset="100%" stopColor="#1a3060"/>
            </radialGradient>
            <radialGradient id="str-root-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#342010"/><stop offset="100%" stopColor="#1a1008"/>
            </radialGradient>
            <radialGradient id="str-root-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#ffa060"/><stop offset="60%" stopColor="#d04020"/><stop offset="100%" stopColor="#701008"/>
            </radialGradient>
          </defs>

          <rect x={viewBox.x} y={viewBox.y} width={viewBox.w} height={viewBox.h} fill="#0b0e1a"/>
          <rect x={viewBox.x} y={viewBox.y} width={viewBox.w} height={viewBox.h} filter="url(#str-stone)" fill="#0b0e1a"/>
          <rect x={viewBox.x} y={viewBox.y} width={viewBox.w} height={viewBox.h} fill="url(#str-vignette)"/>

          {/* Edges */}
          <g>
            {edges.map(({ from, to }) => {
              const fn = layoutNodes.find(n => n.id === from);
              const tn = layoutNodes.find(n => n.id === to);
              if (!fn || !tn) return null;
              const bothActive = (effectiveAllocated[from] ?? 0) >= 1 && (effectiveAllocated[to] ?? 0) >= 1;
              const toReachable = isReachable(to, byId, effectiveAllocated, rootNodeId);
              const sw = nodeScale * (bothActive ? 3 : 2);
              return (
                <line key={`e-${from}-${to}`}
                  x1={fn.lx} y1={fn.ly} x2={tn.lx} y2={tn.ly}
                  stroke={bothActive ? "#c8902a" : toReachable ? "#7a6a40" : "#3a3020"}
                  strokeWidth={sw}
                  opacity={bothActive ? 1 : toReachable ? 0.8 : 0.4}
                  filter={bothActive ? "url(#str-line-glow)" : undefined}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {layoutNodes.map(node => {
              const isRoot = node.id === rootNodeId;
              const nType = node.nodeType;
              const r = getNodeR(nType);
              const outerR = r + 4;
              const max = node.maxPoints ?? 1;
              const pts = effectiveAllocated[node.id] ?? 0;
              const active = pts >= 1;
              const reachable = isReachable(node.id, byId, effectiveAllocated, rootNodeId);

              let fillGrad = active ? "url(#str-active)" : "url(#str-idle)";
              if (nType === "notable") fillGrad = active ? "url(#str-notable-active)" : "url(#str-notable-idle)";
              else if (nType === "root") fillGrad = active ? "url(#str-root-active)" : "url(#str-root-idle)";

              const borderCol = active
                ? (nType === "notable" ? "#70a8e0" : nType === "root" ? "#d06030" : "#d4a030")
                : reachable
                  ? (nType === "notable" ? "#3a5080" : nType === "root" ? "#7a3010" : "#5a4820")
                  : "#1e1a12";

              const isNotableShape = nType === "notable";
              const shapePts = isNotableShape ? diamondPoints(r) : hexPoints(r);
              const outerShapePts = isNotableShape ? diamondPoints(outerR) : hexPoints(outerR);
              const innerPts = isNotableShape ? diamondPoints(r * 0.72) : hexPoints(r * 0.72);
              const fontSize = 11;
              const labelSize = 9;

              return (
                <g key={node.id}
                  transform={`translate(${node.lx},${node.ly})`}
                  opacity={reachable || active ? 1 : 0.22}
                  style={{ cursor: readOnly || isRoot ? "default" : reachable ? "pointer" : "not-allowed" }}
                  onClick={e => handleAllocateNode(node, e)}
                  onContextMenu={e => handleDeallocateNode(node, e)}
                  onMouseEnter={e => setTooltip({ node, screenX: e.clientX, screenY: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, screenX: e.clientX, screenY: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {active && <polygon points={outerShapePts} fill={borderCol} opacity={0.22} filter="url(#str-glow)"/>}
                  <polygon points={outerShapePts} fill="none" stroke={borderCol} strokeWidth={active ? 2 : 1} opacity={active ? 0.9 : 0.45}/>
                  <polygon points={shapePts} fill={fillGrad}/>
                  <polygon points={innerPts} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>

                  {/* Node icon from sprite sheet */}
                  <TreeIcon
                    iconId={node.icon != null ? String(node.icon) : null}
                    size={r * 1.6}
                    nodeName={node.name}
                  />

                  {/* Point counter (skip for root) */}
                  {!isRoot && (
                    <text
                      y={outerR + fontSize * 0.3}
                      textAnchor="middle"
                      fontSize={fontSize}
                      fill={active ? "#d4a030" : reachable ? "#6a5c40" : "#3a3020"}
                      fontFamily="monospace"
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {pts}/{max}
                    </text>
                  )}

                  {/* Name label for notable + root */}
                  {node.name && (nType === "notable" || nType === "root") && (
                    <text
                      y={isRoot ? outerR + fontSize * 0.3 : outerR + fontSize * 0.3 + labelSize + 2}
                      textAnchor="middle"
                      fontSize={labelSize}
                      fill={active ? "#e8c060" : reachable ? "#8a7a58" : "#3a3020"}
                      fontFamily="serif"
                      fontStyle="italic"
                      pointerEvents="none"
                    >
                      {node.name.length > 20 ? node.name.slice(0, 19) + "\u2026" : node.name}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Tooltip overlay */}
        {tooltip && (() => {
          const n = tooltip.node;
          const isRoot = n.id === rootNodeId;
          const max = n.maxPoints ?? 1;
          const pts = effectiveAllocated[n.id] ?? 0;
          const locked = !isReachable(n.id, byId, effectiveAllocated, rootNodeId);
          const containerRect = containerRef.current?.getBoundingClientRect();
          if (!containerRect) return null;

          let tx = tooltip.screenX - containerRect.left + 16;
          let ty = tooltip.screenY - containerRect.top - 12;
          // Flip if too close to right/bottom edge
          if (tx + 296 > containerSize.w) tx = tooltip.screenX - containerRect.left - 312;
          if (ty + 200 > containerSize.h) ty = Math.max(4, containerSize.h - 200);
          ty = Math.max(4, ty);

          const stats = n.stats ?? [];

          return (
            <div
              className="pointer-events-none absolute z-20 w-72 rounded border border-forge-amber/50 bg-forge-bg/95 p-3 shadow-2xl"
              style={{ left: tx, top: ty }}
            >
              <div className="font-display text-sm font-bold text-forge-amber leading-tight">
                {n.name || "Node"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                {isRoot ? "Skill Entry \u2014 auto-granted" : `${getNodeType(n, rootNodeId)} \u00b7 ${pts}/${max} pts`}
              </div>
              {n.description && (
                <div className="mt-1.5 font-body text-[11px] leading-relaxed text-forge-text/90">
                  {n.description}
                </div>
              )}
              {stats.length > 0 && (
                <div className="mt-2 border-t border-forge-border/50 pt-1.5 flex flex-col gap-0.5">
                  {stats.map((stat, i) => (
                    <div key={i} className="font-mono text-[10px] flex justify-between gap-2">
                      <span className={stat.downside ? "text-red-400/80" : "text-forge-dim"}>
                        {stat.statName}: {stat.value}
                      </span>
                      {stat.downside && <span className="text-red-400/60 text-[9px] shrink-0">penalty</span>}
                    </div>
                  ))}
                  {max > 1 && (
                    <div className="mt-1 font-mono text-[9px] text-forge-dim/60 italic">
                      Per point ({max} pts max)
                    </div>
                  )}
                </div>
              )}
              {!readOnly && locked && !isRoot && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">Requires parent node(s)</div>
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
          <span className="inline-block h-2.5 w-2.5" style={{ transform: "rotate(45deg)", background: "#1a1e2e", border: "1px solid #3a5a90" }} />
          Notable
        </span>
        {!readOnly && (
          <span className="ml-auto">Left-click invest \u00b7 Right-click refund \u00b7 Scroll zoom \u00b7 Drag pan</span>
        )}
      </div>
    </div>
  );
}
