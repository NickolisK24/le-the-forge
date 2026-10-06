# R1 Domain Coverage

Built from `docs/generated/r1_extraction_denominator.json` (report_hash `271a27cd30523f98622aa6991786f81888fb256507d2ff8c9f22de205d6f1de1`) and the R1.5 field survival report. Game 1.4.6 build 22986002 (Unity 6000.0.42f1). The current 1.5.x patch has not been extracted (see R1_CURRENT_PATCH_STATUS.md).

Columns: entries = discovered source classes in the domain; raw = raw evidence state; extractor/export = entries with an extractor / any export; canonical = R1 canonical export; Forge = consumption by production code; field survival = gated status (`blocked` = no build-stamped raw dump yet).

| Domain | Classification | Entries | Raw | Extractor | Export | Canonical export | Forge | Field survival |
|---|---|---|---|---|---|---|---|---|
| ability_mutators | REQUIRED_FUTURE | 110 | RAW_MISSING 110 | 0 | 0 | none | NO_EXPORT 110 | 110 class(es) blocked |
| ability_stat_components | REQUIRED_FUTURE | 21 | RAW_MISSING 21 | 0 | 0 | none | NO_EXPORT 21 | 21 class(es) blocked |
| achievements | PRESERVE_ONLY | 2 | RAW_MISSING 2 | 0 | 0 | none | NO_EXPORT 2 | 2 class(es) blocked |
| affixes | REQUIRED_NOW | 1 | RAW_AVAILABLE 1 | 1 | 1 | affixes.json | CONSUMED 1 | evaluated |
| ailments | REQUIRED_NOW | 2 | RAW_MISSING 2 | 2 | 2 | none | SYNCED_NOT_CONSUMED 2 | 2 class(es) blocked |
| arena | REQUIRED_FUTURE | 2 | RAW_MISSING 2 | 0 | 0 | none | NO_EXPORT 2 | 2 class(es) blocked |
| champions | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| character_classes | REQUIRED_NOW | 2 | RAW_MISSING 2 | 2 | 2 | none | CONSUMED 2 | 2 class(es) blocked |
| corruption | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| cosmetics | PRESERVE_ONLY | 10 | RAW_MISSING 10 | 0 | 0 | none | NO_EXPORT 10 | 10 class(es) blocked |
| crafting_glyphs | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| dialogue | PRESERVE_ONLY | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| dungeons | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| endgame_systems | REQUIRED_FUTURE | 9 | RAW_MISSING 9 | 0 | 0 | none | NO_EXPORT 9 | 9 class(es) blocked |
| enemies | REQUIRED_FUTURE | 3 | RAW_MISSING 3 | 1 | 1 | none | CONSUMED 1, NO_EXPORT 2 | 3 class(es) blocked |
| factions | REQUIRED_FUTURE | 4 | RAW_MISSING 4 | 0 | 0 | none | NO_EXPORT 4 | 4 class(es) blocked |
| game_enums | REQUIRED_NOW | 1 | UNKNOWN 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| idol_altars | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| idol_grids | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| item_bases | REQUIRED_NOW | 1 | RAW_MISSING 1 | 1 | 1 | none | CONSUMED 1 | 1 class(es) blocked |
| loading_tips | PRESERVE_ONLY | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| localization_strings | REQUIRED_NOW | 1 | RAW_MISSING 1 | 1 | 1 | none | SYNCED_NOT_CONSUMED 1 | n/a |
| memories | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| monolith_timelines | REQUIRED_NOW | 2 | RAW_MISSING 1, UNKNOWN 1 | 1 | 1 | none | NO_EXPORT 1, SYNCED_NOT_CONSUMED 1 | 2 class(es) blocked |
| monster_mods | REQUIRED_FUTURE | 5 | RAW_MISSING 5 | 0 | 0 | none | NO_EXPORT 5 | 5 class(es) blocked |
| passive_trees | REQUIRED_NOW | 5 | UNKNOWN 5 | 5 | 5 | passive_trees.json | CONSUMED 5 | evaluated |
| player_attributes | REQUIRED_NOW | 2 | RAW_MISSING 2 | 0 | 0 | none | NO_EXPORT 2 | 2 class(es) blocked |
| presentation_assets | PROVEN_OUT_OF_SCOPE | 7 | RAW_MISSING 7 | 0 | 0 | none | NO_EXPORT 7 | n/a |
| property_definitions | REQUIRED_NOW | 5 | RAW_MISSING 5 | 0 | 0 | none | NO_EXPORT 5 | 5 class(es) blocked |
| prophecies | REQUIRED_FUTURE | 8 | RAW_MISSING 8 | 0 | 0 | none | NO_EXPORT 8 | 8 class(es) blocked |
| quests | REQUIRED_FUTURE | 4 | RAW_MISSING 4 | 3 | 3 | none | NO_EXPORT 1, SYNCED_NOT_CONSUMED 3 | 4 class(es) blocked |
| rewards_and_loot | REQUIRED_FUTURE | 8 | RAW_MISSING 8 | 0 | 0 | none | NO_EXPORT 8 | 8 class(es) blocked |
| set_bonuses | REQUIRED_NOW | 1 | RAW_MISSING 1 | 1 | 1 | none | SYNCED_NOT_CONSUMED 1 | 1 class(es) blocked |
| shrines | REQUIRED_FUTURE | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| skill_damage_components | REQUIRED_NOW | 8 | RAW_MISSING 8 | 6 | 6 | none | CONSUMED 6, NO_EXPORT 2 | 8 class(es) blocked |
| skill_trees | REQUIRED_NOW | 137 | UNKNOWN 137 | 137 | 137 | skill_trees.json | CONSUMED 137 | evaluated |
| skills | REQUIRED_NOW | 3 | RAW_MISSING 3 | 2 | 2 | none | CONSUMED 2, NO_EXPORT 1 | 3 class(es) blocked |
| third_party_presentation | PROVEN_OUT_OF_SCOPE | 159 | RAW_MISSING 159 | 0 | 0 | none | NO_EXPORT 159 | n/a |
| tree_registry | REQUIRED_NOW | 1 | RAW_MISSING 1 | 0 | 0 | none | NO_EXPORT 1 | 1 class(es) blocked |
| ui_buffs | PRESERVE_ONLY | 2 | RAW_MISSING 2 | 2 | 2 | none | SYNCED_NOT_CONSUMED 2 | 2 class(es) blocked |
| unenumerated_source.actors_player_specific_gameplay_assets_all_bundle | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | CONSUMED 1 | n/a |
| unenumerated_source.duplicateassetisolation_assets_all_bundle | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| unenumerated_source.globalgamemanagers_assets | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| unenumerated_source.raw_bundles_actors_misc_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | SYNCED_NOT_CONSUMED 1 | n/a |
| unenumerated_source.raw_bundles_database_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| unenumerated_source.raw_bundles_defaultlocalgroup_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | SYNCED_NOT_CONSUMED 1 | n/a |
| unenumerated_source.raw_bundles_duplicateasset_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | SYNCED_NOT_CONSUMED 1 | n/a |
| unenumerated_source.raw_bundles_localization_en_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | CONSUMED 1 | n/a |
| unenumerated_source.raw_bundles_pcg_data_legacy_bundle_dump | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| unenumerated_source.shared_assets_all_bundle | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 0 | none | NO_EXPORT 1 | n/a |
| unenumerated_source.sharedassets1_assets | UNKNOWN | 1 | RAW_MISSING 1 | 1 | 1 | none | CONSUMED 1 | n/a |
| unique_item_mechanics | REQUIRED_FUTURE | 37 | RAW_MISSING 37 | 0 | 0 | none | NO_EXPORT 37 | 37 class(es) blocked |
| uniques | REQUIRED_NOW | 1 | RAW_MISSING 1 | 1 | 1 | none | CONSUMED 1 | 1 class(es) blocked |
| weaver_tree | REQUIRED_NOW | 1 | UNKNOWN 1 | 1 | 1 | weaver_tree.json | EXPORT_NOT_SYNCED 1 | evaluated |
| woven_echoes | REQUIRED_FUTURE | 2 | RAW_MISSING 2 | 0 | 0 | none | NO_EXPORT 2 | 2 class(es) blocked |
| zones_and_scenes | PRESERVE_ONLY | 5 | RAW_MISSING 5 | 0 | 0 | none | NO_EXPORT 5 | 5 class(es) blocked |
| unclassified.* | UNKNOWN | 733 | | | | | | |

## Coverage (from R1_COVERAGE_METRICS.json)

- REQUIRED_NOW: 174 entries, 144 with a canonical export (entry coverage 0.827586); entity coverage of measurable entries 0.451644 (5660 / 12532); 18 entries not measurable.
- REQUIRED_FUTURE: 221 entries, 0 with a canonical export.
- Field coverage of evaluated domains 0.978261; 270 class domains blocked on missing raw.
- Relationships resolved 0.441414; 8171 unallowlisted dangling.
- Semantic coverage 0 (not part of extraction completeness).

## Audit families (EXT-4) after R1

Every family the audit listed is rediscovered mechanically and classified; none is extracted yet, because its raw input (resources.assets) is not preserved. The operator extraction dumps all of them (raw TypeTree) and wraps them in canonical envelopes.

Correction to the audit: `MaterialList` is not crafting materials. Its il2cpp layout holds rendering Materials and Textures (plus non-presentation fields), so it stays UNKNOWN rather than a crafting domain. Crafting rules live in `GlyphOfInsightReplacementList` (REQUIRED_FUTURE) and in item/affix data.
