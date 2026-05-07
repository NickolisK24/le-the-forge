# LE Tools Importer Fixture Context Audit

## 1. Purpose

This audit checks existing LE Tools importer tests and fixture-like payloads for the `base_type_id` context needed by future canonical bundle `item_type` resolution.

This does not change importer behavior, activate bundle IDs, change production output, or modify import routes. It only measures diagnostic context availability in local tests and inline mocked payloads.

## 2. Importer Test Sources Inspected

| Path | What it contains | Payload type | Gear records present? | `base_type_id` / `baseTypeID` present? | `subtype_id` / `subTypeID` present? | `item_type` / slot / name fields | Usable by diagnostic report? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/tests/test_importers.py` | Unit tests for `LastEpochToolsImporter` with mocked HTTP and inline `_LET_HTML` | Raw LE Tools-like HTML with `window["buildInfo"]` | No equipment in current LET HTML fixture | No | No | Class, mastery, passives, skills only | Yes, but result is zero gear items |
| `backend/tests/test_build_import.py` | Import factory, importer, route, and preview mapper tests | Inline mocked LET HTML and inline raw `build_info` dictionaries | Yes in `_map_let_build` and `/api/import/let/json` tests | Raw gear uses `id`, not `baseTypeID`; mapped output emits `base_type_id` | No | Raw gear has slot-keyed equipment; mapped output has slot and `base_type_id` | Yes, with caveats |
| `backend/tests/fixtures/sample_character.json` | Generic character fixture | Build/test fixture | No relevant LE Tools import gear | No | No | Character data only | Not useful for this diagnostic |
| `backend/tests/fixtures/le_tools_parsed_gear_context_sample.json` | Developer-only representative parsed gear context sample | Diagnostic fixture created for bundle item context checks | Yes | Yes for ID-backed cases | Yes in subtype-only guard case | `slot`, `item_type`, `baseTypeID`, `subTypeID`, `name` | Yes; representative but not an existing importer fixture |
| `backend/app/services/importers/lastepochtools_importer.py` | Production importer implementation | Code under audit | Parses `equipment` / `gear` | Reads `id`, `baseTypeID`, `baseType`, `base_type_id`; emits `base_type_id` in gear output | Decodes possible `subTypeID` internally for base item name resolution | Emits `slot`, `base_type_id`, `item_name`, `rarity`, `affixes` | Code confirms output context, but was not changed |
| `backend/app/routes/import_route.py` | Import routes and LET JSON preview mapper | Production route/helper under audit | `_map_let_build` delegates to importer gear parser | Mapped output includes `base_type_id` | No public subtype field | Emits mapped gear list | Usable for local diagnostic runs, but route behavior was not changed |

Search terms included `Last Epoch Tools`, `LE Tools`, `lastepochtools`, `import`, `gear`, `equipment`, `baseTypeID`, `subTypeID`, `base_type_id`, and `buildInfo`.

## 3. Context Coverage Results

The existing LET fixtures are inline test payloads rather than reusable JSON fixture files. I ran the developer-only context report against equivalent local payloads from the tests, both before and after `_map_let_build` where applicable.

| Source | Stage | Total items | Resolved | Needs context | Needs review | Deferred | Unresolved | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `backend/tests/test_importers.py::_LET_HTML` | Raw `buildInfo` | 0 | 0 | 0 | 0 | 0 | 0 | Current fixture has no equipment. |
| `backend/tests/test_importers.py::_LET_HTML` | Mapped importer output | 0 | 0 | 0 | 0 | 0 | 0 | No gear output because input has no equipment. |
| `backend/tests/test_build_import.py::_LET_HTML` | Raw `buildInfo` | 0 | 0 | 0 | 0 | 0 | 0 | Current fixture has no equipment. |
| `backend/tests/test_build_import.py::_LET_HTML` | Mapped importer output | 0 | 0 | 0 | 0 | 0 | 0 | No gear output because input has no equipment. |
| `backend/tests/test_build_import.py::TestMapLetBuildGear.test_preview_mapper_populates_gear` | Raw `build_info.equipment` | 3 | 0 | 0 | 0 | 0 | 3 | Raw records contain `id` but no `item_type` or `baseTypeID` field. The diagnostic does not guess from raw numeric `id`. |
| `backend/tests/test_build_import.py::TestMapLetBuildGear.test_preview_mapper_populates_gear` | Mapped output | 3 | 3 | 0 | 0 | 0 | 0 | Mapped output preserves `base_type_id`, allowing resolver inference through `BASE_TYPE_ID_TO_ITEM_TYPE_ID`. |
| `backend/tests/test_build_import.py::TestImportLetFromJson.test_maps_build_info_with_gear` | Raw `build_info.equipment` | 3 | 0 | 0 | 0 | 0 | 3 | Same inline gear payload as preview mapper test. |
| `backend/tests/test_build_import.py::TestImportLetFromJson.test_maps_build_info_with_gear` | Mapped output | 3 | 3 | 0 | 0 | 0 | 0 | Same mapped output behavior as preview mapper test. |
| `backend/tests/fixtures/le_tools_parsed_gear_context_sample.json` | Diagnostic fixture | 16 | 10 | 3 | 1 | 0 | 2 | Representative developer fixture; not a production importer fixture. |

Generated summary report:

```text
docs/generated/le_tools_importer_fixture_context_report.md
```

Important caveat: the inline gear payloads use synthetic numeric `id` values such as `helm: {"id": 5}`. The importer currently maps integer `id` to `base_type_id`, so the mapped diagnostic resolves `base_type_id=5` as `axe` even though the slot is `helmet`. These tests prove that mapped output preserves a numeric context field, but they do not prove realistic LE Tools item type correctness.

## 4. Importer Output Invariance

Production importer code was not changed.

The diagnostic work consumed local copies of existing inline test payloads and the existing mapped output shape. No production module imports the diagnostic report module, and no route or importer output was modified.

Existing focused importer tests were run along with the bundle item context tests. They continued to pass, confirming the current importer behavior and route-facing expectations remain unchanged.

## 5. Findings

- Existing committed LET HTML fixtures do not include equipment, so they cannot measure item type context.
- Existing inline LET gear tests contain synthetic slot-keyed `equipment` records with numeric `id` fields, not explicit `baseTypeID`, `item_type`, or `subTypeID`.
- Raw inline gear records are not directly resolvable by the context report because they lack item type fields and the report intentionally does not guess from raw numeric `id`.
- Mapped importer output preserves `base_type_id`, which is the key context needed by the developer-only resolver.
- Current inline tests do not exercise realistic collapsed slugs such as `axe`, `mace`, `sword`, or `idol_1x1` from raw LE Tools payloads.
- The representative diagnostic fixture covers those collapsed groups, but it is not sourced from an existing importer test fixture.
- Source IDs appear recoverable after importer mapping, but the current inline fixture IDs are too synthetic to prove semantic correctness.
- The earliest useful diagnostic stage is after importer mapping, where `gear[]` contains `base_type_id`, not the raw current test fixture stage.

## 6. Recommendation

Create or capture a developer-only offline LET `buildInfo` fixture with realistic `equipment` records that use actual LE Tools item identifiers, then run both:

1. The production importer parser against the fixture, asserting existing output shape is unchanged.
2. The LE Tools import context dry-run against a copy of the mapped `gear[]`, asserting `production_safe=false` and reporting `resolved` / `needs_context` / `needs_review` / `unresolved`.

Do not modify importer output yet. If realistic raw payloads still lack explicit `baseTypeID`, identify the earliest parser stage where `base_type_id` is decoded and preserve it in a developer-only diagnostic sidecar before any production migration is considered.

## 7. Offline Synthetic BuildInfo Follow-Up

An offline synthetic LET-style fixture now exists at:

```text
backend/tests/fixtures/le_tools_offline_buildinfo_equipment_sample.json
```

The fixture is explicitly marked synthetic and is not claimed to be captured from a live LE Tools payload. It is shaped for the current `LastEpochToolsImporter` / `_map_let_build` path and includes representative equipment entries for armor, collapsed weapon types, idol splits, missing `baseTypeID`, `spear`, unknown type, and subtype-only context.

The importer accepted the fixture directly. For context reporting, a test-local diagnostic copy was needed because the production mapped gear output preserves `base_type_id` but does not expose raw `item_type`. The copy reads `_raw.item_type` where present and does not mutate importer output.

Offline fixture context summary from copied mapped output:

| Metric | Count |
| --- | ---: |
| total_items | 14 |
| resolved | 10 |
| needs_context | 2 |
| needs_review | 1 |
| deferred | 0 |
| unresolved | 1 |

This proves the current importer path can preserve `base_type_id` through mapped output for ID-backed records. It does not prove live LET payload correctness, and it does not change production importer behavior.

## 8. Stage Context Comparison

A more explicit raw-stage versus mapped-output fixture lives at:

```text
backend/tests/fixtures/le_tools_offline_buildinfo_stage_context_sample.json
```

Run the stage comparison command from `backend`:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_stage_context.py
```

