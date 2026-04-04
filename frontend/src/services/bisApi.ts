/**
 * BIS Search API service — connects the BIS search UI to the backend engine.
 *
 * Uses the shared API client for auth token injection and error handling.
 */

import { apiPost } from "@/lib/api";

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
  const res = await apiPost<BisSearchResponse>("/bis/search", req);
  if (res.errors) {
    throw new Error(res.errors[0]?.message ?? "BIS search failed");
  }
  if (!res.data) {
    throw new Error("Empty response from BIS search");
  }
  return res.data;
}
