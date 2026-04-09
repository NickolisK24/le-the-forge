/**
 * skillClassification.ts — Type definitions for skill classification and primary detection.
 */

/** Classification of a skill's role in a build */
export type SkillClassification = "damage" | "utility" | "minion";

/** Result of primary skill auto-detection from the backend */
export interface PrimarySkillDetection {
  /** Auto-detected primary damage skill name */
  primary_skill: string | null;
  /** Classification for each skill in the build */
  skill_classifications: Record<string, SkillClassification>;
  /** Whether the user has manually overridden the auto-detection */
  is_override: boolean;
}

/** Badge colors for each classification */
export const CLASSIFICATION_COLORS: Record<SkillClassification, string> = {
  damage: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  utility: "text-gray-400 bg-gray-400/10 border-gray-400/30",
  minion: "text-teal-400 bg-teal-400/10 border-teal-400/30",
};

/** Display labels for each classification */
export const CLASSIFICATION_LABELS: Record<SkillClassification, string> = {
  damage: "Damage",
  utility: "Utility",
  minion: "Minion",
};
