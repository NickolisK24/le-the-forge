/**
 * O12 — ExportPanel
 *
 * Provides three export actions: Download JSON, Copy Build String, Copy Share Link.
 */

import { useState } from "react";

export type ExportBuild = {
  build_name: string;
  character_class: string;
  version: string;
  skills: any[];
  gear: any[];
  passives: any[];
};

interface ExportPanelProps {
  build: ExportBuild | null;
}

function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash += str.charCodeAt(i);
  }
  return hash % 999999;
}

export default function ExportPanel({ build }: ExportPanelProps) {
  const [flash, setFlash] = useState<string | null>(null);

  function showFlash(msg: string, duration = 2000) {
    setFlash(msg);
    setTimeout(() => setFlash(null), duration);
  }

  function handleDownloadJson() {
    if (!build) return;
    const blob = new Blob([JSON.stringify(build, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${build.build_name}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleCopyBuildString() {
    if (!build) return;
    const encoded = btoa(JSON.stringify(build));
    navigator.clipboard.writeText(encoded).then(() => showFlash("Copied!"));
  }

  function handleCopyShareLink() {
    if (!build) return;
    const hashCode = simpleHash(JSON.stringify(build));
    const link = `https://le-the-forge.app/share/${hashCode}`;
    navigator.clipboard.writeText(link).then(() => showFlash("Link copied!"));
  }

  if (!build) {
    return (
      <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-6 flex items-center justify-center">
        <p className="text-gray-400 text-sm">No build loaded</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-4">
      <h2 className="font-display text-lg text-[#f5a623]">Export Build</h2>

      {/* Build info card */}
      <div className="rounded border border-[#2a3050] bg-[#0d1120] p-3 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-xs w-16">Name</span>
          <span className="text-gray-100 text-sm font-medium">{build.build_name}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-xs w-16">Class</span>
          <span className="text-[#22d3ee] text-sm">{build.character_class}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-xs w-16">Version</span>
          <span className="text-gray-300 text-sm">{build.version}</span>
        </div>
      </div>

      {/* Export buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleDownloadJson}
          className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
        >
          Download JSON
        </button>
        <button
          onClick={handleCopyBuildString}
          className="px-4 py-2 rounded border border-[#f5a623] text-[#f5a623] text-sm font-semibold hover:bg-[#f5a623]/10 transition-colors"
        >
          Copy Build String
        </button>
        <button
          onClick={handleCopyShareLink}
          className="px-4 py-2 rounded border border-[#22d3ee] text-[#22d3ee] text-sm font-semibold hover:bg-[#22d3ee]/10 transition-colors"
        >
          Copy Share Link
        </button>
      </div>

      {/* Flash message */}
      {flash && (
        <div className="rounded border border-green-700 bg-green-900/20 px-3 py-2 text-sm text-green-400">
          {flash}
        </div>
      )}
    </div>
  );
}
