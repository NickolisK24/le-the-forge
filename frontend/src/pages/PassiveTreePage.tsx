/**
 * PassiveTreePage — interactive passive tree viewer with node allocation.
 *
 * Implements graph-valid selection:
 *   - Left-click to allocate (+1 point, or shift+click for max)
 *   - Right-click to deallocate (-1 point, or shift+right-click for full remove)
 *   - Deallocation blocked if it would orphan other allocated nodes (BFS check)
 *   - Uses BFS seeded ONLY from startIds (not all tier roots)
 *   - Dev-mode integrity validation after every allocation change
 */

import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Spinner } from "@/components/ui";
import type { CharacterClass } from "@/types";
import {
  fetchClassTree,
  type PassiveNode,
  type PassiveTreeResponse,
} from "@/services/passiveTreeService";
import { MASTERIES } from "@/lib/gameData";
import { BASE_CLASSES } from "@constants";
import PassiveTreeCanvas from "@/components/passives/PassiveTreeCanvas";
import PassiveStatsDebugPanel from "@/components/passives/PassiveStatsDebugPanel";
import StatValidationPanel from "@/components/passives/StatValidationPanel";
import PointEconomyPanel from "@/components/passives/PointEconomyPanel";
import MergedStatsPanel from "@/components/passives/MergedStatsPanel";
import StatSourceInspector from "@/components/passives/StatSourceInspector";
import ResolutionPipelineViewer from "@/components/passives/ResolutionPipelineViewer";
import ConditionalStatViewer from "@/components/passives/ConditionalStatViewer";
import BuffDebugPanel from "@/components/passives/BuffDebugPanel";
import { createBuffState, getActiveBuffs, runBuffTests, type BuffState } from "@/logic/buffManager";
import {
  evaluateConditionalModifiers,
  createEmptyBuildContext,
  EXAMPLE_CONDITIONAL_MODIFIERS,
  CONTEXT_CONDITIONAL_MODIFIERS,
} from "@/logic/conditionalStatEngine";
import { createPlannerContext, type RuntimeContext } from "@/types/runtimeContext";
import { mergeStatSnapshots, resolveCharacterStatsUnified } from "@/logic/mergeCharacterStats";
import { generateStatMergeSnapshot } from "@/logic/debugStatMerge";
import { generateResolutionSnapshot } from "@/logic/debugStatResolution";
import { validatePassiveBuild } from "@/logic/validatePassiveBuild";
import {
  findAllAllocatedPaths,
  collectPathNodes,
  collectPathEdges,
} from "@/logic/findPassivePath";
import { createPassiveStatSnapshot } from "@/logic/debugStatSnapshot";
import { resolveCharacterStats } from "@/logic/resolveCharacterStats";
import { computePassiveStats } from "@/logic/computePassiveStats";
import { resolveStats } from "@/logic/statResolutionPipeline";
import {
  buildBidirectionalAdjacency,
  findStartNodes,
  computeAvailableNodes,
  canRemoveNode,
  validateTreeIntegrity,
} from "@/utils/passiveGraph";
import { computeLayout } from "@/utils/passiveLayout";
import { serializeBuild, saveBuildToLocalStorage, clearBuildFromLocalStorage } from "@/logic/saveBuild";
import { deserializeBuild, loadBuildFromLocalStorage } from "@/logic/loadBuild";
import { copyBuildToClipboard } from "@/logic/exportBuild";
import { importBuildFromString } from "@/logic/importBuild";

