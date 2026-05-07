# LE Tools Importer Fixture Context Report

- production_safe: false
- source: existing local importer tests and inline fixture-like payloads
- importer behavior changed: false
- network calls made: false

## Coverage Summary

| Source | Stage | Total items | Resolved | Needs context | Needs review | Deferred | Unresolved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `backend/tests/test_importers.py::_LET_HTML` | Raw `buildInfo` | 0 | 0 | 0 | 0 | 0 | 0 |
| `backend/tests/test_importers.py::_LET_HTML` | Mapped output | 0 | 0 | 0 | 0 | 0 | 0 |
| `backend/tests/test_build_import.py::_LET_HTML` | Raw `buildInfo` | 0 | 0 | 0 | 0 | 0 | 0 |
| `backend/tests/test_build_import.py::_LET_HTML` | Mapped output | 0 | 0 | 0 | 0 | 0 | 0 |
| `TestMapLetBuildGear.test_preview_mapper_populates_gear` | Raw `build_info.equipment` | 3 | 0 | 0 | 0 | 0 | 3 |
| `TestMapLetBuildGear.test_preview_mapper_populates_gear` | Mapped output | 3 | 3 | 0 | 0 | 0 | 0 |
| `TestImportLetFromJson.test_maps_build_info_with_gear` | Raw `build_info.equipment` | 3 | 0 | 0 | 0 | 0 | 3 |
| `TestImportLetFromJson.test_maps_build_info_with_gear` | Mapped output | 3 | 3 | 0 | 0 | 0 | 0 |
| `backend/tests/fixtures/le_tools_parsed_gear_context_sample.json` | Diagnostic fixture | 16 | 10 | 3 | 1 | 0 | 2 |

## Mapped Inline Gear Detail

The existing inline gear tests use:

```json
{
  "equipment": {
    "helm": {"id": 5, "affixes": [], "ir": 0, "ur": 0},
    "weapon": {"id": 10, "affixes": [], "ir": 0, "ur": 0},
    "belt": {"id": 7, "affixes": [], "ir": 0, "ur": 0}
  }
}
```

After current importer mapping, the diagnostic sees:

| Slot | Inferred Forge item type | `base_type_id` | Resolver status | Bundle item type |
| --- | --- | ---: | --- | --- |
| `helmet` | `axe` | 5 | resolved | `one_handed_axe` |
| `weapon` | `wand` | 10 | resolved | `wand` |
| `belt` | `mace` | 7 | resolved | `one_handed_maces` |

This proves mapped output carries `base_type_id`, but the inline IDs are synthetic and not semantically aligned with their slots. It should not be used as evidence that realistic LET gear item type mapping is correct.

## Findings

- Current LET HTML fixtures do not include equipment.
- Current inline gear fixtures are useful for output-shape invariance, but not realistic item type semantics.
- Raw inline gear fixtures do not directly feed the dry-run resolver because they lack `item_type` / `baseTypeID` fields.
- Mapped importer output preserves `base_type_id`, which is sufficient context for developer-only resolver diagnostics.
- A realistic offline LET `buildInfo` fixture is needed before evaluating true importer item type coverage.

## Recommendation

Add a developer-only offline LET `buildInfo` fixture with realistic equipment identifiers, then run the importer and context report against copied mapped output while asserting importer output shape remains unchanged.
