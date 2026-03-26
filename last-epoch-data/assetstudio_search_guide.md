# AssetStudio Search Guide — Last Epoch Data Extraction

## Setup

> ⚠️ **Important:** Game data is NOT in the main `Last Epoch_Data` folder.
> It is packed in Unity Addressables bundles under `StreamingAssets\aa\StandaloneWindows64\`.

1. Launch `tools\AssestStudio\AssetStudioGUI.exe`
2. Load the data bundles — use **File → Load File** (not Load Folder) and select these bundles:

   **Start with these (highest priority):**
   ```
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\database_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\defaultlocalgroup_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\pcg_data_assets_all.bundle
   ```

   **Then add these for actors/enemies:**
   ```
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_misc_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_player_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\monolith_gameplay_assets_all.bundle
   ```

   > You can also try **File → Load Folder** on the entire `StandaloneWindows64\` folder but it may be slow.

3. Wait for load to complete
4. In the **Asset List** tab:
   - Set type filter to **MonoBehaviour**
   - Use the search box for each asset name below

---

## What to Export

For each asset found, right-click → **Export selected asset** → save to the matching folder under `extracted_raw\`.

---

## 1. Affixes

> Save to: `extracted_raw\affixes\`

| Search Term   | Notes                                                    |
| ------------- | -------------------------------------------------------- |
| `AffixList`   | **Primary target** — all affix definitions, tiers, rolls |
| `UniqueAffix` | Unique item-specific affixes                             |
| `SetAffix`    | Set item affixes                                         |

---

## 2. Items

> Save to: `extracted_raw\items\`

| Search Term      | Notes                                             |
| ---------------- | ------------------------------------------------- |
| `ItemList`       | **Primary target** — all base equipment items     |
| `UniqueList`     | All unique items with mods and level requirements |
| `SetBonusesList` | Set item bonuses by set size                      |
| `MaterialList`   | Crafting/prophecy materials                       |
| `IdolList`       | Idol base types                                   |
| `RelicList`      | Relic base types (if present)                     |

---

## 3. Skills & Abilities

> Save to: `extracted_raw\skills\`

| Search Term       | Notes                                                      |
| ----------------- | ---------------------------------------------------------- |
| `AbilityList`     | **Primary target** — all abilities/skills with tags, costs |
| `AbilityTreeData` | Skill tree node definitions                                |
| `SkillTree`       | Alternative name — search both                             |
| `AbilityData`     | Per-ability data objects                                   |

---

## 4. Passive Trees

> Save to: `extracted_raw\passives\`

| Search Term            | Notes                                        |
| ---------------------- | -------------------------------------------- |
| `PassiveTree`          | Generic search — will return per-class trees |
| `SentinelPassiveTree`  | Sentinel class                               |
| `MagePassiveTree`      | Mage class                                   |
| `PrimitivePassiveTree` | Primalist class                              |
| `RoguePassiveTree`     | Rogue class                                  |
| `AcolytePassiveTree`   | Acolyte class                                |
| `PassiveNodeData`      | Individual node definitions                  |
| `MasteryTree`          | Mastery-specific subtrees                    |

> **Tip:** Search just `Passive` with MonoBehaviour filter to see everything at once.

---

## 5. Blessings & Monolith

> Save to: `extracted_raw\blessings\`

| Search Term            | Notes                    |
| ---------------------- | ------------------------ |
| `BlessingList`         | All monolith blessings   |
| `MonolithBlessingList` | Alternative name         |
| `TimelineList`         | Monolith timelines/zones |
| `MonolithList`         | Monolith node data       |
| `EchoList`             | Woven echo types         |

---

## 6. Ailments & Status Effects

> Save to: `extracted_raw\ailments\`

| Search Term        | Notes                                        |
| ------------------ | -------------------------------------------- |
| `AilmentList`      | **Primary target** — all ailment definitions |
| `AilmentData`      | Per-ailment scaling data                     |
| `StatusEffectList` | Non-ailment status effects                   |
| `BuffList`         | Buff definitions                             |

---

## 7. Classes & Masteries

> Save to: `extracted_raw\classes\`

| Search Term          | Notes                       |
| -------------------- | --------------------------- |
| `CharacterClassList` | All character classes       |
| `MasteryList`        | All mastery types per class |
| `ClassData`          | Class-specific data         |

---

## 8. Enemies & Actors

> Save to: `extracted_raw\actors\`

| Search Term     | Notes                    |
| --------------- | ------------------------ |
| `ActorDataList` | Enemy/actor definitions  |
| `MonsterList`   | Monster base types       |
| `BossData`      | Boss-specific data       |
| `ChampionList`  | Champion/rare enemy data |

---

## 9. Loot & Progression

> Save to: `extracted_raw\loot\`

| Search Term       | Notes                |
| ----------------- | -------------------- |
| `LootTableList`   | Drop tables          |
| `ExperienceTable` | XP curve data        |
| `LevelScaling`    | Level scaling values |
| `ProphecyList`    | Prophecy definitions |

---

## 10. Zones & Maps

> Save to: `extracted_raw\zones\`

| Search Term    | Notes               |
| -------------- | ------------------- |
| `WaypointList` | All waypoints/zones |
| `ZoneList`     | Zone definitions    |
| `DungeonList`  | Dungeon definitions |
| `SceneList`    | Scene/area metadata |

---

## 11. Factions & Reputation

> Save to: `extracted_raw\factions\`

| Search Term         | Notes                         |
| ------------------- | ----------------------------- |
| `FactionList`       | All factions (CoF, MG, etc.)  |
| `ReputationList`    | Reputation tier rewards       |
| `FactionRewardList` | Faction-specific item rewards |

---

## Catch-All Searches (do these last)

Run these broad searches to catch anything missed above:

| Search Term                      | What to look for                       |
| -------------------------------- | -------------------------------------- |
| `List` (type: MonoBehaviour)     | Any `*List` asset not already exported |
| `Data` (type: MonoBehaviour)     | Any `*Data` asset not already exported |
| `Table` (type: MonoBehaviour)    | Any `*Table` assets                    |
| `Tree` (type: MonoBehaviour)     | Any remaining tree structures          |
| `Database` (type: MonoBehaviour) | Any `*Database` assets                 |

---

## Export Settings

When exporting MonoBehaviour assets from AssetStudio:

- **Format:** Use "Export selected assets (original)" to get raw binary, **OR**
- **Format:** If AssetStudio offers JSON/dump export, prefer that
- Each asset will export as a `.json` or `.txt` dump file
- Keep the original asset name in the filename

---

## Priority Order

If short on time, do these first:

1. `AffixList` → affixes
2. `ItemList` + `UniqueList` → items
3. `AbilityList` + `AbilityTreeData` → skills
4. `PassiveTree` (all classes) → passives
5. `BlessingList` → blessings
6. `AilmentList` → ailments
7. `CharacterClassList` + `MasteryList` → classes