const CLASSES: CharacterClass[] = [...BASE_CLASSES] as CharacterClass[];
const CANVAS_H = 650;

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PassiveTreePage() {
  const [selectedClass, setSelectedClass] = useState<CharacterClass | null>(null);
  const [selectedMastery, setSelectedMastery] = useState<string>("__all__");
  const [allocatedIds, setAllocatedIds] = useState<Set<string>>(new Set());
  const [allocatedPoints, setAllocatedPoints] = useState<Map<string, number>>(new Map());
  const [showAllocPaths, setShowAllocPaths] = useState(false);
  const [renderTimeMs, setRenderTimeMs] = useState<number | null>(null);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ w: 900, h: CANVAS_H });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => setCanvasSize({ w: entry.contentRect.width, h: CANVAS_H }));
    ro.observe(el);
    setCanvasSize({ w: el.clientWidth, h: CANVAS_H });
    return () => ro.disconnect();
  }, []);

  // Fetch
  const { data: treeData, isLoading, isError, error } = useQuery<PassiveTreeResponse | null>({
    queryKey: ["passives-viewer", selectedClass],
    queryFn: () => (selectedClass ? fetchClassTree(selectedClass) : null),
    enabled: Boolean(selectedClass),
    staleTime: 5 * 60 * 1000,
  });

  // Filter by mastery
  const filteredNodes = useMemo(() => {
    const all = treeData?.nodes ?? [];
    if (selectedMastery === "__all__") return all;
    if (selectedMastery === "__base__") return all.filter((n) => n.mastery === null);
    return all.filter((n) => n.mastery === selectedMastery || n.mastery === null);
  }, [treeData, selectedMastery]);

  // Part 3: Precomputed bidirectional adjacency — rebuilt only when nodes change
  const adjacency = useMemo(() => buildBidirectionalAdjacency(filteredNodes), [filteredNodes]);
  const startIds = useMemo(() => findStartNodes(filteredNodes), [filteredNodes]);

  // Node lookup for O(1) access
  const nodeById = useMemo(() => {
    const m = new Map<string, PassiveNode>();
    for (const n of filteredNodes) m.set(n.id, n);
    return m;
  }, [filteredNodes]);

  // Total base points spent (for mastery_requirement gating)
  const totalBasePointsSpent = useMemo(() => {
    let total = 0;
    for (const node of filteredNodes) {
      if (node.mastery === null && allocatedIds.has(node.id)) {
        total += allocatedPoints.get(node.id) ?? 1;
      }
    }
    return total;
  }, [filteredNodes, allocatedIds, allocatedPoints]);

  // Part 6: Available nodes cached via useMemo
  const availableIds = useMemo(
    () => computeAvailableNodes(filteredNodes, allocatedIds, totalBasePointsSpent),
    [filteredNodes, allocatedIds, totalBasePointsSpent],
  );

  // Passive stat aggregation — recomputes when allocations change
  const passiveStats = useMemo(
    () => computePassiveStats(allocatedPoints, nodeById),
    [allocatedPoints, nodeById],
  );

  // Resolve stats through the pipeline (flat → percent scaling → derived)
  const resolvedStats = useMemo(
    () => resolveStats(passiveStats),
    [passiveStats],
  );

  // Raw snapshot for debug display
  const statSnapshot = useMemo(
    () => createPassiveStatSnapshot(allocatedPoints, nodeById),
    [allocatedPoints, nodeById],
  );

  // Final character stats with base stats + derived
  const characterStats = useMemo(
    () => resolveCharacterStats(passiveStats),
    [passiveStats],
  );

  // Merged stats: passive + skill (skill stats are empty until skill tree is wired)
  const emptySkillStats = useMemo(() => new Map<string, import("@/types/passiveEffects").AggregatedStat>(), []);
  const emptySkillSnapshot = useMemo(() => ({} as Record<string, number>), []);
  const emptyGearSnapshot = useMemo(() => ({} as Record<string, number>), []);
  const mergedSnapshot = useMemo(
    () => mergeStatSnapshots(statSnapshot, emptySkillSnapshot),
    [statSnapshot, emptySkillSnapshot],
  );
  const unifiedFinalStats = useMemo(
    () => resolveCharacterStatsUnified(passiveStats, emptySkillStats),
    [passiveStats, emptySkillStats],
  );

  // Hardened merge snapshot (passive + skill + gear with validation)
  const statMergeSnapshot = useMemo(
    () => generateStatMergeSnapshot(statSnapshot, emptySkillSnapshot, emptyGearSnapshot),
    [statSnapshot, emptySkillSnapshot, emptyGearSnapshot],
  );

  // Resolution pipeline snapshot (per-stage instrumentation)
  const resolutionSnapshot = useMemo(
    () => generateResolutionSnapshot(passiveStats),
    [passiveStats],
  );

  // Conditional stat evaluation (using resolved pool as context)
  // Runtime context for conditional evaluation (planner defaults)
  const runtimeCtx = useMemo<RuntimeContext>(() => createPlannerContext(), []);

  // Buff state (empty in planner mode — buffs applied during simulation)
  const buffState = useMemo<BuffState>(() => createBuffState(), []);
  const activeBuffs = useMemo(() => getActiveBuffs(buffState), [buffState]);
  const buffTestResults = useMemo(() => runBuffTests(), []);

  // Evaluate both basic and context-based conditional modifiers
  const conditionalResults = useMemo(() => {
    const context = createEmptyBuildContext(resolvedStats);
    const allMods = [...EXAMPLE_CONDITIONAL_MODIFIERS, ...CONTEXT_CONDITIONAL_MODIFIERS];
    return evaluateConditionalModifiers(allMods, context, runtimeCtx);
  }, [resolvedStats, runtimeCtx]);

  // Build validation — point economy, tiers, mastery rules
  const buildValidation = useMemo(
    () => validatePassiveBuild(allocatedPoints, nodeById),
    [allocatedPoints, nodeById],
  );

  // --- Path highlighting (allocated paths only; hover paths handled by canvas) ---
  const allocatedPathData = useMemo(() => {
    if (!showAllocPaths || allocatedIds.size === 0) return { nodes: new Set<string>(), edges: new Set<string>() };
    const paths = findAllAllocatedPaths(allocatedIds, adjacency, startIds);
    return { nodes: collectPathNodes(paths), edges: collectPathEdges(paths) };
  }, [showAllocPaths, allocatedIds, adjacency, startIds]);

  const emptySet = useMemo(() => new Set<string>(), []);

  // Part 7: Dev-mode integrity check after every allocation change
  useEffect(() => {
    validateTreeIntegrity(allocatedIds, startIds, adjacency);
  }, [allocatedIds, startIds, adjacency]);

  // -------------------------------------------------------------------
  // Part 4: Left-click allocate (+ shift for max)
  // Part 9: Prevent redundant state updates
  // Part 10: Prevent exceeding max_points
  // -------------------------------------------------------------------
  const handleNodeClick = useCallback(
    (nodeId: string, shiftKey: boolean) => {
      const node = nodeById.get(nodeId);
      if (!node) return;

      if (allocatedIds.has(nodeId)) {
        // Already allocated — add more points
        const current = allocatedPoints.get(nodeId) ?? 1;
        if (current >= node.max_points) return; // Part 10: overflow guard
        const target = shiftKey ? node.max_points : current + 1; // Part 4: shift = max
        const clamped = Math.min(target, node.max_points); // Part 10: safety clamp
        if (clamped === current) return; // Part 9: no change
        setAllocatedPoints((prev) => {
          const next = new Map(prev);
          next.set(nodeId, clamped);
          return next;
        });
      } else if (availableIds.has(nodeId)) {
        // First allocation
        const pts = shiftKey ? node.max_points : 1; // Part 4: shift = max
        setAllocatedIds((prev) => {
          if (prev.has(nodeId)) return prev; // Part 9: redundancy guard
          return new Set(prev).add(nodeId);
        });
        setAllocatedPoints((prev) => {
          const next = new Map(prev);
          next.set(nodeId, Math.min(pts, node.max_points)); // Part 10: clamp
          return next;
        });
      }
    },
    [nodeById, allocatedIds, allocatedPoints, availableIds],
  );

  // -------------------------------------------------------------------
  // Part 5: Right-click deallocate (+ shift for full remove)
  // -------------------------------------------------------------------
  const handleNodeRightClick = useCallback(
    (nodeId: string, shiftKey: boolean) => {
      if (!allocatedIds.has(nodeId)) return;

      const pts = allocatedPoints.get(nodeId) ?? 1;

      if (shiftKey || pts === 1) {
        // Shift+right-click: remove ALL, or regular right-click on last point
        if (!canRemoveNode(nodeId, allocatedIds, startIds, adjacency, filteredNodes)) return;
        setAllocatedIds((prev) => {
          const next = new Set(prev);
          next.delete(nodeId);
          return next;
        });
        setAllocatedPoints((prev) => {
          const next = new Map(prev);
          next.delete(nodeId);
          return next;
        });
      } else {
        // Regular right-click: remove 1 point
        setAllocatedPoints((prev) => {
          const next = new Map(prev);
          next.set(nodeId, pts - 1);
          return next;
        });
      }
    },
    [allocatedIds, allocatedPoints, startIds, adjacency],
  );

  // Layout
  const layout = useMemo(
    () => computeLayout(filteredNodes, canvasSize.w, canvasSize.h),
    [filteredNodes, canvasSize],
  );

  // Render timing
  useEffect(() => {
    if (filteredNodes.length === 0) return;
    const start = performance.now();
    requestAnimationFrame(() => {
      const elapsed = Math.round(performance.now() - start);
      setRenderTimeMs(elapsed);
      if (elapsed > 500) console.warn(`[PassiveTreePage] Render time ${elapsed}ms exceeds 500ms`);
    });
  }, [filteredNodes, allocatedIds]);

  const handleClassChange = (cls: CharacterClass) => {
    setSelectedClass(cls);
    setSelectedMastery("__all__");
    setAllocatedIds(new Set());
    setAllocatedPoints(new Map());
  };
  const handleReset = () => {
    setAllocatedIds(new Set());
    setAllocatedPoints(new Map());
    clearBuildFromLocalStorage();
  };

  // --- Auto-save to localStorage on every allocation change ---
  useEffect(() => {
    if (!selectedClass || allocatedPoints.size === 0) return;
    const build = serializeBuild(allocatedPoints, selectedClass, selectedMastery);
    saveBuildToLocalStorage(build);
  }, [allocatedPoints, selectedClass, selectedMastery]);

  // --- Auto-load from localStorage on mount ---
  useEffect(() => {
    const saved = loadBuildFromLocalStorage();
    if (!saved) return;
    // Only auto-load if we haven't already selected a class
    if (selectedClass) return;
    setSelectedClass(saved.classId as CharacterClass);
    if (saved.masteryId) setSelectedMastery(saved.masteryId);
  }, []);

  // --- Restore allocations once tree data loads and matches saved build ---
  useEffect(() => {
    if (!treeData || !selectedClass) return;
    const saved = loadBuildFromLocalStorage();
    if (!saved || saved.classId !== selectedClass) return;
    // Only restore if we currently have zero allocations (fresh load)
    if (allocatedIds.size > 0) return;

    const result = deserializeBuild(saved, treeData.nodes);
    if (result.success && result.allocatedIds.size > 0) {
      setAllocatedIds(result.allocatedIds);
      setAllocatedPoints(result.allocatedPoints);
      if (result.warnings.length > 0) {
        console.warn("[Build Load] Warnings:", result.warnings);
      }
    }
  }, [treeData, selectedClass]);

  // --- Manual save/load handlers ---
  const handleSaveBuild = () => {
    if (!selectedClass) return;
    const build = serializeBuild(allocatedPoints, selectedClass, selectedMastery);
    saveBuildToLocalStorage(build);
  };

  const handleLoadBuild = () => {
    const saved = loadBuildFromLocalStorage();
    if (!saved) return;
    if (saved.classId !== selectedClass) {
      setSelectedClass(saved.classId as CharacterClass);
      if (saved.masteryId) setSelectedMastery(saved.masteryId);
      // Allocations will be restored by the treeData effect above
      return;
    }
    if (!treeData) return;
    const result = deserializeBuild(saved, treeData.nodes);
    if (result.success) {
      setAllocatedIds(result.allocatedIds);
      setAllocatedPoints(result.allocatedPoints);
    }
  };

  const handleExportBuild = async () => {
    if (!selectedClass) return;
    const build = serializeBuild(allocatedPoints, selectedClass, selectedMastery);
    const ok = await copyBuildToClipboard(build);
    if (ok) {
      setExportMsg("Copied!");
      setTimeout(() => setExportMsg(null), 2000);
    }
  };

  const handleImportBuild = () => {
    const encoded = prompt("Paste build string:");
    if (!encoded) return;
    const build = importBuildFromString(encoded);
    if (!build) {
      setExportMsg("Invalid build string");
      setTimeout(() => setExportMsg(null), 3000);
      return;
    }
    if (build.classId !== selectedClass) {
      setSelectedClass(build.classId as CharacterClass);
      if (build.masteryId) setSelectedMastery(build.masteryId);
    }
    saveBuildToLocalStorage(build);
    if (treeData) {
      const result = deserializeBuild(build, treeData.nodes);
      if (result.success) {
        setAllocatedIds(result.allocatedIds);
        setAllocatedPoints(result.allocatedPoints);
      }
    }
  };

  const masteries = selectedClass ? (MASTERIES[selectedClass] ?? []) : [];
  const totalPointsSpent = useMemo(
    () => Array.from(allocatedPoints.values()).reduce((a, b) => a + b, 0),
    [allocatedPoints],
  );

  // --- States ---
  if (!selectedClass) {
    return (<Page><PageHeader /><ClassSelector selected={null} onSelect={handleClassChange} />
      <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
        <p className="font-mono text-sm text-forge-dim">Select a class above to load the passive tree.</p>
      </div></Page>);
  }
  if (isLoading) {
    return (<Page><PageHeader /><ClassSelector selected={selectedClass} onSelect={handleClassChange} />
      <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
        <div className="flex flex-col items-center gap-3"><Spinner size={32} /><span className="font-mono text-xs text-forge-dim">Loading passive tree…</span></div>
      </div></Page>);
  }
  if (isError) {
    return (<Page><PageHeader /><ClassSelector selected={selectedClass} onSelect={handleClassChange} />
      <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
        <p className="text-sm text-red-400 font-medium">Error loading passive tree</p>
        <p className="text-xs text-red-400/70 mt-1">{(error as Error)?.message ?? "Unknown error"}</p>
      </div></Page>);
  }
  if (filteredNodes.length === 0) {
    return (<Page><PageHeader /><ClassSelector selected={selectedClass} onSelect={handleClassChange} />
      <MasterySelector masteries={masteries} selected={selectedMastery} onSelect={setSelectedMastery} />
      <div className="mt-4 flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
        <p className="font-mono text-sm text-forge-dim">No passive nodes for this selection.</p>
      </div></Page>);
  }

  return (
    <Page>
      <PageHeader />
      <ClassSelector selected={selectedClass} onSelect={handleClassChange} />
      <MasterySelector masteries={masteries} selected={selectedMastery} onSelect={setSelectedMastery} />

      {/* Status bar */}
      <div className="mt-3 mb-3 flex flex-wrap items-center gap-3">
        <Badge label={`Nodes: ${filteredNodes.length}`} ok />
        <Badge label={`Allocated: ${allocatedIds.size}`} ok={allocatedIds.size > 0} />
        <Badge label={`Points: ${totalPointsSpent}`} ok={totalPointsSpent > 0} />
        <Badge label={`Available: ${availableIds.size}`} ok />
        <Badge label={`Connections: ${layout.edges.length}`} ok />
        {renderTimeMs !== null && (
          <span className={`rounded px-2 py-0.5 font-mono text-[10px] ${renderTimeMs > 500 ? "bg-yellow-500/15 text-yellow-400" : "bg-forge-surface2 text-forge-dim"}`}>
            Render: {renderTimeMs}ms
          </span>
        )}
        {allocatedIds.size > 0 && (<>
          <button onClick={handleReset} className="rounded px-2.5 py-1 font-mono text-xs text-forge-dim hover:text-red-400 bg-forge-surface2 transition-colors">Reset</button>
        </>)}
        <button onClick={handleSaveBuild} className="rounded px-2.5 py-1 font-mono text-xs text-forge-dim hover:text-forge-cyan bg-forge-surface2 transition-colors">Save</button>
        <button onClick={handleLoadBuild} className="rounded px-2.5 py-1 font-mono text-xs text-forge-dim hover:text-forge-amber bg-forge-surface2 transition-colors">Load</button>
        <button onClick={handleExportBuild} className="rounded px-2.5 py-1 font-mono text-xs text-forge-dim hover:text-forge-text bg-forge-surface2 transition-colors">Export</button>
        <button onClick={handleImportBuild} className="rounded px-2.5 py-1 font-mono text-xs text-forge-dim hover:text-forge-text bg-forge-surface2 transition-colors">Import</button>
        <button
          onClick={() => setShowAllocPaths((v) => !v)}
          className={`rounded px-2.5 py-1 font-mono text-xs transition-colors ${showAllocPaths ? "bg-amber-500/20 text-amber-400" : "bg-forge-surface2 text-forge-dim hover:text-forge-muted"}`}
        >
          {showAllocPaths ? "Hide Paths" : "Show Paths"}
        </button>
        {exportMsg && <span className="font-mono text-xs text-forge-cyan">{exportMsg}</span>}
      </div>

      {/* Passive tree canvas */}
      <div ref={containerRef}>
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
          highlightedNodes={allocatedPathData.nodes}
          highlightedEdges={allocatedPathData.edges}
          blockingNodeIds={emptySet}
          canvasWidth={canvasSize.w}
          canvasHeight={canvasSize.h}
        />
      </div>

      {/* Stat debug panel */}
      <PassiveStatsDebugPanel
        stats={passiveStats}
        resolvedStats={resolvedStats}
        totalPoints={totalPointsSpent}
        allocatedCount={allocatedIds.size}
      />

      <StatValidationPanel
        snapshot={statSnapshot}
        resolvedCharStats={characterStats}
      />

      <PointEconomyPanel validation={buildValidation} />

      <MergedStatsPanel
        passiveSnapshot={statSnapshot}
        skillSnapshot={emptySkillSnapshot}
        mergedSnapshot={mergedSnapshot}
        finalStats={unifiedFinalStats}
      />

      <StatSourceInspector snapshot={statMergeSnapshot} />

      <ResolutionPipelineViewer snapshot={resolutionSnapshot} />

      <ConditionalStatViewer results={conditionalResults} />

      <BuffDebugPanel activeBuffs={activeBuffs} testResults={buffTestResults} />
    </Page>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Page({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto max-w-5xl px-4 py-8">{children}</div>;
}

function PageHeader() {
  return (
    <div className="mb-4">
      <h1 className="font-display text-2xl font-bold text-forge-amber">Passive Tree</h1>
      <p className="mt-1 font-body text-sm text-forge-muted">Click nodes to allocate points. Nodes must be reachable through connections.</p>
    </div>
  );
}

function ClassSelector({ selected, onSelect }: { selected: CharacterClass | null; onSelect: (c: CharacterClass) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {CLASSES.map((cls) => (
        <button key={cls} onClick={() => onSelect(cls)}
          className={`rounded px-3 py-1.5 font-body text-sm transition-colors ${selected === cls ? "bg-forge-amber/20 text-forge-amber font-semibold" : "bg-forge-surface2 text-forge-muted hover:text-forge-text"}`}>
          {cls}
        </button>
      ))}
    </div>
  );
}

function MasterySelector({ masteries, selected, onSelect }: { masteries: string[]; selected: string; onSelect: (m: string) => void }) {
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {["__all__", "__base__", ...masteries].map((m) => (
        <button key={m} onClick={() => onSelect(m)}
          className={`rounded px-2.5 py-1 font-mono text-xs transition-colors ${selected === m ? "bg-forge-cyan/20 text-forge-cyan font-semibold" : "bg-forge-surface2 text-forge-dim hover:text-forge-muted"}`}>
          {m === "__all__" ? "All" : m === "__base__" ? "Base" : m}
        </button>
      ))}
    </div>
  );
}

function Badge({ label, ok }: { label: string; ok: boolean }) {
  return <span className={`rounded px-2.5 py-1 font-mono text-xs font-semibold ${ok ? "bg-green-500/15 text-green-400" : "bg-forge-surface2 text-forge-dim"}`}>{label}</span>;
}
