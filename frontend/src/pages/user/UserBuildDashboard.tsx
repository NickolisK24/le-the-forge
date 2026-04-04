/**
 * O15 — UserBuildDashboard
 *
 * Route: /my-builds
 *
 * Personal build management dashboard with CRUD-like operations.
 */

import { useState } from "react";

type UserBuild = {
  id: string;
  build_name: string;
  character_class: string;
  version: string;
  created_date: string;
};

const INITIAL_BUILDS: UserBuild[] = [
  { id: "u1", build_name: "My Fireball Build", character_class: "Sorcerer", version: "1.0", created_date: "2026-03-15" },
  { id: "u2", build_name: "Tank Warrior", character_class: "Warrior", version: "1.1", created_date: "2026-03-22" },
  { id: "u3", build_name: "Glass Cannon Ranger", character_class: "Ranger", version: "1.0", created_date: "2026-04-01" },
];

let nextId = 100;

function generateId() {
  return `u${nextId++}`;
}

function downloadBuildJson(build: UserBuild) {
  const blob = new Blob([JSON.stringify(build, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${build.build_name}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function UserBuildDashboard() {
  const [builds, setBuilds] = useState<UserBuild[]>(INITIAL_BUILDS);

  function handleDuplicate(build: UserBuild) {
    const copy: UserBuild = {
      ...build,
      id: generateId(),
      build_name: `${build.build_name} (copy)`,
      created_date: new Date().toISOString().slice(0, 10),
    };
    setBuilds((prev) => [...prev, copy]);
  }

  function handleDelete(id: string) {
    const confirmed = window.confirm("Are you sure you want to delete this build?");
    if (confirmed) {
      setBuilds((prev) => prev.filter((b) => b.id !== id));
    }
  }

  function handleNewBuild() {
    const placeholder: UserBuild = {
      id: generateId(),
      build_name: "New Build",
      character_class: "Sorcerer",
      version: "1.0",
      created_date: new Date().toISOString().slice(0, 10),
    };
    setBuilds((prev) => [...prev, placeholder]);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl text-[#f5a623]">My Builds</h1>
          <p className="text-sm text-gray-400 mt-1">Manage your personal build collection.</p>
        </div>
        <button
          onClick={handleNewBuild}
          className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
        >
          + New Build
        </button>
      </div>

      {builds.length === 0 ? (
        <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-8 text-center">
          <p className="text-gray-400 text-sm">No builds yet. Create your first build!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {builds.map((build) => (
            <div
              key={build.id}
              className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
            >
              <div className="space-y-1">
                <h3 className="text-gray-100 font-medium">{build.build_name}</h3>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-[#22d3ee]">{build.character_class}</span>
                  <span className="text-gray-500">v{build.version}</span>
                  <span className="text-gray-600">Created {build.created_date}</span>
                </div>
              </div>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => handleDuplicate(build)}
                  className="px-3 py-1 rounded border border-[#f5a623] text-[#f5a623] text-xs font-semibold hover:bg-[#f5a623]/10 transition-colors"
                >
                  Duplicate
                </button>
                <button
                  onClick={() => downloadBuildJson(build)}
                  className="px-3 py-1 rounded border border-[#22d3ee] text-[#22d3ee] text-xs font-semibold hover:bg-[#22d3ee]/10 transition-colors"
                >
                  Export
                </button>
                <button
                  onClick={() => handleDelete(build.id)}
                  className="px-3 py-1 rounded border border-red-600 text-red-500 text-xs font-semibold hover:bg-red-600/10 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
