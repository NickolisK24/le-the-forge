/**
 * Buff ID → human-readable label mapping.
 *
 * The backend identifies buffs by snake_case IDs (e.g. "power_surge").
 * Use `buffLabel(id)` to render them in the UI. Unknown IDs are title-cased
 * as a fallback so we never show raw snake_case in a user-facing surface.
 */

export const BUFF_LABELS: Record<string, string> = {
  frenzy:       "Frenzy",
  conviction:   "Conviction",
  power_surge:  "Power Surge",
  exposure:     "Exposure",
  haste:        "Haste",
  warcry:       "Warcry",
  rage:         "Rage",
  rampage:      "Rampage",
  shred_armor:  "Shred Armor",
  mark_for_death: "Mark for Death",
};

/**
 * Return the human-readable label for a buff ID. Falls back to a title-cased
 * version of the raw ID if it isn't in the lookup table.
 */
export function buffLabel(id: string): string {
  if (BUFF_LABELS[id]) return BUFF_LABELS[id];
  return id
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}
