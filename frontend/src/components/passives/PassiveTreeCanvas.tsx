/**
 * PassiveTreeCanvas — shared SVG canvas for rendering passive trees.
 *
 * Pure rendering component: receives all computed graph state as props.
 * Manages only internal tooltip/hover state and the dependency inspector overlay.
 *
 * Uses the layout's node bounding box as the SVG viewBox. Combined with
 * `preserveAspectRatio="xMidYMid meet"`, this auto-fits and centers the tree
 * to fill its container with a small padding margin, regardless of viewport
 * size or which mastery tab is active.
 *
 * Used by both PassiveTreePage (standalone viewer) and BuildPlannerPage (embedded).
 */

import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import type { PassiveNode } from "@/services/passiveTreeService";
import { NodeState, canRemoveNode } from "@/utils/passiveGraph";
import { analyzeNodeDependencies, type DependencyReport } from "@/logic/analyzeNodeDependencies";
import { findPathToNode } from "@/logic/findPassivePath";
import PassiveTreeNode from "./PassiveTreeNode";
import PassiveTreeConnections from "./PassiveTreeConnections";
import DependencyInspector from "./DependencyInspector";

// Node sizing — we measure the container and compute radii in viewBox
// (tree-coord) units so that the smallest node always renders at a
// readable on-screen size, regardless of bbox dimensions.
//
// Minimum on-screen radius (pixels). The core-node coord radius is
// scaled up as needed to guarantee this floor after preserveAspectRatio
// "meet" maps bbox → container.
const MIN_SCREEN_NODE_R = 12;
// Base node radius in coord space (used when the natural scale is large
// enough that MIN_SCREEN_NODE_R does not force a bigger value).
const BASE_COORD_NODE_R = 18;
// Notable-to-core radius ratio (notable nodes are visually larger).
const NOTABLE_RATIO = 1.3;
// Base idle connection stroke width in coord space.
const BASE_COORD_STROKE = 3;

// ---------------------------------------------------------------------------
// Tooltip
// ---------------------------------------------------------------------------

interface TooltipData {
  node: PassiveNode;
  x: number;
  y: number;
}

