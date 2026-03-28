/**
 * BuildImportModal
 *
 * Two-tab import UI:
 *   • "Last Epoch Tools URL" — paste a LE Tools planner URL, backend proxies it
 *   • "JSON" — paste raw Forge export JSON directly
 *
 * On success calls onImport(payload) with a BuildCreatePayload-compatible object.
 * The caller is responsible for applying the payload to their form state.
 */

import { useState } from "react";
import toast from "react-hot-toast";
import { importApi, type ImportedBuild } from "@/lib/api";
import { Button } from "@/components/ui";

type Tab = "url" | "json";

interface Props {
  onImport: (build: ImportedBuild) => void;
  onClose: () => void;
}

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60 disabled:opacity-50";
const labelCls = "font-mono text-[11px] uppercase tracking-widest text-forge-dim";

export default function BuildImportModal({ onImport, onClose }: Props) {
  const [tab, setTab] = useState<Tab>("url");

  // URL tab state
  const [url, setUrl] = useState("");
  const [urlLoading, setUrlLoading] = useState(false);
  const [urlError, setUrlError] = useState("");

  // JSON tab state
  const [jsonText, setJsonText] = useState("");
  const [jsonError, setJsonError] = useState("");

  // Preview — shown after a successful URL fetch before the user confirms
  const [preview, setPreview] = useState<ImportedBuild | null>(null);

  // ---- URL import ---------------------------------------------------------

  async function handleUrlFetch() {
    setUrlError("");
    if (!url.trim()) {
      setUrlError("Paste a Last Epoch Tools URL first.");
      return;
    }
    if (!url.includes("lastepochtools.com/planner/")) {
      setUrlError("URL must be from lastepochtools.com/planner/…");
      return;
    }

    setUrlLoading(true);
    try {
      const res = await importApi.fromUrl(url.trim());
      if (res.error || !res.data?.build) {
        setUrlError(res.error ?? "Unknown error from server.");
      } else {
        setPreview(res.data.build);
      }
    } catch {
      setUrlError("Request failed — backend may be unavailable.");
    } finally {
      setUrlLoading(false);
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
          {(["url", "json"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setPreview(null); setUrlError(""); setJsonError(""); }}
              className={`px-5 py-2.5 font-mono text-[11px] uppercase tracking-widest border-r border-forge-border transition-colors ${
                tab === t
                  ? "bg-forge-surface text-forge-amber"
                  : "text-forge-dim hover:text-forge-text"
              }`}
            >
              {t === "url" ? "🔗 Last Epoch Tools URL" : "{ } JSON Paste"}
            </button>
          ))}
        </div>

        <div className="p-5">

          {/* ---- URL tab ---- */}
          {tab === "url" && !preview && (
            <div className="flex flex-col gap-4">
              <div>
                <p className="font-body text-sm text-forge-text/80 leading-relaxed">
                  Paste a build link from{" "}
                  <span className="text-forge-amber font-mono text-xs">lastepochtools.com/planner/…</span>
                  {" "}and The Forge will import the class, passives, and skills automatically.
                </p>
                <p className="mt-1 font-mono text-[10px] text-forge-dim">
                  ⚠ Gear is not yet imported — fill it in manually after importing.
                </p>
              </div>

              <div>
                <label className={labelCls}>Last Epoch Tools URL</label>
                <input
                  className={inputCls + " mt-1.5"}
                  type="url"
                  placeholder="https://www.lastepochtools.com/planner/kB5dyWvQ"
                  value={url}
                  onChange={(e) => { setUrl(e.target.value); setUrlError(""); }}
                  onKeyDown={(e) => e.key === "Enter" && handleUrlFetch()}
                  autoFocus
                />
                {urlError && (
                  <p className="mt-1.5 font-mono text-[11px] text-red-400">{urlError}</p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleUrlFetch}
                  disabled={urlLoading || !url.trim()}
                >
                  {urlLoading ? "Fetching…" : "Fetch Build →"}
                </Button>
              </div>
            </div>
          )}

          {/* ---- URL preview ---- */}
          {tab === "url" && preview && (
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
                  ⚠ {preview._import_meta.gear_note}
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
      </div>
    </div>
  );
}