JSON:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_stage_context.py --json
```

Generated report:

```text
docs/generated/le_tools_import_stage_context_report.md
```

Stage comparison summary:

| Metric | Count |
| --- | ---: |
| total_items | 12 |
| raw_with_base_type_id | 9 |
| mapped_with_base_type_id | 9 |
| raw_missing_base_type_id | 3 |
| mapped_missing_item_type | 12 |
| needs_test_only_pairing | 11 |
| raw_with_subtype_only | 1 |
| resolved | 8 |
| needs_context | 2 |
| needs_review | 1 |
| unresolved | 1 |

The key result is that mapped importer output preserves `base_type_id`, which is useful for future diagnostics, but it does not expose item type context. The stage comparison therefore uses explicit test-only pairing between raw fixture records and mapped gear records. That pairing is diagnostic-only and does not change importer output.

## 9. Sidecar Builder

A developer-only sidecar builder now consolidates raw, mapped, resolver, and context data:

```text
backend/app/game_data/le_tools_import_context_sidecar.py
```

Command:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py
```

Generated report:

```text
docs/generated/le_tools_import_context_sidecar_report.md
```

The sidecar keeps production importer output unchanged. It copies mapped gear, pairs it with raw fixture records for diagnostics, runs the existing dry-run resolver, and validates that `production_safe=false`, subtype-only records do not resolve, name-only records do not resolve, and collapsed slugs missing `base_type_id` stay `needs_context`.

Sidecar validation report:

```text
docs/generated/le_tools_import_context_sidecar_validation_report.md
```

Current validation status is `warning` with no errors. Warnings are expected because the fixture is synthetic/offline, mapped output lacks item type context, and some records intentionally remain `needs_context`, `needs_review`, or `unresolved`.
