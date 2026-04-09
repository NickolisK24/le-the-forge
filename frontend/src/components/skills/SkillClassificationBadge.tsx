import type { SkillClassification } from "@/types/skillClassification";
import {
  CLASSIFICATION_COLORS,
  CLASSIFICATION_LABELS,
} from "@/types/skillClassification";

interface SkillClassificationBadgeProps {
  classification: SkillClassification;
  size?: "sm" | "md";
}

export function SkillClassificationBadge({
  classification,
  size = "sm",
}: SkillClassificationBadgeProps) {
  const colors = CLASSIFICATION_COLORS[classification];
  const label = CLASSIFICATION_LABELS[classification];
  const textSize = size === "sm" ? "text-[10px]" : "text-xs";

  return (
    <span
      className={`inline-flex items-center rounded border px-1.5 py-0.5 font-medium ${textSize} ${colors}`}
    >
      {label}
    </span>
  );
}
