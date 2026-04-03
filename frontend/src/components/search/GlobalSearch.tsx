import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { createPortal } from "react-dom";

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

const MOCK_DATA: SearchSection[] = [
  {
    title: "Items",
    type: "item",
    results: [
      { id: "i1", name: "Ravenous Void", type: "item", path: "/bis-search", subtitle: "Body Armour" },
      { id: "i2", name: "Bleeding Heart", type: "item", path: "/bis-search", subtitle: "Amulet" },
      { id: "i3", name: "Invoker's Static Touch", type: "item", path: "/bis-search", subtitle: "Gloves" },
    ],
  },
  {
    title: "Skills",
    type: "skill",
    results: [
      { id: "s1", name: "Rive", type: "skill", path: "/build", subtitle: "Sentinel" },
      { id: "s2", name: "Warpath", type: "skill", path: "/build", subtitle: "Sentinel" },
      { id: "s3", name: "Shatter Strike", type: "skill", path: "/build", subtitle: "Sentinel" },
    ],
  },
  {
    title: "Affixes",
    type: "affix",
    results: [
      { id: "a1", name: "Increased Attack Speed", type: "affix", path: "/affixes", subtitle: "Prefix" },
      { id: "a2", name: "Critical Strike Chance", type: "affix", path: "/affixes", subtitle: "Prefix" },
      { id: "a3", name: "Adaptive Spell Damage", type: "affix", path: "/affixes", subtitle: "Suffix" },
    ],
  },
  {
    title: "Builds",
    type: "build",
    results: [
      { id: "b1", name: "Bleed Rive Sentinel", type: "build", path: "/builds", subtitle: "Tier S · SSF" },
      { id: "b2", name: "Void Knight Echoes", type: "build", path: "/builds", subtitle: "Tier A" },
      { id: "b3", name: "Warpath Tank", type: "build", path: "/builds", subtitle: "Tier B · HC" },
    ],
  },
];

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

function flatResults(sections: SearchSection[]): SearchResult[] {
  return sections.flatMap((s) => s.results);
}

function filterSections(sections: SearchSection[], query: string): SearchSection[] {
  if (!query.trim()) return sections;
  const q = query.toLowerCase();
  return sections
    .map((section) => ({
      ...section,
      results: section.results.filter(
        (r) =>
          r.name.toLowerCase().includes(q) ||
          r.subtitle?.toLowerCase().includes(q) ||
          r.type.toLowerCase().includes(q)
      ),
    }))
    .filter((s) => s.results.length > 0);
}

export default function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredSections = filterSections(MOCK_DATA, query);
  const allResults = flatResults(filteredSections);

  // Register global Cmd/Ctrl+K
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (!isOpen) {
          // parent controls open state; this fires onClose as a toggle signal if needed
          // The parent registers its own listener to open — this just prevents default
        }
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

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
            placeholder="Search items, skills, affixes, builds…"
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
          {filteredSections.length === 0 ? (
            <div className="py-12 text-center">
              <p className="font-body text-sm text-forge-dim">No results found.</p>
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
