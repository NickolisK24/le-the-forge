/**
 * SkillsSection — wraps SkillSelector, translating its fine-grained
 * callbacks (add/remove/points/tree-alloc) into setSkills() calls.
 *
 * SkillSelector exposes four separate callbacks because it was designed
 * around BuildPlannerPage's many useState hooks. The adapter computes the
 * next full skills array and dispatches a single setSkills() — keeping
 * the store's action surface narrow and undo-stack-friendly.
 */

import { useCallback } from "react";

import SkillSelector from "@/components/features/build/SkillSelector";
import type { BuildSkill } from "@/types";
import { useBuildWorkspaceStore } from "@/store";

const MAX_SLOTS = 5;

function nextSlotIndex(skills: BuildSkill[]): number {
  const used = new Set(skills.map((s) => s.slot));
  for (let i = 0; i < MAX_SLOTS; i++) {
    if (!used.has(i)) return i;
  }
  return -1;
}

export default function SkillsSection() {
  const skills = useBuildWorkspaceStore((s) => s.build.skills);
  const characterClass = useBuildWorkspaceStore((s) => s.build.character_class);
  const mastery = useBuildWorkspaceStore((s) => s.build.mastery);
  const setSkills = useBuildWorkspaceStore((s) => s.setSkills);

  const handleAdd = useCallback(
    (skillName: string) => {
      if (skills.length >= MAX_SLOTS) return;
      const slot = nextSlotIndex(skills);
      if (slot < 0) return;
      const newSkill: BuildSkill = {
        id: `draft-${Date.now()}-${slot}`,
        slot,
        skill_name: skillName,
        points_allocated: 0,
        spec_tree: [],
      };
      setSkills([...skills, newSkill]);
    },
    [skills, setSkills],
  );

  const handleRemove = useCallback(
    (index: number) => {
      setSkills(skills.filter((_, i) => i !== index));
    },
    [skills, setSkills],
  );

  const handlePointsChange = useCallback(
    (index: number, points: number) => {
      setSkills(
        skills.map((s, i) =>
          i === index ? { ...s, points_allocated: points } : s,
        ),
      );
    },
    [skills, setSkills],
  );

  const handleTreeAlloc = useCallback(
    (skillIndex: number, nodeId: number, points: number) => {
      const current = skills[skillIndex];
      if (!current) return;
      const nextTree: number[] = [];
      // spec_tree holds one entry per invested point; rebuild to match `points`.
      for (let p = 0; p < points; p++) nextTree.push(nodeId);
      // Preserve other-node allocations from the existing spec_tree.
      const otherPoints = current.spec_tree.filter((id) => id !== nodeId);
      const rebuilt = [...otherPoints, ...nextTree];
      setSkills(
        skills.map((s, i) =>
          i === skillIndex ? { ...s, spec_tree: rebuilt } : s,
        ),
      );
    },
    [skills, setSkills],
  );

  return (
    <section data-testid="workspace-section-skills">
      <SkillSelector
        skills={skills}
        characterClass={characterClass}
        mastery={mastery}
        onAddSkill={handleAdd}
        onRemoveSkill={handleRemove}
        onPointsChange={handlePointsChange}
        onTreeAlloc={handleTreeAlloc}
      />
    </section>
  );
}
