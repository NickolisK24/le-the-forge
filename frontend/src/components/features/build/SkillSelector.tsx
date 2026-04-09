/**
 * SkillSelector — 5 skill slot bar with expandable skill tree panels.
 *
 * Clicking a slot toggles the SkillTreePanel below (one at a time).
 * For saved builds (buildSlug provided), tree data and allocations
 * are fetched from the API. For unsaved builds, the renderer is used
 * directly with local allocation data.
 */

import { useState, useMemo } from "react";

import { CLASS_SKILLS, type SkillDef } from "@/lib/gameData";
import type { CharacterClass } from "@/types";
import { getSkillCode, resolveSkillName } from "@/data/skillTrees";
import SkillTreePanel from "./SkillTreePanel";

interface SkillSlot {
  skill_name: string;
  slot: number;
  points_allocated: number;
  spec_tree?: number[];
}

interface Props {
  skills: SkillSlot[];
  characterClass: CharacterClass;
  mastery: string;
  buildSlug?: string;
  readOnly?: boolean;
}

const MAX_SLOTS = 5;

export default function SkillSelector({
  skills,
  characterClass,
  mastery,
  buildSlug,
  readOnly,
}: Props) {
  const [activeSlot, setActiveSlot] = useState<number | null>(null);

  // Build a lookup of skill defs for icons (case-insensitive)
  const skillDefs = useMemo(() => {
    const map: Record<string, SkillDef> = {};
    for (const s of CLASS_SKILLS[characterClass] ?? []) {
      map[s.name.toLowerCase()] = s;
    }
    return map;
  }, [characterClass]);

  const activeSkill = activeSlot !== null ? skills[activeSlot] : null;
  const activeSkillId = activeSkill ? getSkillCode(activeSkill.skill_name) : null;

  function handleSlotClick(index: number) {
    setActiveSlot((prev) => (prev === index ? null : index));
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Slot bar */}
      <div className="flex gap-2 flex-wrap">
        {Array.from({ length: MAX_SLOTS }, (_, i) => {
          const skill = skills[i];
          const displayName = skill ? resolveSkillName(skill.skill_name) : null;
          const def = displayName ? skillDefs[displayName.toLowerCase()] : null;
          const isActive = activeSlot === i;
          const hasTree = skill ? !!getSkillCode(skill.skill_name) : false;

          return (
            <button
              key={i}
              onClick={() => skill && handleSlotClick(i)}
              disabled={!skill}
              className={`
                flex items-center gap-2 rounded border px-3 py-2 transition-colors min-w-0
                ${isActive
                  ? "border-forge-amber bg-forge-amber/10 text-forge-amber"
                  : skill
                    ? "border-forge-border bg-forge-surface2 text-forge-text hover:border-forge-amber/50 hover:text-forge-amber"
                    : "border-forge-border/40 bg-forge-surface2/50 text-forge-dim cursor-default"
                }
              `}
              title={skill ? `${displayName} — click to ${isActive ? "hide" : "show"} skill tree` : `Slot ${i + 1} — empty`}
            >
              <span className="text-base leading-none flex-shrink-0">
                {def?.icon ?? (skill ? "?" : "·")}
              </span>
              <span className="font-body text-xs truncate">
                {displayName ?? `Slot ${i + 1}`}
              </span>
              {skill && (
                <span className="font-mono text-[10px] text-forge-dim flex-shrink-0">
                  Slot {i + 1} · {skill.points_allocated} pts
                  {(() => {
                    if (!skill.spec_tree?.length) return null;
                    const counts: Record<number, number> = {};
                    for (const id of skill.spec_tree) counts[id] = (counts[id] ?? 0) + 1;
                    const total = Object.values(counts).reduce((a, b) => a + b, 0);
                    return total > 0 ? <span className="ml-1 text-forge-amber">· {total} nodes</span> : null;
                  })()}
                </span>
              )}
              {hasTree && (
                <span className={`text-[10px] flex-shrink-0 ${isActive ? "text-forge-amber" : "text-forge-dim"}`}>
                  {isActive ? "▲" : "▼"}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Expanded skill tree panel */}
      {activeSkill && activeSkillId && buildSlug && (
        <div className="rounded border border-forge-border bg-forge-bg">
          <SkillTreePanel
            skillId={activeSkillId}
            buildSlug={buildSlug}
            skillName={activeSkill.skill_name}
            readOnly={readOnly}
          />
        </div>
      )}

      {activeSkill && !activeSkillId && (
        <div className="rounded border border-forge-border bg-forge-surface2 px-4 py-8 text-center">
          <span className="font-mono text-xs text-forge-dim">
            No tree data available for {resolveSkillName(activeSkill.skill_name)}
          </span>
        </div>
      )}

      {activeSkill && activeSkillId && !buildSlug && (
        <div className="rounded border border-forge-border bg-forge-surface2 px-4 py-8 text-center">
          <span className="font-mono text-xs text-forge-dim">
            Save the build first to use the interactive skill tree
          </span>
        </div>
      )}
    </div>
  );
}
