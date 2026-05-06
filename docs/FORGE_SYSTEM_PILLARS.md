# Forge System Pillars

## 1. Purpose

This document defines what The Forge is trying to become and uses that product direction to prioritize:

- simulation work
- product features
- canonical data requirements
- extraction priorities in `last-epoch-data`
- advisory vs authoritative feature labeling

`FORGE_DATA_CONTRACT.md` and `DATA_BUNDLE_SPEC.md` live in `last-epoch-data` and define cross-repo data architecture: bundle shape, schema expectations, compatibility, validation, and source-of-truth boundaries.

This document lives in `le-the-forge` and defines product and system direction for The Forge itself. It should answer why a data family matters, how The Forge intends to use it, and what user-facing confidence label the resulting feature should carry.

The extraction pipeline should be driven by what The Forge needs to be correct, not by extracting everything equally. Data that affects legality, stat truth, user trust, and core simulation correctness should move first. Cosmetic, speculative, or runtime-only mechanics should not displace foundational data work.

## 2. Product Mission

The Forge is a deterministic, transparent, mechanically accurate Last Epoch build analysis engine.

The Forge should help players answer:

- Is this build legal?
- What stats does this build actually have?
- How much damage does this build likely do?
- How survivable is this build?
- What upgrades matter most?
- Which assumptions are verified, estimated, or unknown?

The product should optimize for deterministic results, inspectable formulas, explicit uncertainty, and mechanical accuracy over cosmetic polish. User trust comes from showing the calculation path, the data patch, the source confidence, and the known gaps instead of presenting estimated output as verified truth.

## 3. Core User Promises

1. **Legality**

   The Forge should tell users whether a build, item, passive path, skill tree, or affix setup can exist in-game.

2. **Stat truth**

   The Forge should resolve stats through a deterministic pipeline and explain where stats come from.

3. **Combat insight**

   The Forge should estimate or calculate DPS, ailment damage, proc behavior, minion contribution, and boss performance while clearly labeling confidence.

4. **Survivability insight**

   The Forge should estimate or calculate EHP, mitigation, ward, resistance impact, corruption scaling, and enemy-specific pressure.

5. **Upgrade guidance**

   The Forge should explain which upgrades improve DPS, EHP, or efficiency and why.

6. **Transparency**

   The Forge should tell users when a result is verified, advisory, experimental, estimated, incomplete, or unsupported.

## 4. Feature Status Model

The Forge should use three user-facing statuses.

### Authoritative

Use for features backed by canonical-ready data, validation, deterministic logic, compatible metadata, and sufficient confidence.

Examples eventually:

- item legality
- affix eligibility
- passive allocation legality
- skill tree allocation legality
- stat totals for fully normalized modifiers

### Advisory

Use for useful results that depend on partial, approximate, or lower-confidence data.

Examples currently:

- DPS estimates
- BIS rankings
- boss TTK
- corruption recommendations
- enemy target comparisons
- upgrade scoring when affix pools or enemy profiles are approximated

### Experimental

Use for sandbox, development, or early features where mechanics are incomplete or inferred.

Examples:

- proc-chain simulation
- runtime scripted unique behavior
- minion inheritance
- advanced ailment edge cases
- boss phase scripts
- runtime-only mechanics

A feature can move from Experimental to Advisory to Authoritative only when its data and engine support improve. Status should be attached to the narrowest practical feature surface; one verified sub-calculation does not make a full build report authoritative.

## 5. Pillar 1 - Build Legality

**Goal:** Determine whether a build can exist in-game.

**Covers:**

- class and mastery rules
- passive tree structure
- passive point allocation and prerequisites
- skill specialization tree allocation
- item slots
- item type/subtype rules
- affix eligibility
- level/class requirements
- idol placement and size rules
- unique/set constraints

**Expected feature status:**

Build legality should become Authoritative.

**Data needed from `last-epoch-data`:**

- metadata / manifest
- classes
- masteries
- passive trees
- skill trees
- base items
- item types/subtypes
- affix eligibility
- idols
- uniques
- sets

**Known risks:**

- frontend fallback trees
- hardcoded class/mastery constants
- simplified affix pools
- unresolved item/import IDs

**Definition of done:**

Build legality is deterministic, canonical-backed, validated, and does not depend on silent fallback data.

## 6. Pillar 2 - Stat Resolution

**Goal:** Determine what stats a build actually has.

**Covers:**

- base stats
- attributes
- affixes
- implicits
- blessings
- passives
- skill tree modifiers
- unique and set modifiers
- conditional modifiers
- derived stats
- increased/more/flat/conversion operations
- stat aggregation order

**Expected feature status:**

