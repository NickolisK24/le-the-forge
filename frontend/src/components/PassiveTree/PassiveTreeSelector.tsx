/**
 * PassiveTreeSelector — tab-based mastery tree selector.
 *
 * Renders tabs: Base | Mastery1 | Mastery2 | Mastery3
 * Each tab shows only nodes from that tree section.
 * Base tab shows base-class nodes only (mastery === null).
 * Mastery tabs show that mastery's nodes only (NOT combined with base).
 *
 * This prevents the coordinate overlap that occurs when all sections
 * are rendered on a single canvas (they share x/y ranges in-game).
 */

interface PassiveTreeSelectorProps {
  /** Mastery names for the selected class (e.g. ["Necromancer", "Lich", "Warlock"]) */
  masteries: string[];
  /** Currently active tab: "__base__" or a mastery name */
  activeTab: string;
  /** Called when a tab is clicked */
  onTabChange: (tab: string) => void;
  /** Point counts per section for the budget badges */
  pointsBySection?: Record<string, number>;
  /** Whether the user has committed to a mastery (disables other mastery tabs) */
  lockedMastery?: string | null;
}

export default function PassiveTreeSelector({
  masteries,
  activeTab,
  onTabChange,
  pointsBySection = {},
  lockedMastery,
}: PassiveTreeSelectorProps) {
  const tabs = ["__base__", ...masteries];

  return (
    <div className="flex items-stretch gap-0 rounded-t border border-b-0 border-forge-border bg-forge-surface overflow-x-auto whitespace-nowrap">
      {tabs.map((tab) => {
        const isActive = activeTab === tab;
        const label = tab === "__base__" ? "Base" : tab;
        const points = pointsBySection[tab] ?? 0;
        const isLocked =
          lockedMastery &&
          tab !== "__base__" &&
          tab !== lockedMastery;

        return (
          <button
            key={tab}
            onClick={() => !isLocked && onTabChange(tab)}
            disabled={!!isLocked}
            className={`
              relative flex shrink-0 items-center gap-1.5 px-4 py-2 font-mono text-xs transition-colors min-h-[44px]
              ${isActive
                ? "bg-forge-surface2 text-forge-amber font-semibold border-b-2 border-forge-amber"
                : isLocked
                  ? "text-forge-dim/40 cursor-not-allowed"
                  : "text-forge-dim hover:text-forge-muted hover:bg-forge-surface2/50 cursor-pointer"
              }
            `}
            title={
              isLocked
                ? `Locked — you chose ${lockedMastery}`
                : `View ${label} passive tree`
            }
          >
            <span>{label}</span>
            {points > 0 && (
              <span
                className={`rounded-full px-1.5 py-0.5 text-[9px] font-bold leading-none ${
                  isActive
                    ? "bg-forge-amber/20 text-forge-amber"
                    : "bg-forge-surface2 text-forge-dim"
                }`}
              >
                {points}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
