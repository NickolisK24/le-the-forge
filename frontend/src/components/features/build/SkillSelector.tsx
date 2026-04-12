/**
 * SkillSelector — unified skills section with 5 slots, point allocation,
 * and per-slot expandable skill tree panels.
 *
 * Clicking a slot row toggles the SkillTreePanel below (one at a time).
 * For saved builds (buildSlug provided), tree data and allocations are
 * fetched from the API. For unsaved builds, the renderer is used directly
 * with local allocation data.
 *
 * When edit-mode handlers (onAddSkill / onRemoveSkill / onPointsChange) are
 * supplied, the component also renders:
 *   - an inline points input per filled slot
 *   - a remove (✕) button per filled slot
 *   - an "Add skill" picker below the slot list, for empty slots
 *
 * Without those handlers the component stays read-only (view mode).
 */

import { useState, useMemo } from "react";

import { CLASS_SKILLS, type SkillDef } from "@/lib/gameData";
import type { CharacterClass } from "@/types";
import { getSkillCode, hasSkillTree, resolveSkillName } from "@/data/skillTrees";
import SkillTreePanel from "./SkillTreePanel";
import SkillTreeDraftPanel from "./SkillTreeDraftPanel";

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
  /** Called when the user picks a skill from the add-picker. */
  onAddSkill?: (skillName: string) => void;
  /** Called when the user clicks a slot's remove (✕) button. */
  onRemoveSkill?: (index: number) => void;
  /** Called when the user edits a slot's points input. */
  onPointsChange?: (index: number, points: number) => void;
  /**
   * Called when the user allocates/deallocates a node on the draft-mode
   * skill tree (buildSlug absent). `points` is the new total for that node;
   * callers should rebuild `spec_tree` accordingly.
   */
  onTreeAlloc?: (skillIndex: number, nodeId: number, points: number) => void;
  /** Max value for the points input. Default 30 (base cap 20, +10 for gear). */
  maxSkillLevel?: number;
}

const MAX_SLOTS = 5;
const DEFAULT_MAX_SKILL_LEVEL = 30;

