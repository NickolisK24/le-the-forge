/**
 * BuildPassiveTree — renders all 4 passive trees simultaneously in a 2x2 grid.
 *
 * Last Epoch passive tree rules:
 *   - 4 trees: 1 base class + 3 mastery trees, all visible at once
 *   - Base tree: no point cap, tier gating at 5/10/15/20/25
 *   - 20 points in base tree required to unlock mastery trees
 *   - Chosen mastery: full tree accessible, no point cap
 *   - Non-chosen masteries: capped at 25 points, bottom half only
 *     (nodes with mastery_requirement > 25 are locked)
 *   - Total budget: 113 passive points (98 leveling + 15 quests)
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
import { CLASS_MASTERIES } from "@constants";

type AllocMap = Record<number, number>;

const PANEL_H = 460;

// Last Epoch passive point budget rules
const BASE_TREE_GATE = 20;            // Points in base tree to unlock mastery trees
const NON_CHOSEN_MASTERY_CAP = 25;    // Max points in each non-chosen mastery tree
const NON_CHOSEN_REQ_THRESHOLD = 25;  // mastery_requirement above this = upper half (locked)
// Chosen mastery has no per-section cap
// Base tree has no point cap

interface Props {
  characterClass: string;
  mastery: string;
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
  totalPassivePoints?: number;
}

/** Group nodes by tree section key: "__base__" or mastery name */
function groupBySection(nodes: PassiveNode[]): Record<string, PassiveNode[]> {
  const groups: Record<string, PassiveNode[]> = {};
  for (const n of nodes) {
    const key = n.mastery ?? "__base__";
    (groups[key] ??= []).push(n);
  }
  return groups;
}

