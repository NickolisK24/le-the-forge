/**
 * J18 — Data Loader Panel
 *
 * Triggers POST /api/load/game-data and displays the result:
 *   - Version detected
 *   - Loaded counts per data category
 *   - Integrity summary (errors / warnings)
 *   - Expandable issues list
 */

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Button, Spinner } from "@/components/ui";
import { gameDataApi, type GameDataLoadResult } from "@/lib/api";

interface Props {
  onLoaded?: (result: GameDataLoadResult) => void;
}

const labelCls =
  "block font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1";

function Badge({
  label,
  value,
  accent,
}: {
  label: string;
  value: string | number;
  accent?: boolean;
}) {
  return (
    <div className="text-center">
      <div className={labelCls}>{label}</div>
      <div
        className={`font-display text-xl ${accent ? "text-forge-amber" : "text-forge-text"}`}
      >
        {value}
      </div>
    </div>
  );
}

export default function DataLoaderPanel({ onLoaded }: Props) {
  const [showIssues, setShowIssues] = useState(false);

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await gameDataApi.loadGameData();
      if (res.errors) {
        throw new Error(res.errors[0]?.message ?? "Load failed");
      }
      return res.data!;
    },
    onSuccess: (data) => {
      toast.success("Game data reloaded successfully");
      onLoaded?.(data);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Game data reload failed");
    },
  });

  const result = mutation.data;

  return (
    <div className="space-y-4">
      {/* Trigger */}
      <div className="flex items-center gap-4">
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? (
            <span className="flex items-center gap-2">
              <Spinner size="sm" /> Loading…
            </span>
          ) : (
            "Reload Game Data"
          )}
        </Button>
        {result && (
          <span className="font-mono text-xs text-green-400">
            ✓ Loaded at {new Date().toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Result panel */}
      {result && (
        <div className="space-y-4">
          {/* Version */}
          <div className="rounded border border-forge-border bg-forge-surface p-3">
            <div className={labelCls}>Data Version</div>
            <div className="font-mono text-sm text-forge-amber">
              {result.version}
              <span className="text-forge-dim ml-2 text-[10px]">
                (from {result.version_source})
              </span>
            </div>
          </div>

          {/* Counts */}
          <div className="grid grid-cols-4 gap-3">
            <Badge label="Skills"   value={result.counts.skills ?? 0}   />
            <Badge label="Affixes"  value={result.counts.affixes ?? 0}  accent />
            <Badge label="Enemies"  value={result.counts.enemies ?? 0}  />
            <Badge label="Passives" value={result.counts.passives ?? 0} />
          </div>

          {/* Integrity summary */}
          <div className="rounded border border-forge-border bg-forge-surface p-3">
            <div className={labelCls}>Integrity</div>
            <div className="flex gap-6 font-mono text-sm">
              <span className="text-forge-dim">
                Total: <span className="text-forge-text">{result.integrity.total}</span>
              </span>
              <span className={result.integrity.errors > 0 ? "text-red-400" : "text-green-400"}>
                Errors: {result.integrity.errors}
              </span>
              <span className={result.integrity.warnings > 0 ? "text-yellow-400" : "text-forge-dim"}>
                Warnings: {result.integrity.warnings}
              </span>
            </div>
          </div>

          {/* Issues list */}
          {result.issues.length > 0 && (
            <div>
              <button
                type="button"
                className="font-mono text-xs text-forge-dim hover:text-forge-text mb-2"
                onClick={() => setShowIssues((s) => !s)}
              >
                {showIssues ? "▲ Hide" : "▼ Show"} {result.issues.length} issue
                {result.issues.length !== 1 ? "s" : ""}
              </button>

              {showIssues && (
                <div className="rounded border border-forge-border bg-forge-surface2 p-2 space-y-1 max-h-64 overflow-y-auto">
                  {result.issues.map((issue, i) => (
                    <div key={i} className="flex gap-3 font-mono text-xs">
                      <span
                        className={
                          issue.severity === "error"
                            ? "text-red-400 w-14 shrink-0"
                            : "text-yellow-400 w-14 shrink-0"
                        }
                      >
                        {issue.severity.toUpperCase()}
                      </span>
                      <span className="text-forge-dim w-20 shrink-0 truncate">
                        {issue.category}
                      </span>
                      <span className="text-forge-text">{issue.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
