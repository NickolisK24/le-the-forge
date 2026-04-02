/**
 * Passive tree service — fetches live passive node data from the backend API.
 * Types mirror the PassiveNode ORM model returned by /api/passives.
 */

const BASE = import.meta.env.VITE_API_URL ?? "/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PassiveNodeStat {
  key: string;
  value: string | number;
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
  node_type: string;      // "core" (max_points > 1) or "notable" (max_points === 1)
  x: number;
  y: number;
  max_points: number;
  connections: string[];  // IDs of parent/adjacent nodes
  stats: PassiveNodeStat[];
  ability_granted: string | null;
  icon: string | null;
}

export interface PassiveTreeResponse {
  class: string | null;
  mastery: string | null;
  count: number;
  nodes: PassiveNode[];
}

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

async function _get(path: string): Promise<PassiveTreeResponse> {
  const res = await fetch(`${BASE}${path}`);
  let json: any;
  try {
    json = await res.json();
  } catch {
    throw new Error(`Server error (${res.status}) — invalid response from ${path}`);
  }
  if (!res.ok) {
    throw new Error(json.errors?.[0]?.message ?? `Request failed: ${path}`);
  }
  return json.data as PassiveTreeResponse;
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