function NodeTooltip({
  data,
  containerRect,
  allocated,
  canDealloc,
}: {
  data: TooltipData;
  containerRect: DOMRect | null;
  allocated: boolean;
  canDealloc: boolean;
}) {
  if (!containerRect) return null;
  const n = data.node;
  const tx = data.x - containerRect.left + 16;
  const ty = data.y - containerRect.top - 12;
  return (
    <div
      className="pointer-events-none absolute z-20 w-64 rounded border border-forge-border bg-forge-bg/95 p-3 shadow-2xl"
      style={{
        left: Math.min(tx, containerRect.width - 272),
        top: Math.max(4, ty),
      }}
    >
      <div className="font-display text-sm font-bold text-forge-amber">
        {n.name || "Passive Node"}
      </div>
      <div className="mt-0.5 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
        {n.node_type} · {n.max_points} pts
        {n.mastery && <span> · {n.mastery}</span>}
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
      {allocated && !canDealloc && (
        <div className="mt-1.5 font-mono text-[10px] text-red-400/80">
          Cannot remove — other nodes depend on this
        </div>
      )}
      <div className="mt-1.5 font-mono text-[10px] text-forge-dim/50">
        {allocated
          ? "L-click: +1 · Shift+L: max · R-click: -1 · Shift+R: remove"
          : "Left-click to allocate · Shift+click for max"}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface PassiveTreeCanvasProps {
  nodes: PassiveNode[];
  edges: Array<{ fromId: string; toId: string }>;
  positions: Map<string, { sx: number; sy: number; masteryIndex: number }>;
  /** Bounding box of the layout (from computeLayout). Used as the SVG viewBox. */
  bbox: { x: number; y: number; width: number; height: number };
  allocatedIds: Set<string>;
  allocatedPoints: Map<string, number>;
  startIds: Set<string>;
  adjacency: Map<string, Set<string>>;
  onNodeClick: (nodeId: string, shift: boolean) => void;
  onNodeRightClick: (nodeId: string, shift: boolean) => void;
  availableIds: Set<string>;
  highlightedNodes: Set<string>;
  highlightedEdges: Set<string>;
  blockingNodeIds: Set<string>;
  showPathHighlights?: boolean;
  readOnly?: boolean;
  /** Node IDs that are mastery-locked (upper half of non-chosen mastery trees) */
  masteryLockedIds?: Set<string>;
  /** Optional override for canvas min-height (px). Defaults to 500. */
  minHeight?: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PassiveTreeCanvas({
  nodes,
  edges,
  positions,
  bbox,
  allocatedIds,
  allocatedPoints,
  startIds,
  adjacency,
  onNodeClick,
  onNodeRightClick,
  availableIds,
  highlightedNodes,
  highlightedEdges,
  blockingNodeIds,
  readOnly,
  masteryLockedIds,
  minHeight = 500,
}: PassiveTreeCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [inspectorReport, setInspectorReport] = useState<{
    report: DependencyReport;
    x: number;
    y: number;
  } | null>(null);

  // Total base points spent — needed by dependency inspector for tier gating
  const totalBasePointsSpent = useMemo(() => {
    let total = 0;
    for (const node of nodes) {
      if (node.mastery === null && allocatedIds.has(node.id)) {
        total += allocatedPoints.get(node.id) ?? 1;
      }
    }
    return total;
  }, [nodes, allocatedIds, allocatedPoints]);

  // Node state resolver
  const getNodeState = useCallback(
    (nodeId: string): NodeState => {
      if (masteryLockedIds?.has(nodeId)) return NodeState.MASTERY_LOCKED;
      if (allocatedIds.has(nodeId)) return NodeState.ALLOCATED;
      if (availableIds.has(nodeId)) return NodeState.AVAILABLE;
      return NodeState.LOCKED;
    },
    [allocatedIds, availableIds, masteryLockedIds],
  );

  const handleHover = useCallback(
    (node: PassiveNode, x: number, y: number) => {
      setTooltip({ node, x, y });
    },
    [],
  );

  const handleLeave = useCallback(() => {
    setTooltip(null);
    setInspectorReport(null);
  }, []);

  // Shift-hover: show dependency inspector
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Shift" && tooltip) {
        const report = analyzeNodeDependencies(
          tooltip.node.id,
          nodes,
          allocatedIds,
          allocatedPoints,
          adjacency,
          startIds,
          totalBasePointsSpent,
        );
        setInspectorReport({ report, x: tooltip.x, y: tooltip.y });
      }
      if (e.type === "keyup" && e.key === "Shift") {
        setInspectorReport(null);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("keyup", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("keyup", onKey);
    };
  }, [tooltip, nodes, allocatedIds, allocatedPoints, adjacency, startIds, totalBasePointsSpent]);

  // Stable id of the hovered node — the tooltip object gets a new reference
  // on every mouse-move (new x/y), but downstream BFS/memoization only needs
  // to recompute when the hovered node itself changes.
  const tooltipNodeId = tooltip?.node.id ?? null;

  // --- Hover path highlighting (BFS from roots to hovered node) ---
  const hoverPath = useMemo(() => {
    if (!tooltipNodeId) return [];
    return findPathToNode(tooltipNodeId, adjacency, startIds);
  }, [tooltipNodeId, adjacency, startIds]);

  const hoverPathNodes = useMemo(() => new Set(hoverPath), [hoverPath]);
  const hoverPathEdges = useMemo(() => {
    const set = new Set<string>();
    for (let i = 0; i < hoverPath.length - 1; i++) {
      set.add(`${hoverPath[i]}-${hoverPath[i + 1]}`);
      set.add(`${hoverPath[i + 1]}-${hoverPath[i]}`);
    }
    return set;
  }, [hoverPath]);

  // Merge prop-provided highlights with internal hover highlights
  const mergedHighlightedNodes = useMemo(() => {
    const set = new Set(highlightedNodes);
    for (const id of hoverPathNodes) set.add(id);
    return set;
  }, [highlightedNodes, hoverPathNodes]);

  const mergedHighlightedEdges = useMemo(() => {
    const set = new Set(highlightedEdges);
    for (const e of hoverPathEdges) set.add(e);
    return set;
  }, [highlightedEdges, hoverPathEdges]);

  // Blocking nodes from inspector report (internal)
  const internalBlockingNodeIds = useMemo(() => {
    if (!inspectorReport) return blockingNodeIds;
    const set = new Set(blockingNodeIds);
    const r = inspectorReport.report;
    if (!r.isAllocated) {
      for (const pid of r.missingParents) set.add(pid);
    }
    if (r.isAllocated && !r.canRemove) {
      for (const cid of r.blockingChildren) set.add(cid);
    }
    return set;
  }, [inspectorReport, blockingNodeIds]);

  const containerRect = containerRef.current?.getBoundingClientRect() ?? null;
  const tooltipAllocated = tooltipNodeId ? allocatedIds.has(tooltipNodeId) : false;
  // Memoize the removal-safety BFS — keyed on node id (not the whole tooltip
  // object, which gets a new reference on every mouse-move). Without this,
  // each mouse-move updating `tooltip` re-runs canRemoveNode (a full BFS)
  // synchronously during render, costing seconds on larger graphs.
  const tooltipCanDealloc = useMemo(
    () =>
      tooltipNodeId && tooltipAllocated
        ? canRemoveNode(tooltipNodeId, allocatedIds, startIds, adjacency, nodes)
        : false,
    [tooltipNodeId, tooltipAllocated, allocatedIds, startIds, adjacency, nodes],
  );

  // Track container size so we can convert between screen pixels and
  // viewBox coord-space. preserveAspectRatio "meet" picks the smaller of
  // the two axis scales, so we mirror that logic below.
  const [containerSize, setContainerSize] = useState<{ w: number; h: number }>({
    w: 800,
    h: 600,
  });
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const update = () => {
      const rect = el.getBoundingClientRect();
      setContainerSize({ w: rect.width || 800, h: rect.height || 600 });
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Pixels-per-coord-unit the SVG will render at (preserveAspectRatio
  // "meet" → min of the two axis scales). Guard against zero bbox.
  const coordToPxScale = useMemo(() => {
    const sx = containerSize.w / (bbox.width || 1);
    const sy = containerSize.h / (bbox.height || 1);
    return Math.min(sx, sy) || 1;
  }, [containerSize, bbox.width, bbox.height]);

  // Node radii in coord space. Floor of BASE_COORD_NODE_R, but scale up
  // whenever the natural render would be smaller than MIN_SCREEN_NODE_R
  // pixels so nodes stay readable on any container/bbox combination.
  const nodeRCore = Math.max(
    BASE_COORD_NODE_R,
    MIN_SCREEN_NODE_R / coordToPxScale,
  );
  const nodeRNotable = nodeRCore * NOTABLE_RATIO;

  // Connection stroke widths in coord space. Anchored to the core radius
  // so they visually scale with the node size (and thus with the tree).
  const strokeIdle = Math.max(BASE_COORD_STROKE, nodeRCore * 0.18);
  const strokeHighlighted = strokeIdle * 1.4;
  const strokeAllocated = strokeIdle * 1.8;

  const viewBoxStr = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`;

  return (
    <div className="flex h-full w-full flex-col">
      {/* SVG canvas — fills the parent container. The viewBox is the node
          bounding box (with a small padding margin), so preserveAspectRatio
          "xMidYMid meet" auto-fits and centers the tree to fill any
          container width/height — including mobile pinch-zoom viewports. */}
      <div
        ref={containerRef}
        className="relative w-full flex-1 min-h-0 overflow-hidden rounded border border-forge-border select-none"
        style={{ minHeight, background: "#0b0e1a" }}
      >
        <svg
          viewBox={viewBoxStr}
          preserveAspectRatio="xMidYMid meet"
          width="100%"
          height="100%"
          style={{ display: "block" }}
        >
          <rect x={bbox.x} y={bbox.y} width={bbox.width} height={bbox.height} fill="#0b0e1a" />
          <PassiveTreeConnections
            edges={edges}
            positions={positions}
            allocatedIds={allocatedIds}
            highlightedEdges={mergedHighlightedEdges}
            strokeIdle={strokeIdle}
            strokeHighlighted={strokeHighlighted}
            strokeAllocated={strokeAllocated}
          />
          {nodes.map((node) => {
            const pos = positions.get(node.id);
            if (!pos) return null;
            const radius = node.max_points === 1 ? nodeRNotable : nodeRCore;
            return (
              <PassiveTreeNode
                key={node.id}
                node={node}
                sx={pos.sx}
                sy={pos.sy}
                radius={radius}
                state={getNodeState(node.id)}
                allocatedPoints={allocatedPoints.get(node.id) ?? 0}
                onNodeClick={onNodeClick}
                onNodeRightClick={onNodeRightClick}
                onHover={handleHover}
                onLeave={handleLeave}
                highlighted={mergedHighlightedNodes.has(node.id)}
                blocked={internalBlockingNodeIds.has(node.id)}
              />
            );
          })}
        </svg>
        {tooltip && !inspectorReport && (
          <NodeTooltip
            data={tooltip}
            containerRect={containerRect}
            allocated={tooltipAllocated}
            canDealloc={tooltipCanDealloc}
          />
        )}
        {inspectorReport && (
          <DependencyInspector
            report={inspectorReport.report}
            screenX={inspectorReport.x}
            screenY={inspectorReport.y}
            containerRect={containerRect}
          />
        )}
      </div>

      {/* Legend */}
      <div className="mt-2 flex flex-wrap items-center gap-4 font-mono text-[10px] text-forge-dim">
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border-2"
            style={{ borderColor: "#8890b8", background: "#181c30" }}
          />{" "}
          Allocated
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border"
            style={{ borderColor: "#5a6090", background: "#181c30" }}
          />{" "}
          Available
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border opacity-40"
            style={{ borderColor: "#3a4070", background: "#181c30" }}
          />{" "}
          Locked
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border opacity-20"
            style={{ borderColor: "#ef4444", background: "#181c30" }}
          />{" "}
          Mastery Required
        </span>
        {!readOnly && (
          <span className="text-forge-dim/50 ml-auto">
            L-click: invest · Shift+L: max · R-click: refund · Shift+R: remove all
          </span>
        )}
      </div>
    </div>
  );
}
