/**
 * BIS Search API service — connects the BIS search UI to the backend engine.
 */

const BASE = import.meta.env.VITE_API_URL ?? "/api";

export interface BisSearchRequest {
  slots: string[];
  target_affixes: string[];
  target_tiers: Record<string, number>;
  top_n?: number;
  max_candidates?: number;
}

export interface BisSearchResultEntry {
  rank: number;
  build_id: string;
  score: number;
  percentile: number;
}

export interface BisSearchResponse {
  search_id: string;
  total_evaluated: number;
  best_score: number;
  duration_s: number;
  results: BisSearchResultEntry[];
}

export async function runBisSearch(
  req: BisSearchRequest,
): Promise<BisSearchResponse> {
  const res = await fetch(`${BASE}/bis/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `BIS search failed (${res.status})`);
  }

  return res.json();
}
