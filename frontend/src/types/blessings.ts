/**
 * Monolith of Fate Blessings — frontend types.
 *
 * These mirror the backend blessing registry returned by
 * `GET /api/ref/blessings` and the persisted `Build.blessings` array.
 */

/**
 * A single blessing definition as shipped in the reference registry.
 *
 * `stat_type` controls how the value folds into the resolved stat pool:
 *   - "flat"      → additive onto the target stat
 *   - "increased" → additive-percent pool
 *   - "more"      → multiplicative
 *   - "dual"      → applies to every key in `stat_keys`
 *   - "drop_rate" → non-combat (skipped by the simulator)
 */
export interface BlessingDefinition {
  id: string;
  name: string;
  grand_name: string;
  simulation_relevant: boolean;
  stat_key: string;
  stat_type: string;
  normal_min: number;
  normal_max: number;
  grand_min: number;
  grand_max: number;
  description?: string;
  stat_keys?: string[];
}

/**
 * A Monolith timeline (one of ten) and the blessings that may drop in it.
 */
export interface BlessingTimeline {
  id: string;
  name: string;
  level: number;
  order: number;
  blessings: BlessingDefinition[];
}

/**
 * A single selected blessing as persisted on a Build.
 *
 * `value` is the rolled magnitude (player choice anywhere between the
 * normal/grand min and max of the chosen blessing).
 */
export interface SelectedBlessing {
  timeline_id: string;
  blessing_id: string;
  is_grand: boolean;
  value: number;
}