Stat resolution should be Authoritative for fully normalized modifiers and Advisory where conditional or runtime behavior is unresolved.

**Data needed from `last-epoch-data`:**

- class base stats
- attribute scaling
- affixes and tiers
- affix tags
- implicits
- blessings
- passive node stat payloads
- skill node stat payloads
- unique/set modifier rows
- normalized stat operation model

**Known risks:**

- tooltip/prose parsing
- synthetic passive stat fallbacks
- unmapped passive stat entries
- unique special effects from prose
- conditional mechanics not fully wired into DPS
- manual or hardcoded modifier mappings

**Definition of done:**

The Forge can explain every included stat contribution and label excluded, text-only, deferred, or unresolved mechanics.

## 7. Pillar 3 - Combat Simulation

**Goal:** Estimate or calculate build damage in deterministic combat scenarios.

**Covers:**

- skill base damage
- added damage effectiveness
- damage types
- skill tags
- attack/cast speed
- cooldowns
- mana gating
- crit
- ailments
- armor shred
- damage over time
- hit cadence and tick rates
- conditional DPS
- proc/trigger behavior
- minion contribution
- boss encounter phases

**Expected feature status:**

Combat simulation is Advisory today. Specific sub-calculations can become Authoritative only when they are verified and canonical-backed. Proc chains, minion inheritance, runtime scripts, and advanced ailment edge cases should remain Experimental until verified.

**Data needed from `last-epoch-data`:**

- skill metadata
- skill base damage
- skill effectiveness
- skill tags
- cooldown/mana cost
- hit cadence/tick rates
- ailment behavior
- armor shred mechanics
- conditional skill modifiers
- triggered skill relationships
- minion skill data
- enemy/boss profiles for targets

**Known risks:**

- approximated skill base damage values
- unverified ailment DPS
- minion DPS not modeled
- conditional bonuses not fully wired into combat
- armor shred stacks not accumulated over fight duration
- runtime-only skill behavior
- enemy armor/resistance estimates

**Definition of done:**

Combat results identify which components are verified, advisory, estimated, experimental, or excluded.

## 8. Pillar 4 - Survivability / EHP

**Goal:** Estimate or calculate how much pressure a build can survive.

**Covers:**

- health
- ward
- armor
- resistances
- endurance
- dodge
- block
- crit avoidance
- damage reduction
- recovery
- enemy damage profiles
- corruption scaling
- boss-specific pressure

**Expected feature status:**

Survivability and EHP should remain Advisory until enemy profiles and corruption scaling are canonical-backed. Internal deterministic defense formulas can become Authoritative once their inputs are verified.

**Data needed from `last-epoch-data`:**

- class base defensive stats
- item defensive affixes
- implicits
- blessings
- passives
- enemy profiles
- boss profiles
- enemy damage types
- armor/resistance data
- corruption scaling formulas
- timeline/boss context

**Known risks:**

- enemy armor/resistance estimates
- hardcoded enemy archetypes
- hardcoded corruption formulas
- incomplete boss mechanics
- timeline context not canonical

**Definition of done:**

The Forge separates player-side verified defense math from enemy/corruption assumptions and labels confidence clearly.

## 9. Pillar 5 - Optimization and Upgrade Guidance

**Goal:** Help users decide what to change next.

**Covers:**

- stat sensitivity
- DPS/EHP tradeoffs
- upgrade efficiency
- best-in-slot candidates
- affix priority
- crafting probability
- corruption recommendations
- encounter-specific recommendations

**Expected feature status:**

Optimization and upgrade guidance should remain Advisory until all required legality, stat, combat, enemy, and crafting inputs are canonical-ready. Advanced encounter-specific optimization should remain Experimental until boss and corruption data improves.

**Data needed from `last-epoch-data`:**

- affix pools
- affix tiers
- affix eligibility
- crafting rules
- item bases
- uniques
- idols
- blessings
- normalized modifiers
- skill combat metadata
- enemy/corruption profiles
- boss/timeline context

**Known risks:**

- simplified BIS candidate pools
- approximated enemy profiles
- approximated DPS inputs
- missing item/import resolution
- crafting assumptions
- advisory results looking authoritative

**Definition of done:**

Optimization output shows its assumptions and never presents approximation-backed recommendations as verified truth.

## 10. Pillar 6 - Transparency and Trust

**Goal:** Make The Forge honest, inspectable, and trustworthy.

**Covers:**

- known limitations
- source confidence
- data patch/build visibility
- calculation traces
- formula inspection
- advisory/experimental labels
- missing data warnings
- stale data warnings
- import resolution warnings
- unsupported mechanic explanations

**Expected feature status:**

Transparency and trust should be treated as core product functionality, not polish.

