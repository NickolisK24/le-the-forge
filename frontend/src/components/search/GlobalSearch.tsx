import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { createPortal } from "react-dom";
import { useQuery } from "@tanstack/react-query";

import { buildsApi, refApi } from "@/lib/api";
import type { BuildListItem } from "@/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

// "skill" | "affix" | "build" — live categories wired to the reference/builds
// registries. "item" is kept in the type union only because the search result
// badges already have styles for it; no items are currently sourced.
interface SearchResult {
  id: string;
  name: string;
  type: "item" | "skill" | "affix" | "build";
  path: string;
  subtitle?: string;
}

interface SearchSection {
  title: string;
  type: SearchResult["type"];
  results: SearchResult[];
}

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
}

// Cap results per section so the dropdown stays navigable; users can always
// refine the query to narrow matches.
const MAX_PER_SECTION = 12;

const TYPE_BADGE_STYLES: Record<SearchResult["type"], string> = {
  item:  "text-forge-amber  border-forge-amber/40  bg-forge-amber/8",
  skill: "text-forge-cyan   border-forge-cyan/40   bg-forge-cyan/8",
  affix: "text-forge-green  border-forge-green/40  bg-forge-green/8",
  build: "text-forge-muted  border-forge-border",
};

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6.5" cy="6.5" r="4.5" />
      <path d="M12 12 L14.5 14.5" strokeWidth="2" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <path d="M4 4 L12 12" />
      <path d="M12 4 L4 12" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Live data hooks — the search pulls from the same registries the rest of the
// app uses. Queried lazily (only when the palette is opened) and cached for
// the session.
// ---------------------------------------------------------------------------

function useSearchSkills(enabled: boolean) {
  return useQuery({
    queryKey: ["search", "skills"],
    queryFn: () => refApi.skills(),
    enabled,
    staleTime: Infinity,
  });
}

function useSearchAffixes(enabled: boolean) {
  return useQuery({
    queryKey: ["search", "affixes"],
    queryFn: () => refApi.affixes(),
    enabled,
    staleTime: Infinity,
  });
}

function useSearchBuilds(enabled: boolean) {
  return useQuery({
    queryKey: ["search", "builds"],
    queryFn: () => buildsApi.list({ per_page: 100, sort: "votes" }),
    enabled,
    staleTime: 5 * 60 * 1000,
  });
}

// ---------------------------------------------------------------------------
// Section builders — turn API payloads into SearchResult[]
// ---------------------------------------------------------------------------

function buildSkillSection(
  data: Record<string, unknown> | null | undefined,
): SearchResult[] {
  if (!data || typeof data !== "object") return [];
  const out: SearchResult[] = [];
  const seen = new Set<string>();
  for (const [cls, list] of Object.entries(data)) {
    if (!Array.isArray(list)) continue;
    for (const skill of list) {
      if (typeof skill !== "string") continue;
      // Same skill can appear under multiple class buckets (e.g. via the
      // "Other" fallback) — dedupe on skill name.
      const key = skill.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({
        id: `skill-${out.length}`,
        name: skill,
        type: "skill",
        path: `/build?skill=${encodeURIComponent(skill)}`,
        subtitle: cls === "Other" ? undefined : cls,
      });
    }
  }
  return out;
}

function buildAffixSection(
  data: Array<{ id: string; name: string; type: string }> | null | undefined,
): SearchResult[] {
  if (!Array.isArray(data)) return [];
  return data.map((a, i) => ({
    id: `affix-${a.id ?? i}`,
    name: a.name,
    type: "affix" as const,
    path: `/affixes?q=${encodeURIComponent(a.name)}`,
    subtitle: a.type === "prefix" ? "Prefix" : a.type === "suffix" ? "Suffix" : a.type,
  }));
}

function buildBuildSection(
  data: BuildListItem[] | null | undefined,
): SearchResult[] {
  if (!Array.isArray(data)) return [];
  return data.map((b) => {
    const tagBits: string[] = [];
    if (b.tier) tagBits.push(`Tier ${b.tier}`);
    if (b.character_class) tagBits.push(b.character_class);
    if (b.is_ssf) tagBits.push("SSF");
    if (b.is_hc) tagBits.push("HC");
    return {
      id: `build-${b.slug}`,
      name: b.name,
      type: "build" as const,
      path: `/builds/${b.slug}`,
      subtitle: tagBits.join(" · ") || undefined,
    };
  });
}

// ---------------------------------------------------------------------------
// Filtering — case-insensitive substring match on name + subtitle
// ---------------------------------------------------------------------------

function filterSection(results: SearchResult[], q: string): SearchResult[] {
  if (!q) return results.slice(0, MAX_PER_SECTION);
  const needle = q.toLowerCase();
  const matched: SearchResult[] = [];
  for (const r of results) {
    if (
      r.name.toLowerCase().includes(needle) ||
      r.subtitle?.toLowerCase().includes(needle)
    ) {
      matched.push(r);
      if (matched.length >= MAX_PER_SECTION) break;
    }
  }
  return matched;
}

