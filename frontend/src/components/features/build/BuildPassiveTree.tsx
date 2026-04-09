/**
 * BuildPassiveTree — wrapper that bridges BuildPlannerPage's numeric allocation
 * model with the shared PassiveTreeCanvas component.
 *
 * Responsibilities:
 *   - Fetches API tree data for the character class
 *   - Converts between raw_node_id (number[]) and string-ID formats
 *   - Computes graph state (adjacency, available nodes, layout)
 *   - Delegates rendering to PassiveTreeCanvas
 *   - Handles allocation logic (click → increment/decrement → callback)
 */

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Spinner } from "@/components/ui";
import {
  fetchClassTree,
  type PassiveNode,
  type PassiveTreeResponse,
} from "@/services/passiveTreeService";
import {
  buildBidirectionalAdjacency,
  findStartNodes,
  computeAvailableNodes,
  canRemoveNode,
} from "@/utils/passiveGraph";
import { computeLayout } from "@/utils/passiveLayout";
import PassiveTreeCanvas from "@/components/passives/PassiveTreeCanvas";
import PassiveTreeSelector from "@/components/PassiveTree/PassiveTreeSelector";
import { CLASS_MASTERIES } from "@constants";

type AllocMap = Record<number, number>;

const CANVAS_H = 580;

// Last Epoch passive point budget rules
const BASE_POINT_CAP = 20;         // Max points in base class tree
const NON_CHOSEN_MASTERY_CAP = 25; // Max points in each non-chosen mastery
// Chosen mastery has no per-section cap (uses overall budget)

interface Props {
  characterClass: string;
  mastery: string;
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
  totalPassivePoints?: number;
}

