export const SUPPORT_STATUSES = [
  "trusted",
  "partial",
  "text_only",
  "unsupported",
  "experimental",
  "unknown",
] as const;

export type SupportStatus = (typeof SUPPORT_STATUSES)[number];

export const TRUST_LEVELS = [
  "game_extracted",
  "generated_from_game_data",
  "manual_bridge",
  "inferred",
  "placeholder",
  "deprecated",
] as const;

export type TrustLevel = (typeof TRUST_LEVELS)[number];

export function isStableCalculableStatus(status: SupportStatus): boolean {
  return status === "trusted";
}
