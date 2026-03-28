import { useState, useMemo, useRef, useEffect } from "react";
import { clsx } from "clsx";
import type { PassiveNode } from "@/lib/gameData";
import { PASSIVE_TREES } from "@/data/passiveTrees";
import { PASSIVE_TREE_META } from "@/data/passiveTrees/edges";
import iconSpriteMap from "@/data/iconSpriteMap.json";
import { fetchClassTree } from "@/services/passiveTreeService";
import type { PassiveNode as ApiPassiveNode } from "@/services/passiveTreeService";

// Sprite sheet from lastepochtools CDN
const SPRITE_URL =
  "https://www.lastepochtools.com/data/version140/planner/res/d285216918221e26ef5d5b32f3407c4a.webp";
const SPRITE_ICON_SIZE = 64;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const NODE_R: Record<string, number> = {
  core: 18,
  notable: 24,
  keystone: 32,
  "mastery-gate": 22,
};

// Last Epoch mastery mechanics:
//   • All mastery trees unlock once 20 points are spent in the BASE tree
//     (handled automatically by masteryRequirement = 20 on mastery nodes in edges.ts)
//   • Cross-mastery investment is allowed, BUT:
//     once your PRIMARY mastery has >= CHAIN_THRESHOLD points, you are "chained"
//     and nodes deeper than SECONDARY_MASTERY_DEPTH in other masteries become locked
const CHAIN_THRESHOLD = 20;       // primary mastery points that triggers the chain
const SECONDARY_MASTERY_DEPTH = 20; // masteryRequirement >= this is "deep" in a secondary mastery

// Flat-top hexagon points at radius r
function hexPoints(r: number): string {
  return Array.from({ length: 6 }, (_, i) => {
    const a = (i * 60) * Math.PI / 180; // flat-top: 0°,60°,120°,...
    return `${(Math.cos(a) * r).toFixed(2)},${(Math.sin(a) * r).toFixed(2)}`;
  }).join(" ");
}

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

// Maximum passive points per class
const MAX_PASSIVE_POINTS = 113;

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

const DISPLAY_H = 580;

// ---------------------------------------------------------------------------
// Layout — use real game x,y, centered around the canvas midpoint
// ---------------------------------------------------------------------------
interface LayoutNode extends PassiveNode {
  lx: number;
  ly: number;
}