export default function BuildPassiveTree({
  characterClass,
  mastery,
  allocated,
  onAllocate,
  readOnly = false,
  totalPassivePoints = 113,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ w: 800, h: CANVAS_H });
  const [activeTab, setActiveTab] = useState<string>("__base__");

  // Reset tab when class changes
  useEffect(() => {
    setActiveTab("__base__");
  }, [characterClass]);

  // Resize observer for responsive width
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) =>
      setCanvasSize({ w: entry.contentRect.width, h: CANVAS_H }),
    );
    ro.observe(el);
    setCanvasSize({ w: el.clientWidth, h: CANVAS_H });
    return () => ro.disconnect();
  }, []);

  // Fetch full class tree from API
  const { data: treeData, isLoading, isError, error } = useQuery<PassiveTreeResponse>({
    queryKey: ["passives-build", characterClass],
    queryFn: () => fetchClassTree(characterClass),
    enabled: Boolean(characterClass),
    staleTime: 5 * 60 * 1000,
  });

  const masteries = useMemo(
    () => (CLASS_MASTERIES as Record<string, readonly string[]>)[characterClass] ?? [],
    [characterClass],
  );

  // Filter nodes: show only the active tab's section (no overlap)
  const filteredNodes = useMemo(() => {
    if (treeData?.grouped) {
      return treeData.grouped[activeTab] ?? [];
    }
    const all = treeData?.nodes ?? [];
    if (activeTab === "__base__") return all.filter((n) => n.mastery === null);
    return all.filter((n) => n.mastery === activeTab);
  }, [treeData, activeTab]);

  // ID mappings: raw_node_id ↔ string id
  const { rawToStr, strToRaw } = useMemo(() => {
    const r2s = new Map<number, string>();
    const s2r = new Map<string, number>();
    for (const node of filteredNodes) {
      r2s.set(node.raw_node_id, node.id);
      s2r.set(node.id, node.raw_node_id);
    }
    return { rawToStr: r2s, strToRaw: s2r };
  }, [filteredNodes]);

  // Convert numeric AllocMap → string-based Sets/Maps for canvas
  const { allocatedIds, allocatedPoints } = useMemo(() => {
    const ids = new Set<string>();
    const pts = new Map<string, number>();
    for (const [rawId, count] of Object.entries(allocated)) {
      const strId = rawToStr.get(Number(rawId));
      if (strId && count > 0) {
        ids.add(strId);
        pts.set(strId, count);
      }
    }
    return { allocatedIds: ids, allocatedPoints: pts };
  }, [allocated, rawToStr]);

  // Graph computations
  const adjacency = useMemo(
    () => buildBidirectionalAdjacency(filteredNodes),
    [filteredNodes],
  );
  const startIds = useMemo(
    () => findStartNodes(filteredNodes),
    [filteredNodes],
  );

  const totalBasePointsSpent = useMemo(() => {
    let total = 0;
    for (const node of filteredNodes) {
      if (node.mastery === null && allocatedIds.has(node.id)) {
        total += allocatedPoints.get(node.id) ?? 1;
      }
    }
    return total;
  }, [filteredNodes, allocatedIds, allocatedPoints]);

  const availableIds = useMemo(
    () => computeAvailableNodes(filteredNodes, allocatedIds, totalBasePointsSpent),
    [filteredNodes, allocatedIds, totalBasePointsSpent],
  );

  // Layout
  const layout = useMemo(
    () => computeLayout(filteredNodes, canvasSize.w, canvasSize.h),
    [filteredNodes, canvasSize],
  );

  // Node lookup
  const nodeById = useMemo(() => {
    const m = new Map<string, PassiveNode>();
    for (const n of filteredNodes) m.set(n.id, n);
    return m;
  }, [filteredNodes]);

  // Point budget
  const totalSpent = Object.values(allocated).reduce((s, v) => s + v, 0);
  const pointsLeft = totalPassivePoints - totalSpent;

  // Points per tree section for tab badges
  const pointsBySection = useMemo(() => {
    const result: Record<string, number> = {};
    const allNodes = treeData?.nodes ?? [];
    for (const node of allNodes) {
      if (!allocatedIds.has(node.id)) continue;
      const section = node.mastery ?? "__base__";
      result[section] = (result[section] ?? 0) + (allocatedPoints.get(node.id) ?? 1);
    }
    return result;
  }, [treeData, allocatedIds, allocatedPoints]);

  // Section cap: how many more points can go into the node's section?
  const sectionCapRemaining = useCallback(
    (node: PassiveNode): number => {
      const section = node.mastery ?? "__base__";
      const spent = pointsBySection[section] ?? 0;
      if (section === "__base__") return Math.max(0, BASE_POINT_CAP - spent);
      if (section === mastery) return Infinity; // chosen mastery: no per-section cap
      return Math.max(0, NON_CHOSEN_MASTERY_CAP - spent);
    },
    [pointsBySection, mastery],
  );

  // Allocation handlers — convert string IDs back to numeric for parent callback
  const handleNodeClick = useCallback(
    (nodeId: string, shiftKey: boolean) => {
      if (readOnly) return;
      const node = nodeById.get(nodeId);
      const rawId = strToRaw.get(nodeId);
      if (!node || rawId === undefined) return;
      if (pointsLeft <= 0 && !allocatedIds.has(nodeId)) return;

      const capLeft = sectionCapRemaining(node);
      if (capLeft <= 0 && !allocatedIds.has(nodeId)) return;

      if (allocatedIds.has(nodeId)) {
        const current = allocatedPoints.get(nodeId) ?? 1;
        if (current >= node.max_points) return;
        const target = shiftKey ? node.max_points : current + 1;
        const addable = Math.min(target - current, pointsLeft, capLeft);
        const clamped = Math.min(current + addable, node.max_points);
        if (clamped === current) return;
        onAllocate(rawId, clamped);
      } else if (availableIds.has(nodeId)) {
        const desired = shiftKey ? node.max_points : 1;
        const pts = Math.min(desired, pointsLeft, capLeft);
        if (pts <= 0) return;
        onAllocate(rawId, pts);
      }
    },
    [nodeById, strToRaw, allocatedIds, allocatedPoints, availableIds, onAllocate, readOnly, pointsLeft, sectionCapRemaining],
  );

  const handleNodeRightClick = useCallback(
    (nodeId: string, shiftKey: boolean) => {
      if (readOnly) return;
      if (!allocatedIds.has(nodeId)) return;
      const rawId = strToRaw.get(nodeId);
      if (rawId === undefined) return;

      const pts = allocatedPoints.get(nodeId) ?? 1;

      if (shiftKey || pts === 1) {
        if (!canRemoveNode(nodeId, allocatedIds, startIds, adjacency, filteredNodes)) return;
        onAllocate(rawId, 0);
      } else {
        onAllocate(rawId, pts - 1);
      }
    },
    [allocatedIds, allocatedPoints, startIds, adjacency, filteredNodes, strToRaw, onAllocate, readOnly],
  );

  // Empty highlight sets (no show-paths toggle in build planner)
  const emptySet = useMemo(() => new Set<string>(), []);

  // --- Loading / Error states ---
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size={28} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded border border-red-500/30 bg-red-500/10 px-4 py-3">
        <p className="text-sm text-red-400">
          Failed to load passive tree: {(error as Error)?.message ?? "Unknown error"}
        </p>
      </div>
    );
  }

  if (filteredNodes.length === 0) {
    return (
      <div ref={containerRef} className="flex flex-col gap-0">
        <PassiveTreeSelector
          masteries={[...masteries]}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          pointsBySection={pointsBySection}
          lockedMastery={mastery || null}
        />
        <div className="flex items-center justify-center py-12 border border-t-0 border-forge-border">
          <span className="font-mono text-xs text-forge-dim">No passive data for this section.</span>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="flex flex-col gap-0">
      {/* Mastery tab selector */}
      <PassiveTreeSelector
        masteries={[...masteries]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        pointsBySection={pointsBySection}
        lockedMastery={mastery || null}
      />

      {/* Point budget bar */}
      <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-3 py-1.5">
        <div className="flex items-center gap-3 font-mono text-[10px]">
          <span className="text-forge-dim uppercase tracking-widest">Passive Points</span>
          <span className={`font-bold ${totalSpent > 0 ? "text-forge-amber" : "text-forge-dim"}`}>
            {totalSpent} spent
          </span>
          <span className="text-forge-dim">·</span>
          <span className={`font-bold ${pointsLeft < 10 ? "text-red-400" : "text-forge-text"}`}>
            {pointsLeft} remaining
          </span>
          <span className="text-forge-dim">/ {totalPassivePoints}</span>
          {/* Section cap for current tab */}
          {activeTab === "__base__" && (
            <>
              <span className="text-forge-dim">·</span>
              <span className="text-forge-dim">
                Base: {pointsBySection["__base__"] ?? 0}/{BASE_POINT_CAP}
              </span>
            </>
          )}
          {activeTab !== "__base__" && activeTab !== mastery && (
            <>
              <span className="text-forge-dim">·</span>
              <span className="text-forge-dim">
                {activeTab}: {pointsBySection[activeTab] ?? 0}/{NON_CHOSEN_MASTERY_CAP}
              </span>
            </>
          )}
        </div>
        {!readOnly && pointsLeft === 0 && (
          <span className="font-mono text-[9px] text-red-400/80">All points spent</span>
        )}
      </div>

      <PassiveTreeCanvas
        nodes={filteredNodes}
        edges={layout.edges}
        positions={layout.positions}
        scale={layout.scale}
        allocatedIds={allocatedIds}
        allocatedPoints={allocatedPoints}
        startIds={startIds}
        adjacency={adjacency}
        onNodeClick={handleNodeClick}
        onNodeRightClick={handleNodeRightClick}
        availableIds={availableIds}
        highlightedNodes={emptySet}
        highlightedEdges={emptySet}
        blockingNodeIds={emptySet}
        canvasWidth={canvasSize.w}
        canvasHeight={canvasSize.h}
        readOnly={readOnly}
      />
    </div>
  );
}
