# Patch Update Guide

How to re-extract game data after a Last Epoch patch.

---

## When to do this

- After any game patch that changes items, skills, affixes, or balance
- You only need the **Windows PC** for this entire process
- The Mac just does `git pull` at the end

---

## Step 1 — Update the game

Let Steam update Last Epoch normally. No action needed here beyond letting it finish.

---

## Step 2 — Archive the old version (optional but recommended)

Copy the key files from the old version before overwriting:

```
patch_versions\
  └── <old_version_number>\
        ├── GameAssembly.dll
        └── Last Epoch_Data\
              └── il2cpp_data\Metadata\global-metadata.dat
```

You don't need to copy the entire game — just those two files are enough to re-dump IL2CPP later if needed.

---

## Step 3 — Update game_files\current

If you keep a separate copy of the game in `game_files\current\`, sync it with the new Steam install:

```
Steam install location (default):
C:\Program Files (x86)\Steam\steamapps\common\Last Epoch\
```

At minimum, copy:

- `GameAssembly.dll`
- `Last Epoch_Data\resources.assets`
- `Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\*.bundle`
- `Last Epoch_Data\il2cpp_data\Metadata\global-metadata.dat`

---

## Step 4 — Re-run IL2CPP dump (only if assemblies changed)

Skip this step if the patch was small (balance only, no new classes/skills/enums).

**How to tell:** Check if `GameAssembly.dll` changed size or timestamp vs. the old version.

If it changed, re-run Il2CppDumper:

1. Open `tools\Il2CppDumper\`
2. Run `Il2CppDumper.exe`
3. Point it at:
   - `game_files\current\GameAssembly.dll`
   - `game_files\current\Last Epoch_Data\il2cpp_data\Metadata\global-metadata.dat`
4. Output to `il2cpp_dump\` (overwrite existing)

This regenerates `DummyDll\` — needed if new enums or classes were added.

---

## Step 5 — Re-export assets from AssetStudio

> Reference: `assetstudio_search_guide.md`

1. Open `tools\AssestStudio\AssetStudioGUI.exe`
2. **File → Load File** — reload these bundles from the updated game:
   ```
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\database_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\defaultlocalgroup_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\pcg_data_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_misc_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_player_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\monolith_gameplay_assets_all.bundle
   ```
3. Filter by **MonoBehaviour**
4. **Export → Export all assets** → export to the matching `extracted_raw\raw_bundles\<bundle_name>\` folder
   - Overwrite existing files

> If you only want to re-export specific changed systems (e.g. affixes only), use the search box to find specific assets and export just those.

---

## Step 6 — Delete cached binary files (if items or affixes changed)

These are cached parses of `resources.assets`. If affixes or items changed, delete them so they get re-parsed fresh:

```
extracted_raw\MasterAffixesList.json   ← delete if affixes changed
extracted_raw\MasterItemsList.json     ← delete if items changed
extracted_raw\UniqueList.json          ← delete if uniques changed
extracted_raw\MonolithTimelines.json   ← delete if timelines/blessings changed
```

If you don't delete them, the pipeline will use the old cached data.

---

## Step 7 — Run the pipeline

From the `LastEpochTools\` root directory:

```bash
python tools/scripts/run_all.py
```

This runs all 13 steps in order and regenerates everything in `exports_json\`.

If only specific systems changed, you can run individual scripts:

```bash
python tools/scripts/process_affixes.py    # affixes only
python tools/scripts/process_items.py      # items only
python tools/scripts/process_skills.py     # skills only
# etc.
```

---

## Step 8 — Validate the output

Quick checks after the pipeline finishes:

- All scripts completed with ✅ (no ❌ failures)
- `exports_json\` files all exist and are non-empty
- Spot check a few values:
  - Open `exports_json\affixes.json` — do names look right?
  - Open `exports_json\skills.json` — do skill names match in-game?
  - Open `exports_json\classes.json` — all 5 classes present?

---

## Step 9 — Commit and push

```bash
git add exports_json/
git add extracted_raw/enums/enums.json
git add extracted_raw/manifest.json
git commit -m "data: patch X.X.X"
git push
```

Replace `X.X.X` with the actual patch number (visible in-game on the main menu).

---

## Step 10 — Pull on MacBook

```bash
git pull
```

Done. The Mac project now has the updated data.

---

## Troubleshooting

| Problem                                      | Fix                                                                          |
| -------------------------------------------- | ---------------------------------------------------------------------------- |
| A script fails with a missing file error     | Check that AssetStudio export completed for that bundle                      |
| Affixes/items look outdated                  | Delete the cached `.json` files in `extracted_raw\` (Step 6) and re-run      |
| New enum values missing                      | Re-run IL2CPP dump (Step 4), then re-run pipeline                            |
| `extract_enums.py` fails                     | Ensure `pythonnet` is installed: `pip install pythonnet`                     |
| Mage class missing                           | Already handled — `process_classes.py` injects it via fallback automatically |
| Pipeline runs but a specific output is wrong | Run that processor individually to see its error output                      |
| Unicode/encoding errors on Windows console   | Run with: `$env:PYTHONUTF8="1"; python tools/scripts/run_all.py`             |

---

## Notes

- **Never manually edit** anything in `exports_json\` — it gets overwritten on every run
- The pipeline is safe to re-run at any time — it always overwrites cleanly
- `extracted_raw\raw_bundles\` is gitignored (18,000+ files) — it stays on Windows only
- `game_files\` is gitignored — the full game install stays on Windows only
