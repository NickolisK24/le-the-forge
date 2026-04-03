/**
 * O14 — BuildLibraryPage
 *
 * Route: /build-library
 *
 * Searchable, filterable, paginated build library using mock data.
 */

import { useState } from "react";
import { Link } from "react-router-dom";

type LibraryBuild = {
  id: string;
  build_name: string;
  character_class: string;
  version: string;
  views: number;
};

const CLASSES = ["All", "Sorcerer", "Warrior", "Ranger", "Rogue"] as const;
type ClassFilter = (typeof CLASSES)[number];

const MOCK_BUILDS: LibraryBuild[] = [
  { id: "1", build_name: "Glacial Storm Sorcerer", character_class: "Sorcerer", version: "1.0", views: 4821 },
  { id: "2", build_name: "Berserker Warrior", character_class: "Warrior", version: "1.1", views: 3204 },
  { id: "3", build_name: "Lightning Arrow Ranger", character_class: "Ranger", version: "1.0", views: 2975 },
  { id: "4", build_name: "Shadow Rogue", character_class: "Rogue", version: "1.2", views: 2561 },
  { id: "5", build_name: "Fireball Mage", character_class: "Sorcerer", version: "1.0", views: 2104 },
  { id: "6", build_name: "Shield Warrior", character_class: "Warrior", version: "1.1", views: 1890 },
  { id: "7", build_name: "Poison Ranger", character_class: "Ranger", version: "1.2", views: 1432 },
  { id: "8", build_name: "Blade Dancer Rogue", character_class: "Rogue", version: "1.0", views: 1105 },
];

const PAGE_SIZE = 4;

export default function BuildLibraryPage() {
  const [search, setSearch] = useState("");
  const [classFilter, setClassFilter] = useState<ClassFilter>("All");
  const [page, setPage] = useState(0);

  const filtered = MOCK_BUILDS.filter((b) => {
    const matchSearch = b.build_name.toLowerCase().includes(search.toLowerCase());
    const matchClass = classFilter === "All" || b.character_class === classFilter;
    return matchSearch && matchClass;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages - 1);
  const pageBuilds = filtered.slice(safePage * PAGE_SIZE, safePage * PAGE_SIZE + PAGE_SIZE);

  function handleSearchChange(val: string) {
    setSearch(val);
    setPage(0);
  }

  function handleClassChange(val: ClassFilter) {
    setClassFilter(val);
    setPage(0);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div>
        <h1 className="font-display text-2xl text-[#f5a623]">Build Library</h1>
        <p className="text-sm text-gray-400 mt-1">Browse and discover community builds.</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search builds..."
          className="flex-1 min-w-[180px] rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#f5a623]"
        />
        <select
          value={classFilter}
          onChange={(e) => handleClassChange(e.target.value as ClassFilter)}
          className="rounded border border-[#2a3050] bg-[#0d1120] px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-[#f5a623]"
        >
          {CLASSES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Build cards */}
      {pageBuilds.length === 0 ? (
        <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-8 text-center">
          <p className="text-gray-400 text-sm">No builds match your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {pageBuilds.map((b) => (
            <div key={b.id} className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
              <div>
                <h3 className="text-gray-100 font-medium text-sm">{b.build_name}</h3>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-[#22d3ee] text-xs">{b.character_class}</span>
                  <span className="text-gray-500 text-xs">v{b.version}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500 text-xs">{b.views.toLocaleString()} views</span>
                <Link
                  to={`/shared/${b.id}`}
                  className="px-3 py-1 rounded bg-[#f5a623] text-[#10152a] text-xs font-semibold hover:bg-[#e0952a] transition-colors"
                >
                  View Build
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-sm">
          Page {safePage + 1} of {totalPages} ({filtered.length} builds)
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={safePage === 0}
            className="px-3 py-1 rounded border border-[#2a3050] text-gray-400 text-sm disabled:opacity-40 hover:border-[#f5a623] hover:text-[#f5a623] transition-colors"
          >
            Prev
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={safePage >= totalPages - 1}
            className="px-3 py-1 rounded border border-[#2a3050] text-gray-400 text-sm disabled:opacity-40 hover:border-[#f5a623] hover:text-[#f5a623] transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
