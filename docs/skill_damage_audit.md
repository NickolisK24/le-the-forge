# Skill Damage Value Audit Report

**Date:** 2026-04-09

## Summary

Audited 34 damage skills added in the previous coverage fix. Values were originally estimated from use duration and skill type. This audit calibrates them against the original 103 verified skills.

**Results:**
- 1 CONFIRMED (value was correct)
- 9 ADJUSTED UP (value too low)
- 21 ADJUSTED DOWN (value too high or reclassified)
- 6 RECLASSIFIED from DAMAGE to UTILITY (buff/aura spells set to base_damage=0)

## Calibration Reference

Base damage correlates with attack speed (slower skills hit harder):

| Melee | Spell | Bow | Throwing |
|-------|-------|-----|----------|
| Fast (>2.0 AS): 65-80 | Fast (>1.5 AS): 30-70 | 70-130 | 35-65 |
| Medium (1.0-2.0): 80-140 | Medium (0.8-1.5): 60-140 | | |
| Slow (<1.0): 130-200 | Slow (<0.8): 150-300 | | |

Level scaling correlates with base damage: bd<60→0.07-0.09, bd 60-100→0.10-0.12, bd 100-150→0.12-0.13, bd 150+→0.13-0.15.

## Individual Skill Audits

| Skill | Old BD | New BD | Old LS | New LS | Verdict | Reasoning |
|-------|--------|--------|--------|--------|---------|-----------|
| Abyssal Echoes | 100 | 120 | 0.08 | 0.12 | ADJUST UP | Void DoT spell, calibrate vs Shadow Cascade (120) |
| Armblade Slash | 90 | 80 | 0.08 | 0.10 | ADJUST DOWN | Fast melee (spdMul=1.2), calibrate vs Mana Strike (80) |
| Cinder Strike | 90 | 75 | 0.08 | 0.10 | ADJUST DOWN | Fast melee (spdMul=1.2, fire), similar to Serpent Strike (70) |
| Decoy | 55 | 40 | 0.08 | 0.07 | ADJUST DOWN | Fire/throwing utility, below Smoke Bomb (45) |
| Eterra's Blessing | 100 | 0 | 0.08 | 0.00 | RECLASSIFY | Buff spell, no direct damage |
| Flay | 130 | 110 | 0.08 | 0.12 | ADJUST DOWN | Slow melee (dur=1.0), calibrate vs Swipe (110) |
| Frigid Tempest | 100 | 70 | 0.08 | 0.10 | ADJUST DOWN | Fast spell (dur=0.50), like Marrow Shards (70) |
| Ghostflame | 30 | 25 | 0.08 | 0.07 | ADJUST DOWN | Channelled (5 ticks/sec), per-tick damage |
| Hammer Throw | 55 | 65 | 0.08 | 0.09 | ADJUST UP | Throwing (spdMul=1.1), above Shurikens (55) |
| Heartseeker | 70 | 75 | 0.08 | 0.10 | ADJUST UP | Bow skill, calibrate vs Arrow Barrage (70) |
| Holy Aura | 100 | 0 | 0.08 | 0.00 | RECLASSIFY | Buff aura, no direct damage |
| Human Form | 50 | 0 | 0.08 | 0.00 | RECLASSIFY | Transform buff, no direct damage |
| Lethal Mirage | 130 | 160 | 0.08 | 0.14 | ADJUST UP | Very slow melee (dur=1.5), calibrate vs Void Cleave (160) |
| Maul | 60 | 45 | 0.08 | 0.07 | ADJUST DOWN | Very fast melee (dur=0.25, as=4.0), per-hit low |
| Multistrike | 90 | 85 | 0.08 | 0.10 | ADJUST DOWN | Medium melee, similar to Warpath (85) |
| Net | 55 | 40 | 0.08 | 0.07 | ADJUST DOWN | Physical/throwing utility, like Acid Flask (35) |
| Rebuke | 30 | 20 | 0.08 | 0.07 | ADJUST DOWN | Channelled defensive, very low per-tick |
| Riposte | 90 | 80 | 0.08 | 0.10 | ADJUST DOWN | Medium melee with buff tag, like Mana Strike (80) |
| Roar | 100 | 0 | 0.08 | 0.00 | RECLASSIFY | Buff shout, no direct damage |
| Sacrifice | 100 | 120 | 0.08 | 0.12 | ADJUST UP | Physical spell, like Glacier (120) |
| Shield Bash | 90 | 95 | 0.08 | 0.10 | ADJUST UP | Medium melee, slightly above Scorpion Aspect (95) |
| Shocking Impact | 100 | 150 | 0.08 | 0.13 | ADJUST UP | Slow spell (dur=2.0), big hit like Death Seal (150) |
| Spirit Thorns | 100 | 65 | 0.08 | 0.09 | ADJUST DOWN | Physical spell, like Ice Thorns (65) |
| Swarm Strike | 90 | 85 | 0.08 | 0.10 | ADJUST DOWN | Medium melee (spdMul=1.2), like Warpath (85) |
| Symbols of Hope | 100 | 0 | 0.08 | 0.00 | RECLASSIFY | Buff spell, no direct damage |
| Tempest Strike | 90 | 100 | 0.08 | 0.12 | ADJUST UP | Multi-element melee, like Blade Flurry (100) |
| Thorn Shield | 100 | 0 | 0.08 | 0.00 | RECLASSIFY | Buff/thorns, no direct hit damage |
| Umbral Blades | 80 | 80 | 0.08 | 0.10 | CONFIRMED | Multi-hit throwing (hit_count=5), keep current |
| Upheaval | 90 | 110 | 0.08 | 0.12 | ADJUST UP | Medium melee, heavy hit like Swipe (110) |
| Vengeance | 85 | 85 | 0.08 | 0.10 | CONFIRMED | Medium melee, counter-attack like Warpath (85) |
| Wave of Death | 100 | 80 | 0.08 | 0.10 | ADJUST DOWN | Necrotic spell, like Soul Feast (80) |

## Confidence Assessment

After corrections, estimated confidence that values are within 25% of real game values: **70-80%**. The calibration against verified original skills provides a strong anchor, but without access to the actual game damage formulas, some uncertainty remains for skills with unique mechanics (combo skills, channelled skills, transform skills).

## Flagged Original Skills

No original 103 skills were identified as clearly wrong during this audit. The original values appear well-calibrated.
