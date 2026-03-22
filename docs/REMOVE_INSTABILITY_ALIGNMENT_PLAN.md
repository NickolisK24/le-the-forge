
# Last Epoch Crafting System Alignment — Remove Instability & Fractures

This document explains:

1. Why instability and fractures should NOT exist in this project
2. What changed in Last Epoch crafting historically
3. What systems should be removed
4. What systems should replace them
5. Exact migration steps
6. Updated development direction

This document exists to **correct system alignment with modern Last Epoch crafting mechanics.**

---

# Core Discovery

Modern Last Epoch crafting **does NOT use instability or fracture mechanics.**

These systems were removed and replaced by:

```
FORGING POTENTIAL (FP)
```

This means:

```
Instability = obsolete
Fracture Chance = obsolete
Fracture Severity = obsolete
```

If your goal is:

```
Accurate Last Epoch crafting simulation
```

Then instability and fractures must be removed.

---

# Historical Context

## Old System (Pre-0.8.4)

Crafting used:

```
Instability
→ Increased with crafting

Fracture Chance
→ Increased with instability

Fracture Outcomes:
- Minor fracture
- Damaging fracture
- Destructive fracture
```

This system could:

```
Brick items
Destroy affixes
Lock crafting
```

This system is **no longer used in the game.**

---

## Modern System (0.8.4 and Later)

Instability and fracture chance were removed.

Replaced with:

```
Forging Potential (FP)
```

New crafting loop:

```
Craft Action
→ FP Cost Rolled
→ FP Reduced
→ If FP = 0 → Crafting Stops
```

Important:

```
Items NEVER fracture now.
Items NEVER get destroyed by crafting.
```

Crafting simply ends when FP runs out.

---

# Why This Matters For Your Project

Your system must match:

```
Modern Last Epoch mechanics
```

Not:

```
Legacy systems from older patches
```

If instability/fracture systems remain:

You will simulate:

```
A dead game system
```

Not current gameplay.

---

# Systems That Should Be Removed

Search your codebase for:

```
instability
fracture
fracture_risk
fracture_item
severity
instability_gain
```

Remove:

```
Instability tracking
Fracture probability math
Fracture severity systems
Fracture outcomes
Instability growth logic
```

Delete or disable:

```
fracture_engine.py
instability models
fracture severity handlers
```

---

# Systems That Should Stay

These systems are correct and should remain:

```
Forge Potential (FP)
FP Cost Rolling
Affix Tier Upgrades
Prefix/Suffix Limits
Sealed Affix Logic
Craft Validation
Affix Database
Simulation Framework
```

These are still core gameplay mechanics.

---

# Systems To Add (Modern Mechanics)

After removing instability systems, focus on:

## Glyph System

Important glyphs:

```
Glyph of Hope
→ Chance to prevent FP loss

Glyph of Chaos
→ Changes affix during upgrade

Glyph of Order
→ Stabilizes upgrade ranges
```

These directly affect crafting.

---

## Rune System

Key rune types:

```
Rune of Removal
Rune of Shattering
Rune of Refinement
Rune of Ascendance
Rune of Creation
```

These dramatically change item states.

They must exist in the simulation.

---

## Tier System Rules

Modern crafting:

```
T1–T5 → Craftable
T6–T7 → Drop Only
```

Validation must enforce this.

---

# Updated Core Craft Loop

Replace instability logic with:

```
Validate Craft
→ Roll FP Cost
→ Apply Craft
→ Reduce FP
→ Check FP Remaining
→ Continue or Stop
```

That is the modern gameplay loop.

---

# Migration Plan (Exact Steps)

Follow these steps in order.

---

## Step 1 — Locate Instability Usage

Search entire repo:

```
instability
fracture
risk
severity
```

Document every occurrence.

---

## Step 2 — Disable Fracture Logic

Remove:

```
fracture_item()
fracture_risk()
severity calculations
```

Temporarily stub them if needed.

---

## Step 3 — Remove Instability From Item Model

Old:

```
item["instability"]
```

Remove completely.

Items should track:

```
forge_potential
prefixes
suffixes
sealed_affix
```

Nothing else.

---

## Step 4 — Simplify Craft Logic

Old:

```
Roll FP
Add Instability
Roll Fracture
Apply Severity
```

New:

```
Roll FP
Apply Craft
Reduce FP
Stop if FP == 0
```

Much simpler.

---

## Step 5 — Update Simulation Engine

Remove:

```
fracture probability tracking
instability growth
severity modeling
```

Replace with:

```
FP exhaustion modeling
FP efficiency tracking
Success rate simulation
```

---

# New Simulation Goals

Simulation should measure:

```
Average FP Used
Success Chance
FP Remaining
Craft Completion Rate
Optimal Craft Order
```

Not fracture chance.

---

# Updated Project Direction

Your project is now:

```
FP-Driven Craft Simulator
```

Not:

```
Risk-Based Fracture Simulator
```

That distinction matters.

---

# Recommended New Priorities

Focus on:

## Priority 1 — FP Accuracy

Ensure:

```
Correct FP ranges
Correct FP costs
Correct FP consumption
```

Everything depends on this.

---

## Priority 2 — Glyph Effects

Glyph behavior dramatically changes outcomes.

Implement:

```
Glyph of Hope logic
Glyph of Chaos logic
Glyph probability effects
```

---

## Priority 3 — Rune Mechanics

These define advanced crafting.

Must support:

```
Removal
Refinement
Transformation
Conversion
```

---

## Priority 4 — Craft Sequencing

Allow:

```
Multiple-step craft planning
Order optimization
Simulation pathing
```

This is where major value exists.

---

# Final Architectural Model

The correct high-level model is:

```
Item
→ Craft Action
→ FP Cost
→ Apply Result
→ Continue Until FP Ends
```

That is the real system.

---

# Final Recommendation

Immediately:

```
Stop building instability systems
Stop building fracture systems
Refocus entirely on FP-driven crafting
```

This aligns your project with:

```
Modern Last Epoch
Real Player Behavior
Real Crafting Outcomes
```

That is the correct direction.