export default function SkillSelector({
  skills,
  characterClass,
  mastery,
  buildSlug,
  readOnly,
  onAddSkill,
  onRemoveSkill,
  onPointsChange,
  onTreeAlloc,
  maxSkillLevel = DEFAULT_MAX_SKILL_LEVEL,
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

  const editable = Boolean(onAddSkill || onRemoveSkill || onPointsChange) && !readOnly;

  const selectedNames = useMemo(
    () => new Set(skills.map((s) => s.skill_name)),
    [skills],
  );
  const availableSkills = useMemo(
    () => (CLASS_SKILLS[characterClass] ?? []).filter(
      (s) => !s.mastery || s.mastery === mastery,
    ),
    [characterClass, mastery],
  );

  function handleSlotClick(index: number) {
    setActiveSlot((prev) => (prev === index ? null : index));
  }

  const hasEmptySlot = skills.length < MAX_SLOTS;
  const showAddPicker = editable && Boolean(onAddSkill) && hasEmptySlot;

  return (
    <div className="flex flex-col gap-2">
      {/* Slot rows — one per slot (up to MAX_SLOTS). Filled rows show
          points + expand + remove; empty rows show a subtle placeholder
          that hints to the add-picker below. */}
      <div className="flex flex-col gap-1.5">
        {Array.from({ length: MAX_SLOTS }, (_, i) => {
          const skill = skills[i];
          const displayName = skill ? resolveSkillName(skill.skill_name) : null;
          const def = displayName ? skillDefs[displayName.toLowerCase()] : null;
          const isActive = activeSlot === i;
          const skillHasTree = skill ? hasSkillTree(skill.skill_name) : false;

          if (!skill) {
            return (
              <div
                key={i}
                className="flex items-center gap-3 rounded border border-dashed border-forge-border/50 bg-forge-surface2/30 px-3 py-2"
              >
                <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim/60 flex-shrink-0">
                  Slot {i + 1}
                </span>
                <span className="flex-1 font-body text-xs text-forge-dim/70">
                  {showAddPicker ? "Empty — pick a skill below" : "Empty"}
                </span>
              </div>
            );
          }

          return (
            <div
              key={i}
              onClick={() => handleSlotClick(i)}
              className={`
                flex items-center gap-3 rounded border px-3 py-2 transition-colors min-w-0 cursor-pointer
                ${isActive
                  ? "border-forge-amber bg-forge-amber/10"
                  : "border-forge-border bg-forge-surface2 hover:border-forge-amber/50"
                }
              `}
              title={`${displayName} — click to ${isActive ? "collapse" : "expand"} skill tree`}
            >
              <span className="text-base leading-none flex-shrink-0">
                {def?.icon ?? "?"}
              </span>
              <div className="flex min-w-0 flex-1 flex-col">
                <span className={`font-body text-sm truncate ${isActive ? "text-forge-amber" : "text-forge-text"}`}>
                  {displayName}
                </span>
                <span className="font-mono text-[10px] text-forge-dim">
                  Slot {i + 1} · {skill.points_allocated} pts
                  {(() => {
                    if (!skill.spec_tree?.length) return null;
                    const total = skill.spec_tree.length;
                    return total > 0 ? <span className="ml-1 text-forge-amber">· {total} nodes</span> : null;
                  })()}
                </span>
              </div>
              {editable && onPointsChange ? (
                <input
                  type="number"
                  min={0}
                  max={maxSkillLevel}
                  value={skill.points_allocated}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => {
                    const n = Math.min(maxSkillLevel, Math.max(0, Number(e.target.value) || 0));
                    onPointsChange(i, n);
                  }}
                  className="w-14 rounded-sm border border-forge-border bg-forge-bg px-2 py-0.5 font-mono text-xs text-forge-text outline-none focus:border-forge-amber/60 text-center flex-shrink-0"
                  title={`Skill level (0–${maxSkillLevel}; base cap 20, gear can push higher)`}
                />
              ) : null}
              {skillHasTree && (
                <span
                  className={`font-mono text-[10px] flex-shrink-0 ${isActive ? "text-forge-amber" : "text-forge-dim"}`}
                  aria-label={isActive ? "collapse tree" : "expand tree"}
                >
                  {isActive ? "▲" : "▼"}
                </span>
              )}
              {editable && onRemoveSkill && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveSkill(i);
                    if (activeSlot === i) setActiveSlot(null);
                  }}
                  className="text-forge-dim hover:text-red-400 transition-colors font-mono text-xs leading-none flex-shrink-0"
                  title="Remove skill"
                >
                  ✕
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Expanded skill tree panel. Saved builds go through the API-backed
          SkillTreePanel; draft builds use the local-state SkillTreeDraftPanel
          so point allocation works before the build is saved. */}
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

      {activeSkill && activeSkillId && !buildSlug && activeSlot !== null && (
        <div className="rounded border border-forge-border bg-forge-bg">
          <SkillTreeDraftPanel
            skillId={activeSkillId}
            skillName={activeSkill.skill_name}
            specTree={activeSkill.spec_tree ?? []}
            onAllocate={
              onTreeAlloc
                ? (nodeId, points) => onTreeAlloc(activeSlot, nodeId, points)
                : () => {}
            }
            readOnly={readOnly || !onTreeAlloc}
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

      {/* Add-skill picker — unified with the slot list, not a separate
          section. Only shown when editable and at least one slot is open. */}
      {showAddPicker && onAddSkill && (
        <div className="rounded border border-forge-border/60 bg-forge-surface2/40 px-3 py-2">
          <div className="flex items-baseline justify-between gap-3 mb-1.5">
            <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
              Add skill
            </span>
            <span className="font-mono text-[10px] text-forge-dim/70">
              {characterClass} · {mastery}
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {availableSkills
              .filter((s) => !selectedNames.has(s.name))
              .map((s) => (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => onAddSkill(s.name)}
                  title={s.tags.join(", ")}
                  className="flex items-center gap-1.5 rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1 font-body text-xs text-forge-text hover:border-forge-amber/60 hover:text-forge-amber transition-colors"
                >
                  <span>{s.icon}</span>
                  <span>{s.name}</span>
                  {s.mastery && (
                    <span className="font-mono text-[9px] text-forge-dim opacity-70">{s.mastery}</span>
                  )}
                </button>
              ))}
          </div>
          {skills.length === 0 && (
            <p className="mt-1.5 font-body text-[11px] text-forge-dim">
              Pick up to {MAX_SLOTS} skills. Base cap is 20; gear can raise it further.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
