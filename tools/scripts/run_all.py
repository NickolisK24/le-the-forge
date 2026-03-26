"""
run_all.py
==========
Master script — runs the full extraction pipeline in order.

Steps:
  1. extract_enums.py   — extract enums from DummyDlls
  2. classify.py        — classify all raw bundle JSON files
  3. process_skills.py  — build skills.json
  4. process_classes.py — build classes.json
  5. process_ailments.py — build ailments.json
  [more processors added here as data becomes available]

Usage:
    python tools/scripts/run_all.py
"""

import os
import sys
import subprocess
import time

# Ensure UTF-8 output on Windows consoles (handles special chars in print statements)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Force UTF-8 in all child processes (PYTHONUTF8=1 propagated via env)
os.environ.setdefault("PYTHONUTF8", "1")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE = [
    ("Extract Enums",        "extract_enums.py"),
    ("Classify Assets",      "classify.py"),
    ("Process Skills",       "process_skills.py"),
    ("Process Classes",      "process_classes.py"),
    ("Process Ailments",     "process_ailments.py"),
    ("Process Localization", "process_localization.py"),
    ("Process Skill Trees",  "process_skill_trees.py"),
    ("Process Affixes",      "process_affixes.py"),
    ("Process Items",        "process_items.py"),
    ("Process Uniques",      "process_uniques.py"),
    ("Process Timelines",    "process_timelines.py"),
    ("Process Monster Mods", "process_monster_mods.py"),
    ("Process Loot Tables",  "process_loot.py"),
]


def run_step(label: str, script: str) -> bool:
    path = os.path.join(SCRIPTS_DIR, script)
    if not os.path.exists(path):
        print(f"  ⏭️  {label} — SKIPPED (script not found: {script})")
        return True

    print(f"\n{'='*60}")
    print(f"  ▶ {label}")
    print(f"{'='*60}")
    t = time.time()

    result = subprocess.run([sys.executable, path], capture_output=False)

    elapsed = time.time() - t
    if result.returncode == 0:
        print(f"  ✅ {label} completed in {elapsed:.1f}s")
        return True
    else:
        print(f"  ❌ {label} FAILED (exit code {result.returncode})")
        return False


def main():
    print("🚀 Last Epoch Data Extraction Pipeline")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Scripts: {SCRIPTS_DIR}")

    failed = []
    for label, script in PIPELINE:
        ok = run_step(label, script)
        if not ok:
            failed.append(label)

    print(f"\n{'='*60}")
    if not failed:
        print("✅ All steps completed successfully!")
    else:
        print(f"❌ {len(failed)} step(s) failed:")
        for f in failed:
            print(f"   - {f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
