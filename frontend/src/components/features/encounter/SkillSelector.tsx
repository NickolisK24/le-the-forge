/**
 * E10 — Skill Selector
 *
 * Selects character class, mastery, skill, and skill level.
 */

import type { BuildDefinition, CharacterClass } from "@/services/buildApi";
import { CLASSES, CLASS_MASTERIES } from "@/services/buildApi";

// Representative skill list — a broader list would come from an API endpoint
const SKILLS_BY_CLASS: Record<CharacterClass, string[]> = {
  Acolyte:   ["Rip Blood", "Bone Curse", "Hungering Souls", "Harvest", "Drain Life", "Death Seal"],
  Mage:      ["Glacier", "Glacial Bolt", "Frost Wall", "Lightning Blast", "Flame Rush", "Fireball"],
  Primalist: ["Maelstrom", "Tornado", "Upheaval", "Swipe", "Summon Wolf", "Entangling Roots"],
  Sentinel:  ["Lunge", "Judgement", "Holy Aura", "Rive", "Volatile Reversal", "Warpath"],
  Rogue:     ["Shuriken Throw", "Shift", "Smoke Bomb", "Flurry", "Arrow Storm", "Cinder Strike"],
};

type BuildFields = Pick<BuildDefinition, "character_class" | "mastery" | "skill_id" | "skill_level">;

interface Props {
  values: BuildFields;
  onChange: (patch: Partial<BuildFields>) => void;
  disabled?: boolean;
}

function Select({
  label, value, options, disabled, onChange,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  disabled?: boolean;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-forge-muted uppercase tracking-wide">{label}</label>
      <select
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="
          w-full rounded border border-forge-border bg-forge-input
          px-3 py-2 text-sm text-forge-text
          focus:border-forge-accent focus:outline-none
          disabled:opacity-50
        "
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

export default function SkillSelector({ values, onChange, disabled }: Props) {
  const masteries = CLASS_MASTERIES[values.character_class] ?? [];
  const skills    = SKILLS_BY_CLASS[values.character_class] ?? [];

  function handleClassChange(cls: string) {
    const newClass    = cls as CharacterClass;
    const newMastery  = CLASS_MASTERIES[newClass]?.[0] ?? "";
    const newSkill    = SKILLS_BY_CLASS[newClass]?.[0] ?? "";
    onChange({ character_class: newClass, mastery: newMastery, skill_id: newSkill });
  }

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Class &amp; Skill
      </h3>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Select
          label="Class"
          value={values.character_class}
          options={CLASSES.map((c) => ({ value: c, label: c }))}
          disabled={disabled}
          onChange={handleClassChange}
        />
        <Select
          label="Mastery"
          value={values.mastery}
          options={masteries.map((m) => ({ value: m, label: m }))}
          disabled={disabled}
          onChange={(m) => onChange({ mastery: m })}
        />
        <Select
          label="Skill"
          value={values.skill_id}
          options={skills.map((s) => ({ value: s, label: s }))}
          disabled={disabled}
          onChange={(s) => onChange({ skill_id: s })}
        />
        <div className="flex flex-col gap-1">
          <label className="text-xs text-forge-muted uppercase tracking-wide">
            Skill Level
          </label>
          <input
            type="number"
            min={1}
            max={40}
            step={1}
            value={values.skill_level}
            disabled={disabled}
            onChange={(e) => {
              const v = parseInt(e.target.value, 10);
              if (!isNaN(v) && v >= 1 && v <= 40) onChange({ skill_level: v });
            }}
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-sm text-forge-text
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50
            "
          />
        </div>
      </div>
    </section>
  );
}
