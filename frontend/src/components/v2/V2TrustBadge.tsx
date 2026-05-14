import type { V2BadgeDefinition } from "@/lib/v2TrustStatus";
import { getSupportBadge, getTrustBadge } from "@/lib/v2TrustStatus";

type V2BadgeSize = "sm" | "md";

interface V2BadgeProps {
  badge: V2BadgeDefinition;
  size?: V2BadgeSize;
}

interface V2StatusBadgeProps {
  status?: unknown;
  size?: V2BadgeSize;
}

const TONE_CLASSES: Record<V2BadgeDefinition["tone"], string> = {
  amber: "border-amber-400/40 bg-amber-500/10 text-amber-200",
  blue: "border-sky-400/40 bg-sky-500/10 text-sky-200",
  gray: "border-gray-400/30 bg-gray-500/10 text-gray-300",
  green: "border-emerald-400/40 bg-emerald-500/10 text-emerald-200",
  purple: "border-violet-400/40 bg-violet-500/10 text-violet-200",
  red: "border-rose-400/40 bg-rose-500/10 text-rose-200",
  slate: "border-slate-400/40 bg-slate-500/10 text-slate-200",
};

export function V2TrustBadge({ status, size = "sm" }: V2StatusBadgeProps) {
  return <V2Badge badge={getTrustBadge(status)} size={size} />;
}

export function V2SupportBadge({ status, size = "sm" }: V2StatusBadgeProps) {
  return <V2Badge badge={getSupportBadge(status)} size={size} />;
}

export function V2Badge({ badge, size = "sm" }: V2BadgeProps) {
  const textSize = size === "sm" ? "text-[10px]" : "text-xs";
  const padding = size === "sm" ? "px-1.5 py-0.5" : "px-2 py-1";

  return (
    <span
      className={`inline-flex items-center rounded border font-medium ${padding} ${textSize} ${TONE_CLASSES[badge.tone]}`}
      title={badge.title}
      aria-label={`${badge.label}: ${badge.title}`}
    >
      {badge.label}
    </span>
  );
}
