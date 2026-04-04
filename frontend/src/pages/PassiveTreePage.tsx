/**
 * PassiveTreePage — browse and plan passive allocations.
 *
 * Fetches tree data from the live API when class/mastery selection changes.
 * Exposes the current allocated node ID array via the onAllocatedChange prop
 * so it can be wired into the Build Planner later.
 */

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Spinner } from "@/components/ui";
import PassiveTreeRenderer from "@/components/PassiveTree/PassiveTreeRenderer";
import PassiveTreeControls from "@/components/PassiveTree/PassiveTreeControls";
import type { CharacterClass } from "@/types";
import {
  fetchClassTree,
  fetchMasteryTree,
} from "@/services/passiveTreeService";
import type { AllocMap } from "@/components/PassiveTree/PassiveTreeRenderer";

interface Props {
  /** Called whenever the allocated node set changes (for Build Planner wiring). */
  onAllocatedChange?: (nodeIds: string[]) => void;
}

export default function PassiveTreePage({ onAllocatedChange }: Props) {
  const [selectedClass,  setSelectedClass]  = useState<CharacterClass | null>(null);
  const [selectedMastery, setSelectedMastery] = useState<string>("__base__");
  const [allocated, setAllocated] = useState<AllocMap>({});

  // ---------------------------------------------------------------------------
  // Data fetch — re-runs whenever class or mastery changes
  // ---------------------------------------------------------------------------
  const {
    data: treeData,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["passives", selectedClass, selectedMastery],
    queryFn: () => {
      if (!selectedClass) return null;
      // "__base__" is a client-side sentinel — fetch full tree and filter below
      return selectedMastery && selectedMastery !== "__base__"
        ? fetchMasteryTree(selectedClass, selectedMastery)
        : fetchClassTree(selectedClass);
    },
    enabled: Boolean(selectedClass),
    staleTime: 5 * 60 * 1000, // passive data changes rarely; cache for 5 min
  });

  const nodes = useMemo(() => {
    const all = treeData?.nodes ?? [];
    if (selectedMastery === "__base__") return all.filter((n) => n.mastery === null);
    // Mastery endpoint returns base + mastery nodes; show only mastery nodes
    return all.filter((n) => n.mastery !== null);
  }, [treeData, selectedMastery]);

  // ---------------------------------------------------------------------------
  // Allocation handlers
  // ---------------------------------------------------------------------------
  const handleAllocate = (nodeId: string, points: number) => {
    setAllocated((prev) => {
      const next = { ...prev, [nodeId]: points };
      if (points === 0) delete next[nodeId];
      onAllocatedChange?.(Object.keys(next));
      return next;
    });
  };

  const resetAllocations = () => {
    setAllocated({});
    onAllocatedChange?.([]);
  };

  const handleClassChange = (cls: CharacterClass | null) => {
    setSelectedClass(cls);
    setSelectedMastery("__base__");
    setAllocated({});
    onAllocatedChange?.([]);
  };

  const handleMasteryChange = (mastery: string) => {
    setSelectedMastery(mastery);
    setAllocated({});
    onAllocatedChange?.([]);
  };

  // ---------------------------------------------------------------------------
  // Derive point counts for the controls (base vs mastery nodes)
  // ---------------------------------------------------------------------------
  const { basePointsSpent, masteryPointsSpent } = useMemo(() => {
    let base = 0;
    let mastery = 0;
    for (const node of nodes) {
      const pts = allocated[node.id] ?? 0;
      if (node.mastery === null) base += pts;
      else mastery += pts;
    }
    return { basePointsSpent: base, masteryPointsSpent: mastery };
  }, [nodes, allocated]);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="flex flex-col gap-4">
      {/* Page header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wide text-forge-amber">
          Passive Tree
        </h1>
        <p className="mt-1 font-body text-sm text-forge-muted">
          Browse passive nodes and plan your build allocations.
        </p>
      </div>

      {/* Controls */}
      <PassiveTreeControls
        selectedClass={selectedClass}
        selectedMastery={selectedMastery}
        onClassChange={handleClassChange}
        onMasteryChange={handleMasteryChange}
        basePointsSpent={basePointsSpent}
        masteryPointsSpent={masteryPointsSpent}
        onReset={resetAllocations}
      />

      {/* Prompt when no class selected */}
      {!selectedClass && (
        <div className="flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <p className="font-mono text-sm text-forge-dim">
            Select a class above to load the passive tree.
          </p>
        </div>
      )}

      {/* Loading skeleton */}
      {selectedClass && isLoading && (
        <div className="flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <div className="flex flex-col items-center gap-3">
            <Spinner size={32} />
            <span className="font-mono text-xs text-forge-dim">
              Loading passive tree…
            </span>
          </div>
        </div>
      )}

      {/* Error state */}
      {selectedClass && isError && (
        <div className="flex h-80 items-center justify-center rounded border border-forge-border bg-forge-surface">
          <p className="font-mono text-sm text-red-400/80">
            {(error as Error)?.message ?? "Failed to load passive tree."}
          </p>
        </div>
      )}

      {/* Tree panel */}
      {selectedClass && !isLoading && !isError && treeData && (
        <div className="overflow-hidden rounded border border-forge-border">
          {/* Panel header */}
          <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-2">
            <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
              {treeData.class ?? selectedClass}
              {(treeData.mastery || selectedMastery === "__base__") && (
                <span className="text-forge-muted"> · {selectedMastery === "__base__" ? "Base" : treeData.mastery}</span>
              )}
            </span>
            <span className="font-mono text-[10px] text-forge-dim">
              {treeData.count} nodes
            </span>
          </div>

          <PassiveTreeRenderer
            nodes={nodes}
            allocated={allocated}
            onAllocate={handleAllocate}
          />
        </div>
      )}
    </div>
  );
}