/** Get mastery index (1/2/3) for a mastery name within a class */
function getMasteryIndex(masteries: readonly string[], masteryName: string): number {
  const idx = masteries.indexOf(masteryName);
  return idx >= 0 ? idx + 1 : 0;
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
  const [panelWidth, setPanelWidth] = useState(400);

  // Resize observer for responsive width
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => setPanelWidth(Math.floor(entry.contentRect.width / 2)));
    ro.observe(el);
    setPanelWidth(Math.floor(el.clientWidth / 2));
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

  const allNodes = useMemo(() => treeData?.nodes ?? [], [treeData]);

  // Group nodes by section
  const sections = useMemo(() => groupBySection(allNodes), [allNodes]);

  // Section keys in display order: base, then masteries in CLASS_MASTERIES order
  const sectionKeys = useMemo(
    () => ["__base__", ...masteries],
    [masteries],
  );

  // Global ID mappings: raw_node_id <-> string id (across all sections)
  const { rawToStr, strToRaw } = useMemo(() => {
    const r2s = new Map<number, string>();
    const s2r = new Map<string, number>();
    for (const node of allNodes) {
      r2s.set(node.raw_node_id, node.id);
      s2r.set(node.id, node.raw_node_id);
    }
    return { rawToStr: r2s, strToRaw: s2r };
  }, [allNodes]);

  // Convert numeric AllocMap -> string-based Sets/Maps for canvas
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

  // Points spent per section
  const pointsBySection = useMemo(() => {
    const result: Record<string, number> = {};
    for (const node of allNodes) {
      const strId = node.id;
      const pts = allocatedPoints.get(strId);
      if (pts && pts > 0) {
        const section = node.mastery ?? "__base__";
        result[section] = (result[section] ?? 0) + pts;
      }
    }
    return result;
  }, [allNodes, allocatedPoints]);

  const basePointsSpent = pointsBySection["__base__"] ?? 0;
  const totalSpent = Object.values(pointsBySection).reduce((s, v) => s + v, 0);
  const pointsLeft = totalPassivePoints - totalSpent;
  const masteryTreesUnlocked = basePointsSpent >= BASE_TREE_GATE;

  // Per-section graph computations (memoized per section)
  const sectionData = useMemo(() => {
    const result: Record<string, {
      nodes: PassiveNode[];
      adjacency: Map<string, Set<string>>;
      startIds: Set<string>;
      layout: ReturnType<typeof computeLayout>;
    }> = {};
    for (const key of sectionKeys) {
      const nodes = sections[key] ?? [];
      const adjacency = buildBidirectionalAdjacency(nodes);
      const startIds = findStartNodes(nodes);
      const layout = computeLayout(nodes, panelWidth, PANEL_H);
      result[key] = { nodes, adjacency, startIds, layout };
    }
    return result;
  }, [sectionKeys, sections, panelWidth]);

  // Mastery-locked node IDs: upper-half nodes in non-chosen mastery trees
  const masteryLockedIds = useMemo(() => {
    const locked = new Set<string>();
    for (const key of sectionKeys) {
      if (key === "__base__") continue;
      if (key === mastery) continue; // chosen mastery: full access
      const nodes = sections[key] ?? [];
      for (const node of nodes) {
        if (node.mastery_requirement > NON_CHOSEN_REQ_THRESHOLD) {
          locked.add(node.id);
        }
      }
    }
    return locked;
  }, [sectionKeys, sections, mastery]);

  // Available nodes per section
  const sectionAvailable = useMemo(() => {
    const result: Record<string, Set<string>> = {};
    for (const key of sectionKeys) {
      const sd = sectionData[key];
      if (!sd) { result[key] = new Set(); continue; }

      if (key === "__base__") {
        // Base tree: always accessible, tier gating within the tree
        result[key] = computeAvailableNodes(sd.nodes, allocatedIds, basePointsSpent);
      } else if (!masteryTreesUnlocked) {
        // Mastery trees locked until 20 base points
        result[key] = new Set();
      } else {
        // Mastery tree: compute available nodes using that tree's own points for tier gating
        const sectionPoints = pointsBySection[key] ?? 0;
        const available = computeAvailableNodes(sd.nodes, allocatedIds, sectionPoints);
        // Remove mastery-locked nodes from available set
        for (const id of masteryLockedIds) {
          available.delete(id);
        }
        result[key] = available;
      }
    }
    return result;
  }, [sectionKeys, sectionData, allocatedIds, basePointsSpent, masteryTreesUnlocked, pointsBySection, masteryLockedIds]);

  // Section cap: how many more points can go into a section
  const sectionCapRemaining = useCallback(
    (sectionKey: string): number => {
      const spent = pointsBySection[sectionKey] ?? 0;
      if (sectionKey === "__base__") return Infinity; // no cap
      if (sectionKey === mastery) return Infinity; // chosen mastery: no cap
      return Math.max(0, NON_CHOSEN_MASTERY_CAP - spent);
    },
    [pointsBySection, mastery],
  );

  // Node lookup across all sections
  const nodeById = useMemo(() => {
    const m = new Map<string, PassiveNode>();
    for (const n of allNodes) m.set(n.id, n);
    return m;
  }, [allNodes]);

  // Allocation handler for a specific section
  const makeHandleClick = useCallback(
    (sectionKey: string) => (nodeId: string, shiftKey: boolean) => {
      if (readOnly) return;
      const node = nodeById.get(nodeId);
      const rawId = strToRaw.get(nodeId);
      if (!node || rawId === undefined) return;

      // Don't allow allocation on mastery-locked nodes
      if (masteryLockedIds.has(nodeId)) return;

      // Don't allow mastery tree allocation if base tree gate not met
      if (sectionKey !== "__base__" && !masteryTreesUnlocked) return;

      if (pointsLeft <= 0 && !allocatedIds.has(nodeId)) return;

      const capLeft = sectionCapRemaining(sectionKey);
      if (capLeft <= 0 && !allocatedIds.has(nodeId)) return;

      const sd = sectionData[sectionKey];
      if (!sd) return;
      const available = sectionAvailable[sectionKey] ?? new Set();

      if (allocatedIds.has(nodeId)) {
        const current = allocatedPoints.get(nodeId) ?? 1;
        if (current >= node.max_points) return;
        const target = shiftKey ? node.max_points : current + 1;
        const addable = Math.min(target - current, pointsLeft, capLeft);
        const clamped = Math.min(current + addable, node.max_points);
        if (clamped === current) return;
        onAllocate(rawId, clamped);
      } else if (available.has(nodeId)) {
        const desired = shiftKey ? node.max_points : 1;
        const pts = Math.min(desired, pointsLeft, capLeft);
        if (pts <= 0) return;
        onAllocate(rawId, pts);
      }
    },
    [nodeById, strToRaw, allocatedIds, allocatedPoints, onAllocate, readOnly, pointsLeft,
      sectionCapRemaining, sectionData, sectionAvailable, masteryLockedIds, masteryTreesUnlocked],
  );

  const makeHandleRightClick = useCallback(
    (sectionKey: string) => (nodeId: string, shiftKey: boolean) => {
      if (readOnly) return;
      if (!allocatedIds.has(nodeId)) return;
      const rawId = strToRaw.get(nodeId);
      if (rawId === undefined) return;

      const sd = sectionData[sectionKey];
      if (!sd) return;

      const pts = allocatedPoints.get(nodeId) ?? 1;

      if (shiftKey || pts === 1) {
        if (!canRemoveNode(nodeId, allocatedIds, sd.startIds, sd.adjacency, sd.nodes)) return;
        onAllocate(rawId, 0);
      } else {
        onAllocate(rawId, pts - 1);
      }
    },
    [allocatedIds, allocatedPoints, strToRaw, onAllocate, readOnly, sectionData],
  );

  // Empty highlight sets
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

  if (allNodes.length === 0) {
    return (
      <div ref={containerRef} className="flex items-center justify-center py-12 border border-forge-border">
        <span className="font-mono text-xs text-forge-dim">No passive data available.</span>
      </div>
    );
  }

  /** Label for a section's point indicator */
  function sectionPointLabel(key: string): string {
    const spent = pointsBySection[key] ?? 0;
    if (key === "__base__") return `${spent}`;
    if (key === mastery) return `${spent}`;
    return `${spent}/${NON_CHOSEN_MASTERY_CAP}`;
  }

  /** Section display name */
  function sectionName(key: string): string {
    return key === "__base__" ? "Base" : key;
  }

  /** Whether a section is the chosen mastery */
  function isChosenMastery(key: string): boolean {
    return key !== "__base__" && key === mastery;
  }

  /** Whether a section is a non-chosen mastery */
  function isNonChosenMastery(key: string): boolean {
    return key !== "__base__" && key !== mastery;
  }

  return (
    <div ref={containerRef} className="flex flex-col gap-0">
      {/* Total point budget bar */}
      <div className="flex items-center justify-between border border-forge-border bg-forge-surface2 px-3 py-2 rounded-t">
        <div className="flex items-center gap-3 font-mono text-[10px]">
          <span className="text-forge-dim uppercase tracking-widest">Passive Points</span>
          <span className={`font-bold ${totalSpent > 0 ? "text-forge-amber" : "text-forge-dim"}`}>
            {totalSpent} / {totalPassivePoints}
          </span>
          <span className="text-forge-dim">|</span>
          <span className={`font-bold ${pointsLeft < 10 ? "text-red-400" : "text-forge-text"}`}>
            {pointsLeft} remaining
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[10px]">
          {!masteryTreesUnlocked && (
            <span className="text-yellow-400/80">
              {BASE_TREE_GATE - basePointsSpent} base pts to unlock masteries
            </span>
          )}
          {!readOnly && pointsLeft === 0 && (
            <span className="text-red-400/80">All points spent</span>
          )}
        </div>
      </div>

      {/* 2x2 grid of tree panels */}
      <div className="grid grid-cols-2 gap-0">
        {sectionKeys.map((key) => {
          const sd = sectionData[key];
          if (!sd) return null;
          const available = sectionAvailable[key] ?? new Set();
          const isMastery = key !== "__base__";
          const isLocked = isMastery && !masteryTreesUnlocked;
          const isChosen = isChosenMastery(key);
          const isNonChosen = isNonChosenMastery(key);
          const spent = pointsBySection[key] ?? 0;

          return (
            <div key={key} className="flex flex-col border border-forge-border">
              {/* Section header */}
              <div className={`flex items-center justify-between px-3 py-1.5 ${
                isChosen
                  ? "bg-forge-amber/10 border-b border-forge-amber/30"
                  : isLocked
                    ? "bg-forge-surface opacity-60 border-b border-forge-border"
                    : "bg-forge-surface2 border-b border-forge-border"
              }`}>
                <div className="flex items-center gap-2 font-mono text-[11px]">
                  <span className={`font-bold ${
                    isChosen ? "text-forge-amber" : isLocked ? "text-forge-dim" : "text-forge-text"
                  }`}>
                    {sectionName(key)}
                  </span>
                  {isChosen && (
                    <span className="rounded bg-forge-amber/20 px-1.5 py-0.5 text-[9px] font-bold text-forge-amber">
                      CHOSEN
                    </span>
                  )}
                  {isLocked && (
                    <span className="rounded bg-forge-surface2 px-1.5 py-0.5 text-[9px] text-forge-dim">
                      LOCKED
                    </span>
                  )}
                </div>
                <div className="font-mono text-[10px]">
                  {key === "__base__" ? (
                    <span className={spent >= BASE_TREE_GATE ? "text-green-400" : "text-forge-dim"}>
                      {sectionPointLabel(key)} pts
                      {spent < BASE_TREE_GATE && (
                        <span className="text-forge-dim"> (gate: {BASE_TREE_GATE})</span>
                      )}
                    </span>
                  ) : isChosen ? (
                    <span className="text-forge-amber">{spent} pts</span>
                  ) : (
                    <span className={spent >= NON_CHOSEN_MASTERY_CAP ? "text-red-400" : "text-forge-dim"}>
                      {sectionPointLabel(key)} pts
                    </span>
                  )}
                </div>
              </div>

              {/* Tree canvas or locked overlay */}
              {isLocked ? (
                <div
                  className="flex items-center justify-center"
                  style={{ height: PANEL_H, background: "#0b0e1a" }}
                >
                  <div className="text-center">
                    <div className="font-mono text-xs text-forge-dim/60">
                      Spend {BASE_TREE_GATE - basePointsSpent} more point{BASE_TREE_GATE - basePointsSpent !== 1 ? "s" : ""} in Base tree
                    </div>
                    <div className="font-mono text-[10px] text-forge-dim/40 mt-1">
                      to unlock mastery trees
                    </div>
                  </div>
                </div>
              ) : sd.nodes.length === 0 ? (
                <div
                  className="flex items-center justify-center"
                  style={{ height: PANEL_H, background: "#0b0e1a" }}
                >
                  <span className="font-mono text-xs text-forge-dim">No passive data.</span>
                </div>
              ) : (
                <PassiveTreeCanvas
                  nodes={sd.nodes}
                  edges={sd.layout.edges}
                  positions={sd.layout.positions}
                  scale={sd.layout.scale}
                  allocatedIds={allocatedIds}
                  allocatedPoints={allocatedPoints}
                  startIds={sd.startIds}
                  adjacency={sd.adjacency}
                  onNodeClick={makeHandleClick(key)}
                  onNodeRightClick={makeHandleRightClick(key)}
                  availableIds={available}
                  highlightedNodes={emptySet}
                  highlightedEdges={emptySet}
                  blockingNodeIds={emptySet}
                  canvasWidth={panelWidth}
                  canvasHeight={PANEL_H}
                  readOnly={readOnly || isLocked}
                  masteryLockedIds={isNonChosen ? masteryLockedIds : undefined}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
