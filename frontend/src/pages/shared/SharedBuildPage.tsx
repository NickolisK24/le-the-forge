/**
 * O13 — SharedBuildPage
 *
 * Route: /shared/:buildId
 *
 * Loads a mock shared build after a 500 ms delay and displays its details.
 */

import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

type SharedBuild = {
  build_name: string;
  character_class: string;
  version: string;
  skills: { skill_id: string; level: number }[];
  gear: any[];
  passives: any[];
};

export default function SharedBuildPage() {
  const { buildId } = useParams<{ buildId: string }>();
  const [build, setBuild] = useState<SharedBuild | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [simMsg, setSimMsg] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setBuild({
        build_name: `Shared Build #${buildId}`,
        character_class: "Sorcerer",
        version: "1.0",
        skills: [{ skill_id: "fireball", level: 10 }],
        gear: [],
        passives: [],
      });
    }, 500);
    return () => clearTimeout(timer);
  }, [buildId]);

  function handleSave() {
    setToast("Saved!");
    setTimeout(() => setToast(null), 2000);
  }

  function handleSimulate() {
    setSimMsg("Simulation not available in preview");
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <h1 className="font-display text-2xl text-[#f5a623]">Shared Build</h1>
        <p className="text-sm text-gray-400 mt-1">Build ID: <span className="text-[#22d3ee]">{buildId}</span></p>
      </div>

      {!build ? (
        <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-6">
          <p className="text-gray-400 text-sm animate-pulse">Loading build {buildId}...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Build info card */}
          <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-2">
            <div className="flex items-center gap-3">
              <span className="text-gray-400 text-xs w-20">Name</span>
              <span className="text-gray-100 font-medium">{build.build_name}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-400 text-xs w-20">Class</span>
              <span className="text-[#22d3ee]">{build.character_class}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-400 text-xs w-20">Version</span>
              <span className="text-gray-300">{build.version}</span>
            </div>
          </div>

          {/* Skills */}
          <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-[#f5a623] mb-2">Skills</h2>
            {build.skills.length === 0 ? (
              <p className="text-gray-500 text-sm">No skills</p>
            ) : (
              <ul className="space-y-1">
                {build.skills.map((s, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-200">{s.skill_id}</span>
                    <span className="text-gray-500">— Level {s.level}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              className="px-4 py-2 rounded bg-[#f5a623] text-[#10152a] text-sm font-semibold hover:bg-[#e0952a] transition-colors"
            >
              Save to Workspace
            </button>
            <button
              onClick={handleSimulate}
              className="px-4 py-2 rounded border border-[#22d3ee] text-[#22d3ee] text-sm font-semibold hover:bg-[#22d3ee]/10 transition-colors"
            >
              Simulate
            </button>
          </div>

          {toast && (
            <div className="rounded border border-green-700 bg-green-900/20 px-3 py-2 text-sm text-green-400">
              {toast}
            </div>
          )}
          {simMsg && (
            <div className="rounded border border-yellow-700 bg-yellow-900/20 px-3 py-2 text-sm text-yellow-400">
              {simMsg}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