function toLayoutNodes(nodes: PassiveNode[]): LayoutNode[] {
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

  // Normalize mastery name to region key (e.g. "Forge Guard" → "forge-guard")
  const chosenMasteryRegion = mastery ? mastery.toLowerCase().replace(/\s+/g, '-') : '';

  const [activeRegion, setActiveRegion] = useState(regionKeys.includes("base") ? "base" : (regionKeys[0] ?? "base"));

  // Reset to base tree when class changes
  useEffect(() => {
    const keys = Object.keys(PASSIVE_TREES[cls] ?? {});
    setActiveRegion(keys.includes("base") ? "base" : (keys[0] ?? "base"));
  }, [cls]);

  // Fetch full node data (with stats) from API; keyed by raw_node_id for tooltip lookup
  const [apiNodeMap, setApiNodeMap] = useState<Map<number, ApiPassiveNode>>(new Map());
  useEffect(() => {
    if (!characterClass) return;
    fetchClassTree(characterClass)
      .then(res => {
        const map = new Map<number, ApiPassiveNode>();
        for (const node of res.nodes) {
          map.set(node.raw_node_id, node);
        }
        setApiNodeMap(map);
      })
      .catch(() => {/* silently fail — tooltip just won't show stats */});
  }, [characterClass]);

  const rawNodes: PassiveNode[] = useMemo(
    () => regionMap[activeRegion] ?? [],
    [regionMap, activeRegion]
  );

  const layoutNodes = useMemo(() => toLayoutNodes(rawNodes), [rawNodes]);

  const byId = useMemo(
    () => new Map(layoutNodes.map(n => [n.id, n])),
    [layoutNodes]
  );

  // Build edge list for the current region
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

  // Points spent exclusively in the primary (chosen) mastery region
  const primaryMasterySpent = useMemo(() => {
    if (!chosenMasteryRegion) return 0;
    return Object.entries(allocated).reduce((sum, [nodeIdStr, pts]) => {
      const meta = classMeta[Number(nodeIdStr)];
      return meta?.region === chosenMasteryRegion ? sum + pts : sum;
    }, 0);
  }, [allocated, classMeta, chosenMasteryRegion]);

  // Chain is active once you've committed >= CHAIN_THRESHOLD points to primary mastery
  const isChained = primaryMasterySpent >= CHAIN_THRESHOLD;

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

  // Compute scale + offset to fit all nodes inside the container with padding
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

  // World→screen using auto-fit transform
  const worldToScreen = (lx: number, ly: number) => ({
    sx: lx * scale + offsetX,
    sy: ly * scale + offsetY,
  });

  // Effective node radius scaled to fit
  const scaledR = (base: number) => Math.max(4, base * scale);

  // Unlock check implements Last Epoch mastery rules:
  //   1. Base tree always accessible
  //   2. Mastery trees unlock after 20 base points (handled by masteryRequirement in edges.ts)
  //   3. ALL mastery trees are accessible — cross-mastery investment is allowed
  //   4. CHAIN: once primary mastery has >= CHAIN_THRESHOLD pts, deep nodes
  //      (masteryRequirement >= SECONDARY_MASTERY_DEPTH) in OTHER masteries are locked
  //   5. Parent nodes must be allocated
  const isUnlocked = (nodeId: number): boolean => {
    const meta = classMeta[nodeId];
    if (!meta) return true;
    const isSecondaryMastery = chosenMasteryRegion
      && meta.region !== 'base'
      && meta.region !== chosenMasteryRegion;
    // Chain: deep secondary mastery nodes lock once primary mastery is committed
    if (isSecondaryMastery && isChained && meta.masteryRequirement >= SECONDARY_MASTERY_DEPTH) return false;
    if (totalSpent < meta.masteryRequirement) return false;
    return meta.parentIds.every(pid => (allocated[pid] ?? 0) >= 1);
  };

  // Whether the currently-viewed region is a secondary mastery (not base, not chosen)
  const isSecondaryRegion = !!chosenMasteryRegion
    && activeRegion !== 'base'
    && activeRegion !== chosenMasteryRegion;

  const handleAllocate = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.stopPropagation();
    const pts = allocated[node.id] ?? 0;
    const max = node.maxPoints ?? 1;
    if (pts < max && isUnlocked(node.id) && pointsLeft > 0) {
      onAllocate(node.id, pts + 1);
    }
  };

  const handleDeallocate = (node: LayoutNode, e: React.MouseEvent) => {
    if (readOnly) return;
    e.preventDefault();
    e.stopPropagation();
    const pts = allocated[node.id] ?? 0;
    if (pts <= 0) return;
    const hasAllocatedChild = layoutNodes.some(n => {
      const m = classMeta[n.id];
      return m && m.parentIds.includes(node.id) && (allocated[n.id] ?? 0) >= 1;
    });
    if (!hasAllocatedChild) onAllocate(node.id, pts - 1);
  };

  const regionPoints = layoutNodes.reduce((s, n) => s + (allocated[n.id] ?? 0), 0);

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
          const isBase = key === 'base';
          const isPrimary = !isBase && key === chosenMasteryRegion;
          const isSecondary = !isBase && !!chosenMasteryRegion && !isPrimary;
          return (
            <button
              key={key}
              onClick={() => setActiveRegion(key)}
              title={isSecondary && isChained ? `Secondary mastery — deep nodes locked (chain active at ${CHAIN_THRESHOLD} primary pts)` : undefined}
              className={clsx(
                "flex items-center gap-1 px-4 py-2 font-mono text-[10px] uppercase tracking-widest whitespace-nowrap border-r border-forge-border transition-colors shrink-0",
                activeRegion === key
                  ? isPrimary
                    ? "bg-forge-bg text-amber-300"
                    : "bg-forge-bg text-forge-amber"
                  : isSecondary
                    ? "text-forge-dim/60 hover:text-forge-text"
                    : "text-forge-dim hover:text-forge-text"
              )}
            >
              {isPrimary && <span className="text-amber-400">⬡</span>}
              {isSecondary && isChained && <span className="opacity-60" title="Chain active">⛓</span>}
              {REGION_LABELS[key] ?? key}
              {pts > 0 && <span className="ml-1.5 text-forge-amber opacity-80">{pts}</span>}
            </button>
          );
        })}
        <div className="ml-auto flex items-center px-3 font-mono text-[10px] text-forge-dim whitespace-nowrap">
          {layoutNodes.length} nodes · {edges.length} connections
        </div>
      </div>

      {/* Mastery indicator banner */}
      {chosenMasteryRegion && (
        <div className="flex items-center gap-3 border-b border-forge-border bg-forge-bg/60 px-3 py-1 shrink-0">
          <span className="font-mono text-[9px] uppercase tracking-widest text-forge-dim">Primary Mastery</span>
          <span className="font-mono text-[10px] font-bold text-amber-400">⬡ {mastery}</span>
          <span className="font-mono text-[9px] text-forge-dim">
            {primaryMasterySpent} / {CHAIN_THRESHOLD} pts
          </span>
          {isChained ? (
            <span className="ml-auto font-mono text-[9px] text-orange-400/80">
              ⛓ Chained — deep nodes in secondary masteries locked
            </span>
          ) : (
            <span className="ml-auto font-mono text-[9px] text-forge-dim/50">
              Cross-mastery allowed · chain at {CHAIN_THRESHOLD} primary pts
            </span>
          )}
          {isSecondaryRegion && (
            <span className="font-mono text-[9px] text-forge-dim/70 border-l border-forge-border/50 pl-3">
              Secondary tree — {isChained ? "shallow nodes only" : "all nodes accessible"}
            </span>
          )}
        </div>
      )}

      {/* SVG canvas — static, auto-fit */}
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
            <filter id="stone-texture" x="0%" y="0%" width="100%" height="100%">
              <feTurbulence type="fractalNoise" baseFrequency="0.65 0.45" numOctaves="4" seed="8" stitchTiles="stitch" result="noise"/>
              <feColorMatrix type="matrix" result="tinted"
                values="0.06 0 0 0 0.04   0 0.04 0 0 0.02   0 0 0.03 0 0.01   0 0 0 0.35 0"/>
              <feComposite in="tinted" in2="SourceGraphic" operator="over"/>
            </filter>
            <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
              <feGaussianBlur stdDeviation="5" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="line-glow" x="-20%" y="-300%" width="140%" height="700%">
              <feGaussianBlur stdDeviation="2" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
              <stop offset="0%" stopColor="transparent"/>
              <stop offset="100%" stopColor="#000000" stopOpacity="0.55"/>
            </radialGradient>
            <radialGradient id="node-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#3a3228"/><stop offset="100%" stopColor="#1a1410"/>
            </radialGradient>
            <radialGradient id="node-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#e8c060"/><stop offset="60%" stopColor="#c8902a"/><stop offset="100%" stopColor="#7a5010"/>
            </radialGradient>
            <radialGradient id="node-notable-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#2a2e40"/><stop offset="100%" stopColor="#141620"/>
            </radialGradient>
            <radialGradient id="node-notable-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#90c0f0"/><stop offset="60%" stopColor="#4a80c0"/><stop offset="100%" stopColor="#1a3060"/>
            </radialGradient>
            <radialGradient id="node-keystone-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#1e3020"/><stop offset="100%" stopColor="#0e1810"/>
            </radialGradient>
            <radialGradient id="node-keystone-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#80f090"/><stop offset="60%" stopColor="#30a040"/><stop offset="100%" stopColor="#104020"/>
            </radialGradient>
            <radialGradient id="node-gate-idle" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#342010"/><stop offset="100%" stopColor="#1a1008"/>
            </radialGradient>
            <radialGradient id="node-gate-active" cx="35%" cy="30%" r="65%">
              <stop offset="0%" stopColor="#ffa060"/><stop offset="60%" stopColor="#d04020"/><stop offset="100%" stopColor="#701008"/>
            </radialGradient>
          </defs>

          <rect width={containerSize.w} height={containerSize.h} fill="#0b0e1a"/>
          <rect width={containerSize.w} height={containerSize.h} filter="url(#stone-texture)" fill="#0b0e1a"/>
          <rect width={containerSize.w} height={containerSize.h} fill="url(#vignette)"/>

          {/* Edges */}
          <g>
            {edges.map(({ from, to }) => {
              const fromNode = byId.get(from);
              const toNode = byId.get(to);
              if (!fromNode || !toNode) return null;
              const bothActive = (allocated[from] ?? 0) >= 1 && (allocated[to] ?? 0) >= 1;
              const toUnlocked = isUnlocked(to);
              const { sx: x1, sy: y1 } = worldToScreen(fromNode.lx, fromNode.ly);
              const { sx: x2, sy: y2 } = worldToScreen(toNode.lx, toNode.ly);
              return (
                <line key={`e-${from}-${to}`}
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  stroke={bothActive ? "#c8902a" : toUnlocked ? "#7a6a40" : "#3a3020"}
                  strokeWidth={bothActive ? Math.max(2, 3 * scale) : Math.max(1, 2 * scale)}
                  opacity={bothActive ? 1 : toUnlocked ? 0.8 : 0.4}
                  filter={bothActive ? "url(#line-glow)" : undefined}
                />
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {layoutNodes.map(node => {
              const type = node.type ?? "core";
              const r = scaledR(NODE_R[type] ?? 18);
              const outerR = r + Math.max(2, 4 * scale);
              const max = node.maxPoints ?? 1;
              const pts = allocated[node.id] ?? 0;
              const active = pts >= 1;
              const unlocked = isUnlocked(node.id);
              const { sx: scx, sy: scy } = worldToScreen(node.lx, node.ly);

              let fillGrad = active ? "url(#node-active)" : "url(#node-idle)";
              if (type === "notable")           fillGrad = active ? "url(#node-notable-active)" : "url(#node-notable-idle)";
              else if (type === "keystone")     fillGrad = active ? "url(#node-keystone-active)" : "url(#node-keystone-idle)";
              else if (type === "mastery-gate") fillGrad = active ? "url(#node-gate-active)" : "url(#node-gate-idle)";

              const borderCol = active
                ? (type === "notable" ? "#70a8e0" : type === "keystone" ? "#50c060" : type === "mastery-gate" ? "#d06030" : "#d4a030")
                : unlocked
                  ? (type === "notable" ? "#3a5080" : type === "keystone" ? "#2a5a30" : type === "mastery-gate" ? "#7a3010" : "#5a4820")
                  : "#1e1a12";

              const hexPts = hexPoints(r);
              const outerPts = hexPoints(outerR);
              const fontSize = Math.max(7, 11 * scale);
              const labelSize = Math.max(6, 9 * scale);

              return (
                <g key={node.id}
                  transform={`translate(${scx},${scy})`}
                  opacity={unlocked || active ? 1 : 0.22}
                  style={{ cursor: readOnly ? "default" : unlocked ? "pointer" : "not-allowed" }}
                  onClick={e => handleAllocate(node, e)}
                  onContextMenu={e => handleDeallocate(node, e)}
                  onMouseEnter={e => setTooltip({ node, screenX: e.clientX, screenY: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, screenX: e.clientX, screenY: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {active && <polygon points={outerPts} fill={borderCol} opacity={0.22} filter="url(#glow)"/>}
                  <polygon points={outerPts} fill="none" stroke={borderCol} strokeWidth={active ? 2 : 1} opacity={active ? 0.9 : 0.45}/>
                  <polygon points={hexPts} fill={fillGrad}/>
                  <polygon points={hexPoints(r * 0.72)} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>

                  {/* Node icon from sprite sheet */}
                  <SpriteIcon iconId={node.iconId} size={r * 1.6} />

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

                  {node.name && (type === "notable" || type === "keystone") && scale >= 0.35 && (
                    <text
                      y={outerR + fontSize * 0.3 + labelSize + 2}
                      textAnchor="middle"
                      fontSize={labelSize}
                      fill={active ? "#e8c060" : unlocked ? "#8a7a58" : "#3a3020"}
                      fontFamily="serif"
                      fontStyle="italic"
                      pointerEvents="none"
                    >
                      {node.name.length > 20 ? node.name.slice(0, 19) + "…" : node.name}
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
          const max = n.maxPoints ?? 1;
          const pts = allocated[n.id] ?? 0;
          const nodeMeta = classMeta[n.id];
          const mr = nodeMeta?.masteryRequirement ?? 0;
          const locked = !isUnlocked(n.id);
          const apiNode = apiNodeMap.get(n.id);
          const containerRect = containerRef.current?.getBoundingClientRect();
          if (!containerRect) return null;
          const tx = tooltip.screenX - containerRect.left + 16;
          const ty = tooltip.screenY - containerRect.top - 12;
          return (
            <div
              className="pointer-events-none absolute z-20 w-72 rounded border border-forge-amber/50 bg-forge-bg/95 p-3 shadow-2xl"
              style={{ left: Math.min(tx, containerSize.w - 296), top: Math.max(4, ty) }}
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
              {apiNode?.stats && apiNode.stats.length > 0 && (
                <div className="mt-2 border-t border-forge-border/50 pt-1.5 flex flex-col gap-0.5">
                  {apiNode.stats.map((s, i) => (
                    <div key={i} className="flex justify-between font-mono text-[10px]">
                      <span className="text-forge-dim">{s.key}</span>
                      <span className="text-forge-amber ml-2 shrink-0">{s.value}</span>
                    </div>
                  ))}
                </div>
              )}
              {apiNode?.ability_granted && (
                <div className="mt-1.5 font-mono text-[10px] text-forge-text/70">
                  ✦ Grants: <span className="text-forge-amber">{apiNode.ability_granted}</span>
                </div>
              )}
              {mr > 0 && (
                <div className={clsx("mt-1.5 font-mono text-[10px]", totalSpent >= mr ? "text-forge-dim" : "text-yellow-400/80")}>
                  ⬡ Requires {mr} total points ({totalSpent}/{mr})
                </div>
              )}
              {!readOnly && locked && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">
                  ⚠ {(() => {
                    const nodeMeta2 = classMeta[n.id];
                    const isSecMastery = nodeMeta2?.region && nodeMeta2.region !== 'base'
                      && chosenMasteryRegion && nodeMeta2.region !== chosenMasteryRegion;
                    if (isSecMastery && isChained && (nodeMeta2?.masteryRequirement ?? 0) >= SECONDARY_MASTERY_DEPTH)
                      return `⛓ Chained — invest more in ${mastery} first to unlock deep nodes`;
                    if (mr > 0 && totalSpent < mr)
                      return `Invest ${mr - totalSpent} more point${mr - totalSpent > 1 ? "s" : ""} first`;
                    return "Requires parent node(s)";
                  })()}
                </div>
              )}
              {!readOnly && !locked && pts < max && pointsLeft === 0 && (
                <div className="mt-1 font-mono text-[10px] text-red-400/80">No passive points remaining</div>
              )}
            </div>
          );
        })()}


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
          <span className="ml-auto text-forge-dim/60">left-click to invest · right-click to refund</span>
        )}
      </div>
    </div>
  );
}
