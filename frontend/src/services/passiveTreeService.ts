/**
 * Passive tree service — fetches live passive node data from the backend API.
 *
 * Uses the shared API client for auth token injection and error handling.
 * Types mirror the PassiveNode ORM model returned by /api/passives.
 */

import { apiGet } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PassiveNodeStat {
  key: string;
  value: string | number;
}

export interface PassiveRequirement {
  parent_id: string;
  points: number;
}

export interface PassiveNode {
  id: string;             // namespaced, e.g. "ac_0"
  raw_node_id: number;
  character_class: string;
  mastery: string | null; // null = base class node
  mastery_index: number;  // 0 = base, 1/2/3 = masteries in order
  mastery_requirement: number;
  name: string;
  description: string | null;
  node_type: string;      // "core" or "notable"
  x: number;
  y: number;
  max_points: number;
  connections: string[];  // symmetric neighbor ids (for rendering)
  requires: PassiveRequirement[]; // directed parents with point thresholds
  stats: PassiveNodeStat[];
  ability_granted: string | null;
  icon: string | null;
}

export interface PassiveTreeResponse {
  class: string | null;
  mastery: string | null;
  count: number;
  nodes: PassiveNode[];
  /** Nodes grouped by tree section: "__base__" | mastery name */
  grouped?: Record<string, PassiveNode[]>;
}

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

async function _get(path: string): Promise<PassiveTreeResponse> {
  const res = await apiGet<PassiveTreeResponse>(path);
  if (res.errors) {
    throw new Error(res.errors[0]?.message ?? `Request failed: ${path}`);
  }
  if (!res.data) {
    throw new Error(`Empty response from ${path}`);
  }
  return res.data;
}

/** Fetch the full passive tree for a character class (all masteries). */
export function fetchClassTree(characterClass: string): Promise<PassiveTreeResponse> {
  return _get(`/passives/${encodeURIComponent(characterClass)}`);
}

/** Fetch base class nodes + nodes for the selected mastery. */
export function fetchMasteryTree(
  characterClass: string,
  mastery: string,
): Promise<PassiveTreeResponse> {
  return _get(
    `/passives/${encodeURIComponent(characterClass)}/${encodeURIComponent(mastery)}`,
  );
}
