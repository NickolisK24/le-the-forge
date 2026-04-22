/**
 * PassivesSection — wraps BuildPassiveTree and PassiveProgressBar.
 *
 * The store holds passive allocations as a flat `number[]` — one entry
 * per invested point, in order of allocation. BuildPassiveTree expects
 * an `AllocMap` (nodeId → points). PassiveProgressBar expects the flat
 * history array directly. This wrapper converts between the two.
 */

import { useCallback, useMemo } from "react";

import BuildPassiveTree from "@/components/features/build/BuildPassiveTree";
import PassiveProgressBar from "@/components/features/build/PassiveProgressBar";
import { useBuildWorkspaceStore } from "@/store";

function toAllocMap(history: number[]): Record<number, number> {
  const map: Record<number, number> = {};
  for (const id of history) {
    map[id] = (map[id] ?? 0) + 1;
  }
  return map;
}

export default function PassivesSection() {
  const history = useBuildWorkspaceStore((s) => s.build.passive_tree);
  const characterClass = useBuildWorkspaceStore((s) => s.build.character_class);
  const mastery = useBuildWorkspaceStore((s) => s.build.mastery);
  const setPassiveTree = useBuildWorkspaceStore((s) => s.setPassiveTree);

  const allocated = useMemo(() => toAllocMap(history), [history]);

  const handleAllocate = useCallback(
    (nodeId: number, points: number) => {
      const current = allocated[nodeId] ?? 0;
      if (points === current) return;
      if (points > current) {
        // Append one new entry per additional point.
        const next = [...history];
        for (let i = 0; i < points - current; i++) next.push(nodeId);
        setPassiveTree(next);
      } else {
        // Removing points: drop the last (points-current) occurrences of nodeId.
        const toDrop = current - points;
        const next: number[] = [];
        let dropped = 0;
        for (let i = history.length - 1; i >= 0; i--) {
          if (history[i] === nodeId && dropped < toDrop) {
            dropped++;
            continue;
          }
          next.unshift(history[i]);
        }
        setPassiveTree(next);
      }
    },
    [allocated, history, setPassiveTree],
  );

  const handleRewind = useCallback(
    (stepIndex: number) => {
      setPassiveTree(history.slice(0, stepIndex));
    },
    [history, setPassiveTree],
  );

  return (
    <section data-testid="workspace-section-passives" className="space-y-4">
      <BuildPassiveTree
        characterClass={characterClass}
        mastery={mastery}
        allocated={allocated}
        onAllocate={handleAllocate}
      />
      <PassiveProgressBar
        history={history}
        characterClass={characterClass}
        onRewindTo={handleRewind}
      />
    </section>
  );
}
