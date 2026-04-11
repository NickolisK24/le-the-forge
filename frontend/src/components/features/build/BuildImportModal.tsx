/**
 * BuildImportModal
 *
 * Three-tab import UI:
 *   - "URL Import" — paste a LE Tools or Maxroll planner URL, creates build directly
 *   - "Quick Fetch" — legacy: fetch and preview before applying to form
 *   - "JSON" — paste raw Forge export JSON directly
 *
 * Detects source from URL as the user types and shows a badge.
 * On success, navigates to the new build or applies to form.
 */

import { useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { importApi, type ImportedBuild } from "@/lib/api";
import type { ImportBuildResponse } from "@/types";
import { Button, Spinner } from "@/components/ui";

type Tab = "import" | "fetch" | "json";

interface Props {
  onImport: (build: ImportedBuild) => void;
  onClose: () => void;
}

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60 disabled:opacity-50";
const labelCls = "font-mono text-[11px] uppercase tracking-widest text-forge-dim";

function detectSource(url: string): "lastepochtools" | "maxroll" | null {
  if (/lastepochtools\.com\/planner\//i.test(url)) return "lastepochtools";
  if (/maxroll\.gg\/last-epoch\/planner\//i.test(url)) return "maxroll";
  return null;
}

const SOURCE_LABELS: Record<string, string> = {
  lastepochtools: "Last Epoch Tools",
  maxroll: "Maxroll",
};

export default function BuildImportModal({ onImport, onClose }: Props) {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>("import");

  // Import tab state (new full import)
  const [importUrl, setImportUrl] = useState("");
  const [importLoading, setImportLoading] = useState(false);
  const [importError, setImportError] = useState("");
  const [importResult, setImportResult] = useState<ImportBuildResponse | null>(null);

  // Fetch tab state (legacy preview)
  const [fetchUrl, setFetchUrl] = useState("");
  const [fetchLoading, setFetchLoading] = useState(false);
  const [fetchError, setFetchError] = useState("");
  const [preview, setPreview] = useState<ImportedBuild | null>(null);

  // JSON tab state
  const [jsonText, setJsonText] = useState("");
  const [jsonError, setJsonError] = useState("");

  const importSource = detectSource(importUrl);
  const fetchSource = detectSource(fetchUrl);

  // ---- Full import (URL → save build) ------------------------------------

  async function handleFullImport() {
    setImportError("");
    if (!importUrl.trim()) {
      setImportError("Paste a build URL first.");
      return;
    }
    if (!importSource) {
      setImportError("Unsupported URL. Supported: lastepochtools.com/planner/... or maxroll.gg/last-epoch/planner/...");
      return;
    }

    setImportLoading(true);
    try {
      const res = await importApi.importBuild(importUrl.trim());
      const errMsg = res.errors?.[0]?.message;
      if (errMsg || !res.data) {
        setImportError(errMsg ?? "Import failed — check the URL and try again.");
      } else {
        setImportResult(res.data);
      }
    } catch {
      setImportError("Request failed — backend may be unavailable.");
    } finally {
      setImportLoading(false);
    }
  }

  // ---- Legacy fetch (URL → preview → apply to form) ----------------------

  async function handleUrlFetch() {
    setFetchError("");
    if (!fetchUrl.trim()) {
      setFetchError("Paste a Last Epoch Tools URL first.");
      return;
    }
    if (!fetchUrl.includes("lastepochtools.com/planner/")) {
      setFetchError("URL must be from lastepochtools.com/planner/…");
      return;
    }

    setFetchLoading(true);
    try {
      const res = await importApi.fromUrl(fetchUrl.trim());
      const errMsg = res.errors?.[0]?.message;
      const build = (res.data as Record<string, unknown>)?.build as ImportedBuild | undefined;
      if (errMsg || !build) {
        setFetchError(errMsg ?? "No build data returned — check the URL and try again.");
      } else {
        setPreview(build);
      }
    } catch {
      setFetchError("Request failed — backend may be unavailable.");
    } finally {
      setFetchLoading(false);
    }
  }

  function handleConfirmPreview() {
    if (!preview) return;
    onImport(preview);
    toast.success("Build imported — review and save when ready.");
    onClose();
  }

  // ---- JSON import --------------------------------------------------------

  function handleJsonImport() {
    setJsonError("");
    if (!jsonText.trim()) {
      setJsonError("Paste your build JSON first.");
      return;
    }
    try {
      const parsed = JSON.parse(jsonText);
      if (!parsed.character_class) {
        setJsonError("Invalid build JSON — missing character_class field.");
        return;
      }
      onImport(parsed as ImportedBuild);
      toast.success("Build imported — review and save when ready.");
      onClose();
    } catch {
      setJsonError("Invalid JSON — check your paste for syntax errors.");
    }
  }

  // ---- Source badge -------------------------------------------------------

  function SourceBadge({ source }: { source: string | null }) {
    if (!source) return null;
    return (
      <span className="inline-flex items-center rounded-sm border border-forge-amber/40 bg-forge-amber/10 px-2 py-0.5 font-mono text-[10px] text-forge-amber">
        {SOURCE_LABELS[source] ?? source}
      </span>
    );
  }

  // ---- Render -------------------------------------------------------------

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-lg rounded border border-forge-border bg-forge-bg shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-forge-border px-4 py-3">
          <span className="font-display text-lg text-forge-amber">Import Build</span>
          <button
            onClick={onClose}
            className="font-mono text-sm text-forge-dim transition-colors hover:text-forge-text"
          >
            ✕ Close
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-forge-border">
          {([
            { key: "import" as Tab, label: "Import URL" },
            { key: "fetch" as Tab, label: "Quick Fetch" },
            { key: "json" as Tab, label: "{ } JSON" },
          ]).map((t) => (
            <button
              key={t.key}
              onClick={() => {
                setTab(t.key);
                setImportResult(null);
                setPreview(null);
                setImportError("");
                setFetchError("");
                setJsonError("");
              }}
              className={`px-4 py-2.5 font-mono text-[10px] uppercase tracking-widest border-r border-forge-border transition-colors ${
                tab === t.key
                  ? "bg-forge-surface text-forge-amber"
                  : "text-forge-dim hover:text-forge-text"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="p-5">

          {/* ---- Import tab (new full flow) ---- */}
          {tab === "import" && !importResult && (
            <div className="flex flex-col gap-4">
              <div>
                <p className="font-body text-sm text-forge-text/80 leading-relaxed">
                  Import a build from{" "}
                  <span className="text-forge-amber font-mono text-xs">Maxroll</span>
                  . Paste a planner URL and we'll map everything we can.
                </p>
                <div className="mt-2 rounded border border-yellow-500/20 bg-yellow-500/5 px-3 py-2">
                  <p className="font-mono text-[10px] text-yellow-400/80 leading-relaxed">
                    Last Epoch Tools import is temporarily unavailable — LET moved to
                    client-side rendering which prevents server-side fetching. Use Maxroll
                    planner URLs instead.
                  </p>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <label className={labelCls}>Maxroll Planner URL</label>
                  <SourceBadge source={importSource} />
                  {importSource === "lastepochtools" && (
                    <span className="font-mono text-[10px] text-yellow-400/70">
                      LET import unavailable
                    </span>
                  )}
                </div>
                <input
                  className={inputCls}
                  type="url"
                  placeholder="https://maxroll.gg/last-epoch/planner/zge0t60e"
                  value={importUrl}
                  onChange={(e) => { setImportUrl(e.target.value); setImportError(""); }}
                  onKeyDown={(e) => e.key === "Enter" && handleFullImport()}
                  autoFocus
                />
                {importError && (
                  <p className="mt-1.5 font-mono text-[11px] text-red-400">{importError}</p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleFullImport}
                  disabled={importLoading || !importUrl.trim()}
                >
                  {importLoading ? (
                    <span className="flex items-center gap-2">
                      <Spinner size={14} /> Fetching and parsing build...
                    </span>
                  ) : "Import Build"}
                </Button>
              </div>
            </div>
          )}

          {/* ---- Import success ---- */}
          {tab === "import" && importResult && (
            <div className="flex flex-col gap-4">
              {/* Success with no warnings */}
              {importResult.warnings.length === 0 && (
                <div className="rounded border border-green-500/30 bg-green-500/8 px-4 py-3">
                  <div className="font-display text-sm text-green-400">Build imported successfully</div>
                  <div className="mt-1 font-mono text-[11px] text-forge-dim">
                    {importResult.build_name} — from {SOURCE_LABELS[importResult.source] ?? importResult.source}
                  </div>
                </div>
              )}

              {/* Success with warnings (partial import) */}
              {importResult.warnings.length > 0 && (
                <div className="rounded border border-yellow-500/30 bg-yellow-500/8 px-4 py-3">
                  <div className="font-display text-sm text-yellow-400">Partial import</div>
                  <div className="mt-1 font-mono text-[11px] text-forge-dim">
                    {importResult.build_name} — some fields could not be mapped:
                  </div>
                  <ul className="mt-2 space-y-0.5">
                    {importResult.warnings.map((w, i) => (
                      <li key={i} className="font-mono text-[10px] text-yellow-400/80">• {w}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Imported fields summary */}
              <div className="rounded border border-forge-border bg-forge-surface2 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-2">
                  Imported Fields
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {importResult.imported_fields.map((f) => (
                    <span key={f} className="rounded-sm border border-forge-border bg-forge-bg px-2 py-0.5 font-mono text-[10px] text-forge-text">
                      {f}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex justify-between gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => { setImportResult(null); setImportUrl(""); }}
                >
                  Import Another
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    onClose();
                    navigate(`/build/${importResult.slug}`);
                  }}
                >
                  Open Build
                </Button>
              </div>
            </div>
          )}

          {/* ---- Quick Fetch tab (legacy) ---- */}
          {tab === "fetch" && !preview && (
            <div className="flex flex-col gap-4">
              <div className="rounded border border-yellow-500/20 bg-yellow-500/5 px-4 py-3">
                <div className="font-display text-sm text-yellow-400">Temporarily Unavailable</div>
                <p className="mt-1 font-body text-sm text-forge-text/70 leading-relaxed">
                  Last Epoch Tools moved to client-side rendering, which prevents
                  server-side fetching. This method is temporarily unavailable.
                </p>
                <p className="mt-2 font-mono text-[10px] text-forge-dim">
                  Use the <strong>Import URL</strong> tab with a Maxroll planner URL instead.
                </p>
              </div>

              <div className="opacity-50">
                <div className="flex items-center gap-2 mb-1.5">
                  <label className={labelCls}>Last Epoch Tools URL</label>
                  <SourceBadge source={fetchSource} />
                </div>
                <input
                  className={inputCls}
                  type="url"
                  placeholder="https://www.lastepochtools.com/planner/kB5dyWvQ"
                  value={fetchUrl}
                  onChange={(e) => { setFetchUrl(e.target.value); setFetchError(""); }}
                  onKeyDown={(e) => e.key === "Enter" && handleUrlFetch()}
                  disabled
                />
                {fetchError && (
                  <p className="mt-1.5 font-mono text-[11px] text-red-400">{fetchError}</p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleUrlFetch}
                  disabled
                >
                  Fetch Build →
                </Button>
              </div>
            </div>
          )}

          {/* ---- Quick Fetch preview ---- */}
          {tab === "fetch" && preview && (
            <div className="flex flex-col gap-4">
              <div className="rounded border border-forge-border bg-forge-surface2 p-3 flex flex-col gap-2">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
                  Import Preview
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[11px]">
                  <span className="text-forge-dim">Class</span>
                  <span className="text-forge-text">{preview.character_class}</span>
                  <span className="text-forge-dim">Mastery</span>
                  <span className="text-forge-amber">{preview.mastery || "—"}</span>
                  <span className="text-forge-dim">Level</span>
                  <span className="text-forge-text">{preview.level}</span>
                  <span className="text-forge-dim">Passive nodes</span>
                  <span className="text-forge-text">
                    {preview._import_meta?.passive_nodes ?? preview.passive_tree.length}
                  </span>
                  <span className="text-forge-dim">Skills</span>
                  <span className="text-forge-text">
                    {preview.skills.map((s) => s.skill_name).join(", ") || "—"}
                  </span>
                  <span className="text-forge-dim">Gear</span>
                  <span className="text-forge-dim italic">Not imported</span>
                </div>
              </div>

              {preview._import_meta?.gear_note && (
                <p className="font-mono text-[10px] text-yellow-400/70">
                  {preview._import_meta.gear_note}
                </p>
              )}

              <div className="flex justify-between gap-2">
                <Button variant="outline" size="sm" onClick={() => setPreview(null)}>
                  ← Back
                </Button>
                <Button variant="primary" size="sm" onClick={handleConfirmPreview}>
                  Apply to Form →
                </Button>
              </div>
            </div>
          )}

          {/* ---- JSON tab ---- */}
          {tab === "json" && (
            <div className="flex flex-col gap-4">
              <p className="font-body text-sm text-forge-text/80 leading-relaxed">
                Paste a build JSON exported from The Forge (use the Export button on any build).
              </p>

              <div>
                <label className={labelCls}>Build JSON</label>
                <textarea
                  className={inputCls + " mt-1.5 h-36 resize-none font-mono text-xs"}
                  placeholder='{ "character_class": "Acolyte", "mastery": "Lich", ... }'
                  value={jsonText}
                  onChange={(e) => { setJsonText(e.target.value); setJsonError(""); }}
                />
                {jsonError && (
                  <p className="mt-1.5 font-mono text-[11px] text-red-400">{jsonError}</p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleJsonImport}
                  disabled={!jsonText.trim()}
                >
                  Import →
                </Button>
              </div>
            </div>
          )}

        </div>

        {/* Hard failure note */}
        {importError && importError.includes("422") && (
          <div className="border-t border-forge-border px-4 py-2">
            <p className="font-mono text-[10px] text-forge-dim">
              This issue has been reported and will be reviewed.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