export default function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch live data — only start fetching when the palette opens, but keep
  // the results cached afterwards so re-opening is instant.
  const { data: skillsRes, isLoading: skillsLoading } = useSearchSkills(isOpen);
  const { data: affixesRes, isLoading: affixesLoading } = useSearchAffixes(isOpen);
  const { data: buildsRes, isLoading: buildsLoading } = useSearchBuilds(isOpen);

  const allSkills = useMemo(
    () => buildSkillSection(skillsRes?.data as Record<string, unknown> | undefined),
    [skillsRes],
  );
  const allAffixes = useMemo(
    () => buildAffixSection(affixesRes?.data as any),
    [affixesRes],
  );
  const allBuilds = useMemo(
    () => buildBuildSection(buildsRes?.data as BuildListItem[] | undefined),
    [buildsRes],
  );

  const filteredSections: SearchSection[] = useMemo(() => {
    const sections: SearchSection[] = [];
    const skills = filterSection(allSkills, query);
    if (skills.length > 0) sections.push({ title: "Skills", type: "skill", results: skills });
    const affixes = filterSection(allAffixes, query);
    if (affixes.length > 0) sections.push({ title: "Affixes", type: "affix", results: affixes });
    const builds = filterSection(allBuilds, query);
    if (builds.length > 0) sections.push({ title: "Builds", type: "build", results: builds });
    return sections;
  }, [allSkills, allAffixes, allBuilds, query]);

  const allResults = useMemo(
    () => filteredSections.flatMap((s) => s.results),
    [filteredSections],
  );

  const isAnyLoading = skillsLoading || affixesLoading || buildsLoading;
  const hasAnyData = allSkills.length + allAffixes.length + allBuilds.length > 0;

  // Register global Cmd/Ctrl+K to prevent browser default. Opening/closing is
  // managed by the parent.
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setActiveIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const handleSelect = useCallback(
    (result: SearchResult) => {
      navigate(result.path);
      onClose();
    },
    [navigate, onClose]
  );

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    function handleKeyDown(e: KeyboardEvent) {
      switch (e.key) {
        case "Escape":
          onClose();
          break;
        case "ArrowDown":
          e.preventDefault();
          setActiveIndex((i) => (i + 1) % Math.max(allResults.length, 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setActiveIndex((i) =>
            i === 0 ? Math.max(allResults.length - 1, 0) : i - 1
          );
          break;
        case "Enter":
          if (allResults[activeIndex]) {
            handleSelect(allResults[activeIndex]);
          }
          break;
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, allResults, activeIndex, onClose, handleSelect]);

  // Reset active index when results change
  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  if (!isOpen) return null;

  let resultOffset = 0;

  const modal = (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      style={{ background: "rgba(0,0,0,0.75)", backdropFilter: "blur(4px)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="bg-forge-surface border border-forge-border rounded w-full mx-4 overflow-hidden shadow-2xl"
        style={{ maxWidth: 600 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-forge-border">
          <span className="text-forge-dim shrink-0">
            <SearchIcon />
          </span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search skills, affixes, builds…"
            className="flex-1 bg-transparent border-none outline-none font-body text-sm text-forge-text placeholder:text-forge-dim"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="text-forge-dim hover:text-forge-muted bg-transparent border-none cursor-pointer p-0.5"
            >
              <CloseIcon />
            </button>
          )}
          <kbd className="font-mono text-[10px] text-forge-dim border border-forge-border rounded px-1.5 py-0.5 shrink-0">
            Esc
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {isAnyLoading && !hasAnyData ? (
            <div className="py-12 text-center">
              <p className="font-body text-sm text-forge-dim">Loading…</p>
            </div>
          ) : filteredSections.length === 0 ? (
            <div className="py-12 text-center">
              <p className="font-body text-sm text-forge-dim">
                {query ? "No results found." : "Start typing to search skills, affixes, and builds."}
              </p>
            </div>
          ) : (
            filteredSections.map((section) => {
              const sectionStart = resultOffset;
              resultOffset += section.results.length;

              return (
                <div key={section.type}>
                  {/* Section header */}
                  <div className="px-4 py-2 bg-forge-surface2 border-b border-forge-border">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-forge-cyan/70">
                      {section.title}
                    </span>
                  </div>

                  {/* Section results */}
                  {section.results.map((result, idx) => {
                    const globalIdx = sectionStart + idx;
                    const isActive = globalIdx === activeIndex;

                    return (
                      <button
                        key={result.id}
                        onClick={() => handleSelect(result)}
                        onMouseEnter={() => setActiveIndex(globalIdx)}
                        className={`w-full flex items-center gap-3 px-4 py-2.5 text-left border-none cursor-pointer transition-colors duration-100 border-b border-forge-border/30 ${
                          isActive
                            ? "bg-forge-surface2"
                            : "bg-transparent hover:bg-forge-surface2/60"
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <span className={`font-body text-sm ${isActive ? "text-forge-text" : "text-forge-muted"}`}>
                            {result.name}
                          </span>
                          {result.subtitle && (
                            <span className="font-mono text-[11px] text-forge-dim ml-2">
                              {result.subtitle}
                            </span>
                          )}
                        </div>
                        <span
                          className={`inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm border shrink-0 ${TYPE_BADGE_STYLES[result.type]}`}
                        >
                          {result.type}
                        </span>
                        {isActive && (
                          <kbd className="font-mono text-[10px] text-forge-dim border border-forge-border rounded px-1 py-0.5 shrink-0">
                            ↵
                          </kbd>
                        )}
                      </button>
                    );
                  })}
                </div>
              );
            })
          )}
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-forge-border bg-forge-surface2 flex items-center gap-4">
          <span className="font-mono text-[10px] text-forge-dim flex items-center gap-1">
            <kbd className="border border-forge-border rounded px-1 py-0.5">↑↓</kbd> navigate
          </span>
          <span className="font-mono text-[10px] text-forge-dim flex items-center gap-1">
            <kbd className="border border-forge-border rounded px-1 py-0.5">↵</kbd> select
          </span>
          <span className="font-mono text-[10px] text-forge-dim flex items-center gap-1">
            <kbd className="border border-forge-border rounded px-1 py-0.5">Esc</kbd> close
          </span>
        </div>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}