**Data needed from `last-epoch-data`:**

- `metadata.json`
- `manifest.json`
- `validation_status.json`
- `known_gaps.json`
- confidence metadata
- stale/deferred markers
- source hashes where practical
- schema versions

**Known risks:**

- silent fallbacks
- hidden approximations
- stale local/frontend data
- unclear source of truth
- UI presenting advisory results as authoritative

**Definition of done:**

Users and developers can tell what data patch is loaded, which systems are verified, which are advisory, and which mechanics are missing or approximated.

## 11. Data Dependency Priority

Use the pillars to prioritize extraction work.

### Priority A - Foundation / Trust

Needed first:

- metadata
- bundle manifest
- validation status
- schema compatibility
- source confidence
- stale/deferred markers
- known gaps

Why:

Without this, The Forge cannot safely know what it loaded.

### Priority B - Build Legality and Stat Resolution

Needed next:

- base items
- item types/subtypes
- affixes
- affix tiers
- affix eligibility
- affix tags
- idols
- blessings
- passives
- passive trees
- skill trees
- class/mastery data
- implicits
- uniques/sets

Why:

These power the planner, stat model, item systems, and most live-site user interactions.

### Priority C - Combat Correctness

Needed after core legality/stat foundations:

- skill base damage
- skill effectiveness
- damage types
- skill tags
- mana/cooldown
- hit cadence
- ailment behavior
- conditional modifiers
- armor shred behavior
- minion data
- trigger/proc relationships

Why:

These determine whether DPS and combat output can move from advisory toward authoritative.

### Priority D - Enemy and Encounter Authenticity

Needed after combat foundations:

- enemy profiles
- boss profiles
- armor/resistance values
- corruption scaling
- timeline modifiers
- boss phase mechanics

Why:

These determine whether EHP, boss TTK, corruption recommendations, and encounter-specific optimization are trustworthy.

### Priority E - Advanced Runtime Mechanics

Needed last:

- scripted unique/set behavior
- proc chains
- snapshotting
- minion inheritance
- runtime-only mechanics
- hidden tags
- advanced ailment edge cases
- boss scripts

Why:

These are high-impact but unsafe to infer before the lower layers are stable.

## 12. What Not To Build Yet

Do not prioritize these until the foundation is stronger:

- Full proc-chain simulation before normalized modifier and skill metadata contracts exist.
- Advanced boss scripting before enemy/corruption data is trustworthy.
- Minion inheritance modeling before ownership/scaling data is identified.
- Authoritative DPS claims before skill damage/effectiveness/hit cadence are verified.
- Authoritative BIS rankings before affix eligibility and item pools are canonical.
- More UI polish that hides underlying data uncertainty.
- New hardcoded game-data tables that bypass `last-epoch-data`.

## 13. Cross-Repo Planning Rules

Before implementing a feature or extractor, answer:

1. Which system pillar does this support?
2. Is the feature intended to be Authoritative, Advisory, or Experimental?
3. What data families does it require?
4. Are those data families raw, normalized, canonical-ready, or simulation-ready?
5. Are any inputs currently hardcoded, fallback-backed, approximated, or HYBRID?
6. What should the user see if the data is missing, stale, partial, or estimated?
7. Does this reduce approximation debt or add more?
8. Should this work happen in `le-the-forge`, `last-epoch-data`, or both?

## 14. Current Strategic Focus

The current strategic focus is:

1. Finish planning foundation:
   - `FORGE_DATA_CONTRACT.md`
   - `DATA_BUNDLE_SPEC.md`
   - `FORGE_SYSTEM_PILLARS.md`
2. Then implement bundle metadata and compatibility gates.
3. Then migrate Required Now data families toward canonical bundle consumption.
4. Then improve modifier/stat normalization.
5. Then deepen item/unique/set/implicit mechanics.
6. Then improve skill combat metadata.
7. Then improve enemy/corruption authenticity.
8. Then address advanced runtime/scripted mechanics.

The goal is not to slow development. The goal is to avoid building higher-level systems on unstable data assumptions.

## 15. Open Questions

- Which Forge feature should become the first fully Authoritative feature?
- Which data family should be the first end-to-end canonical migration target?
- Should advisory labels be visible to all users or only in advanced/debug views?
- How should known limitations surface in build reports?
- Which current hardcoded data should be treated as generated cache vs legacy debt?
- Should DPS remain globally Advisory until every supported skill has verified base damage?
- Should optimizer output remain Advisory until affix eligibility and enemy profiles are canonical?
- How should The Forge display data patch/build version in the UI?
- What should happen when a user imports a build containing unresolved items or affixes?
- Which missing mechanics most affect user trust today?
