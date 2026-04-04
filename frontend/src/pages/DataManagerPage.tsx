/**
 * J18 — Data Manager Page
 *
 * Route: /data-manager
 *
 * Allows admins / power users to:
 *   - Inspect the current loaded data version
 *   - Trigger a live reload of all game data
 *   - View per-category load counts
 *   - Review validation issues surfaced by the integrity logger
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Panel, SectionLabel } from "@/components/ui";
import DataLoaderPanel from "@/components/DataLoaderPanel";
import { gameDataApi, type GameDataLoadResult } from "@/lib/api";

const labelCls =
  "block font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1";

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-forge-border/40 last:border-0">
      <span className="font-mono text-xs text-forge-dim">{label}</span>
      <span className="font-mono text-xs text-forge-text">{value}</span>
    </div>
  );
}

export default function DataManagerPage() {
  const [lastResult, setLastResult] = useState<GameDataLoadResult | null>(null);

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <h1 className="font-display text-2xl text-forge-text">Data Manager</h1>
      <p className="font-body text-sm text-forge-dim">
        Manage and inspect the game-data pipeline. Reload data to pick up
        changes to JSON files without restarting the server.
      </p>

      {/* Loader panel */}
      <Panel>
        <SectionLabel>Data Pipeline</SectionLabel>
        <DataLoaderPanel onLoaded={setLastResult} />
      </Panel>

      {/* Last load summary */}
      {lastResult && (
        <Panel>
          <SectionLabel>Last Load Summary</SectionLabel>
          <div className="space-y-0.5">
            <StatRow label="Version"       value={lastResult.version} />
            <StatRow label="Version Source" value={lastResult.version_source} />
            <StatRow label="Skills loaded"  value={lastResult.counts.skills ?? 0} />
            <StatRow label="Affixes loaded" value={lastResult.counts.affixes ?? 0} />
            <StatRow label="Enemies loaded" value={lastResult.counts.enemies ?? 0} />
            <StatRow label="Passives loaded" value={lastResult.counts.passives ?? 0} />
            <StatRow label="Integrity errors"   value={lastResult.integrity.errors} />
            <StatRow label="Integrity warnings" value={lastResult.integrity.warnings} />
            <StatRow label="Total log entries"  value={lastResult.integrity.total} />
          </div>
        </Panel>
      )}

      {/* Info panel */}
      <Panel>
        <SectionLabel>About This Page</SectionLabel>
        <ul className="font-body text-sm text-forge-dim space-y-2 list-disc list-inside">
          <li>
            <strong className="text-forge-text">Reload Game Data</strong> — triggers
            a hot-reload of all JSON bundles (skills, affixes, enemies, passives)
            without restarting the Flask server.
          </li>
          <li>
            <strong className="text-forge-text">Version detection</strong> — reads
            the <code className="text-forge-amber">_version</code> or{" "}
            <code className="text-forge-amber">_meta.version</code> field from the
            affixes bundle.
          </li>
          <li>
            <strong className="text-forge-text">Integrity log</strong> — surfaces
            mapping warnings and errors found during the load pass (e.g. missing
            fields, out-of-range values).
          </li>
        </ul>
      </Panel>
    </div>
  );
}
