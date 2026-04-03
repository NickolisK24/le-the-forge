/**
 * O11 — ImportPanel
 *
 * Supports three import modes: Paste JSON, Build String (base64), Upload File.
 */

import { useState, useRef } from "react";

export type ParsedBuild = {
  build_name: string;
  character_class: string;
  version: string;
  skills: any[];
  gear: any[];
  passives: any[];
};

interface ImportPanelProps {
  onImport?: (buildData: ParsedBuild) => void;
}

type TabId = "json" | "string" | "file";

const TABS: { id: TabId; label: string }[] = [
  { id: "json", label: "Paste JSON" },
  { id: "string", label: "Build String" },
  { id: "file", label: "Upload File" },
];

function extractBuild(raw: any): ParsedBuild {
  return {
    build_name: raw.build_name ?? "Unnamed Build",
    character_class: raw.character_class ?? "Unknown",
    version: raw.version ?? "1.0",
    skills: Array.isArray(raw.skills) ? raw.skills : [],
    gear: Array.isArray(raw.gear) ? raw.gear : [],
    passives: Array.isArray(raw.passives) ? raw.passives : [],
  };
}

export default function ImportPanel({ onImport }: ImportPanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>("json");
  const [jsonText, setJsonText] = useState("");
  const [buildString, setBuildString] = useState("");
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function showSuccess(name: string) {
    setErrorMsg(null);
    setSuccessMsg(`Build imported: ${name}`);
    setTimeout(() => setSuccessMsg(null), 3000);
  }

  function showError(msg: string) {
    setSuccessMsg(null);
    setErrorMsg(msg);
  }

  function importFromJson(text: string) {
    try {
      const raw = JSON.parse(text);
      const build = extractBuild(raw);
      onImport?.(build);
      showSuccess(build.build_name);
    } catch {
      showError("Invalid JSON — could not parse build data.");
    }
  }

  function handleJsonImport() {
    importFromJson(jsonText);
  }

  function handleStringImport() {
    try {
      const decoded = atob(buildString.trim());
      importFromJson(decoded);
    } catch {
      showError("Invalid build string — could not decode base64.");
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      importFromJson(text);
    };
    reader.readAsText(file);
    // Reset so the same file can be re-selected
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-4">
      <h2 className="font-display text-lg text-[#f5a623]">Import Build</h2>

      {/* Tab bar */}
      <div className="flex gap-1 border-b border-[#2a3050]">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id); setErrorMsg(null); setSuccessMsg(null); }}
            className={[
              "px-4 py-2 text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "text-[#f5a623] border-b-2 border-[#f5a623] -mb-px"
                : "text-gray-400 hover:text-gray-200",
            ].join(" ")}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="space-y-3">
        {activeTab === "json" && (
          <>
            <textarea
              rows={8}
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              placeholder='{"build_name": "My Build", ...}'
              className="w-full rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#f5a623] resize-none font-mono"
            />
            <button
              onClick={handleJsonImport}
              className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
            >
              Import
            </button>
          </>
        )}

        {activeTab === "string" && (
          <>
            <input
              type="text"
              value={buildString}
              onChange={(e) => setBuildString(e.target.value)}
              placeholder="Paste base64 build string here..."
              className="w-full rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#f5a623] font-mono"
            />
            <button
              onClick={handleStringImport}
              className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
            >
              Import
            </button>
          </>
        )}

        {activeTab === "file" && (
          <div className="space-y-2">
            <p className="text-sm text-gray-400">Select a <code className="text-[#22d3ee]">.json</code> build file to import.</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileChange}
              className="block text-sm text-gray-400 file:mr-3 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-[#f5a623] file:text-[#10152a] hover:file:bg-[#e0952a] cursor-pointer"
            />
          </div>
        )}
      </div>

      {/* Feedback banners */}
      {successMsg && (
        <div className="rounded border border-green-700 bg-green-900/20 px-3 py-2 text-sm text-green-400">
          {successMsg}
        </div>
      )}
      {errorMsg && (
        <div className="rounded border border-red-700 bg-red-900/20 px-3 py-2 text-sm text-red-400">
          {errorMsg}
        </div>
      )}
    </div>
  );
}
