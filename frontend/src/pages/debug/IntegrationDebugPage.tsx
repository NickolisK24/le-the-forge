/**
 * O16 — IntegrationDebugPage
 *
 * Route: /integration-debug
 *
 * Developer debug page for testing all Phase O integration features.
 */

import { useState } from "react";

function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash += str.charCodeAt(i);
  }
  return hash % 999999;
}

function isCompatible(from: string, to: string): boolean {
  // Simple rule: major versions must match
  const fromParts = from.split(".");
  const toParts = to.split(".");
  return fromParts[0] === toParts[0];
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-base font-semibold text-[#f5a623]">{title}</h2>
      {children}
    </div>
  );
}

export default function IntegrationDebugPage() {
  // Section 1: Import Test
  const [importJson, setImportJson] = useState("");
  const [importResult, setImportResult] = useState<string | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  // Section 2: Export Test
  const [exportBuild, setExportBuild] = useState<object | null>(null);
  const [exportBuildString, setExportBuildString] = useState<string | null>(null);

  // Section 3: Share Link Test
  const [shareLink, setShareLink] = useState<string | null>(null);

  // Section 4: Version Test
  const [versionFrom, setVersionFrom] = useState("1.0");
  const [versionTo, setVersionTo] = useState("1.2");
  const [versionResult, setVersionResult] = useState<string | null>(null);

  // Section 5: Auth Test
  const [apiKey, setApiKey] = useState("");
  const [authResult, setAuthResult] = useState<string | null>(null);

  // --- Handlers ---

  function handleParse() {
    try {
      const parsed = JSON.parse(importJson);
      setImportError(null);
      setImportResult(JSON.stringify(parsed, null, 2));
    } catch (e: any) {
      setImportResult(null);
      setImportError(`Parse error: ${e.message}`);
    }
  }

  function handleGenerateTestBuild() {
    const build = {
      build_name: "Test Build",
      character_class: "Sorcerer",
      version: "1.0",
      skills: [{ skill_id: "fireball", level: 10 }, { skill_id: "frost_nova", level: 5 }],
      gear: [{ slot: "helm", item_id: "iron_helm" }],
      passives: [{ node_id: "elemental_mastery", rank: 3 }],
    };
    setExportBuild(build);
    setExportBuildString(btoa(JSON.stringify(build)));
  }

  function handleGenerateLink() {
    const sampleStr = JSON.stringify({ build_name: "Debug Build", ts: Date.now() });
    const hash = simpleHash(sampleStr);
    setShareLink(`https://le-the-forge.app/share/${hash}`);
  }

  function handleCheckCompatibility() {
    const result = isCompatible(versionFrom, versionTo);
    setVersionResult(result ? "Compatible" : "Not Compatible");
  }

  function handleAuthenticate() {
    if (apiKey.trim().length === 0) {
      setAuthResult("Error: API key cannot be empty");
      return;
    }
    if (apiKey.startsWith("forge_")) {
      setAuthResult(`Authenticated as mock_user (key: ${apiKey.slice(0, 12)}...)`);
    } else {
      setAuthResult("Authentication failed: invalid key format (expected forge_...)");
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div>
        <h1 className="font-display text-2xl text-[#f5a623]">Integration Debug</h1>
        <p className="text-sm text-gray-400 mt-1">Developer tools for testing Phase O external integration features.</p>
      </div>

      {/* Section 1: Import Test */}
      <Card title="1. Import Test">
        <textarea
          rows={5}
          value={importJson}
          onChange={(e) => setImportJson(e.target.value)}
          placeholder='Paste JSON here and click Parse...'
          className="w-full rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#f5a623] resize-none font-mono"
        />
        <button
          onClick={handleParse}
          className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
        >
          Parse
        </button>
        {importResult && (
          <pre className="rounded border border-[#2a3050] bg-[#0d1120] p-3 text-xs text-green-400 overflow-auto max-h-48 font-mono">
            {importResult}
          </pre>
        )}
        {importError && (
          <div className="rounded border border-red-700 bg-red-900/20 px-3 py-2 text-sm text-red-400">
            {importError}
          </div>
        )}
      </Card>

      {/* Section 2: Export Test */}
      <Card title="2. Export Test">
        <button
          onClick={handleGenerateTestBuild}
          className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
        >
          Generate Test Build
        </button>
        {exportBuild && (
          <div className="space-y-2">
            <p className="text-xs text-gray-400 font-medium">JSON:</p>
            <pre className="rounded border border-[#2a3050] bg-[#0d1120] p-3 text-xs text-gray-300 overflow-auto max-h-48 font-mono">
              {JSON.stringify(exportBuild, null, 2)}
            </pre>
            <p className="text-xs text-gray-400 font-medium">Build String (base64):</p>
            <p className="rounded border border-[#2a3050] bg-[#0d1120] p-3 text-xs text-[#22d3ee] break-all font-mono">
              {exportBuildString}
            </p>
          </div>
        )}
      </Card>

      {/* Section 3: Share Link Test */}
      <Card title="3. Share Link Test">
        <button
          onClick={handleGenerateLink}
          className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
        >
          Generate Link
        </button>
        {shareLink && (
          <div className="rounded border border-[#2a3050] bg-[#0d1120] p-3">
            <p className="text-xs text-gray-400 mb-1">Share URL:</p>
            <p className="text-sm text-[#22d3ee] break-all font-mono">{shareLink}</p>
          </div>
        )}
      </Card>

      {/* Section 4: Version Test */}
      <Card title="4. Version Compatibility Test">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs text-gray-400">From version</label>
            <input
              type="text"
              value={versionFrom}
              onChange={(e) => setVersionFrom(e.target.value)}
              className="rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-[#f5a623] w-28"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-gray-400">To version</label>
            <input
              type="text"
              value={versionTo}
              onChange={(e) => setVersionTo(e.target.value)}
              className="rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-[#f5a623] w-28"
            />
          </div>
          <button
            onClick={handleCheckCompatibility}
            className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
          >
            Check Compatibility
          </button>
        </div>
        {versionResult && (
          <div
            className={[
              "rounded border px-3 py-2 text-sm font-medium",
              versionResult === "Compatible"
                ? "border-green-700 bg-green-900/20 text-green-400"
                : "border-red-700 bg-red-900/20 text-red-400",
            ].join(" ")}
          >
            {versionResult}
          </div>
        )}
      </Card>

      {/* Section 5: Auth Test */}
      <Card title="5. Auth Test">
        <div className="flex gap-3">
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="forge_your_api_key_here"
            className="flex-1 rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#f5a623] font-mono"
          />
          <button
            onClick={handleAuthenticate}
            className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors whitespace-nowrap"
          >
            Authenticate
          </button>
        </div>
        {authResult && (
          <div
            className={[
              "rounded border px-3 py-2 text-sm",
              authResult.startsWith("Authenticated")
                ? "border-green-700 bg-green-900/20 text-green-400"
                : "border-red-700 bg-red-900/20 text-red-400",
            ].join(" ")}
          >
            {authResult}
          </div>
        )}
      </Card>
    </div>
  );
}
