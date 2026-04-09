import { useState } from "react";
import type { SkillClassification } from "@/types/skillClassification";
import { SkillClassificationBadge } from "./SkillClassificationBadge";

interface SkillEntry {
  skill_name: string;
  slot: number;
  classification: SkillClassification;
}

interface PrimarySkillSelectorProps {
  /** All skills in the build */
  skills: SkillEntry[];
  /** Auto-detected primary skill name */
  detectedPrimary: string | null;
  /** Currently active primary (may be overridden) */
  activePrimary: string | null;
  /** Whether the current selection is a manual override */
  isOverride: boolean;
  /** Called when the user selects a different primary skill */
  onOverride: (skillName: string) => void;
  /** Called when the user resets to auto-detection */
  onResetToAuto: () => void;
}

export function PrimarySkillSelector({
  skills,
  detectedPrimary,
  activePrimary,
  isOverride,
  onOverride,
  onResetToAuto,
}: PrimarySkillSelectorProps) {
  const [showDropdown, setShowDropdown] = useState(false);

  if (!skills.length) {
    return (
      <div className="text-sm text-gray-500">No skills selected</div>
    );
  }

  const primaryName = activePrimary || detectedPrimary || skills[0]?.skill_name;
  const primaryClassification =
    skills.find((s) => s.skill_name === primaryName)?.classification ?? "damage";

  // Sort: damage first, then utility, then minion
  const sortOrder: Record<SkillClassification, number> = {
    damage: 0,
    utility: 1,
    minion: 2,
  };
  const sortedSkills = [...skills].sort(
    (a, b) =>
      sortOrder[a.classification] - sortOrder[b.classification] ||
      a.slot - b.slot
  );

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 uppercase tracking-wider">
        Analyzing:
      </span>
      <span className="text-sm font-semibold text-white">
        {primaryName}
      </span>
      <SkillClassificationBadge
        classification={primaryClassification}
        size="sm"
      />
      <span className="text-[10px] text-gray-500">
        {isOverride ? "(manual)" : "(auto)"}
      </span>

      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="text-xs text-amber-400/70 hover:text-amber-400 transition-colors"
        >
          Change
        </button>

        {showDropdown && (
          <div className="absolute top-full left-0 mt-1 z-50 w-56 rounded-md border border-gray-700 bg-gray-900 shadow-lg">
            <div className="py-1">
              {isOverride && (
                <button
                  onClick={() => {
                    onResetToAuto();
                    setShowDropdown(false);
                  }}
                  className="w-full px-3 py-1.5 text-left text-xs text-amber-400 hover:bg-gray-800 border-b border-gray-700"
                >
                  Reset to auto-detect
                </button>
              )}
              {sortedSkills.map((skill) => (
                <button
                  key={skill.skill_name}
                  onClick={() => {
                    onOverride(skill.skill_name);
                    setShowDropdown(false);
                  }}
                  className={`w-full px-3 py-1.5 text-left text-xs hover:bg-gray-800 flex items-center justify-between ${
                    skill.skill_name === primaryName
                      ? "text-white bg-gray-800"
                      : "text-gray-300"
                  }`}
                >
                  <span>
                    {skill.skill_name}
                    {skill.skill_name === detectedPrimary && (
                      <span className="ml-1 text-[9px] text-gray-500">
                        (auto)
                      </span>
                    )}
                  </span>
                  <SkillClassificationBadge
                    classification={skill.classification}
                    size="sm"
                  />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
