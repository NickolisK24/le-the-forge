# Simulation Design

Defines the mathematical and simulation logic used in The Forge.

---

## Core Approach

* deterministic formulas
* Monte Carlo simulations

---

## Damage Formula

damage = base_damage × (1 + increased_damage) × more_damage

---

## Combat Simulation

* simulate thousands of attacks
* apply crit chance
* apply modifiers
* record results

Outputs:

* average DPS
* variance

---

## Defense Calculation

EHP = health / (1 - damage_reduction)

---

## Crafting Simulation

* simulate crafting attempts
* track outcomes
* compute probabilities

---

## Optimization

* simulate baseline
* apply stat changes
* compare results
* rank improvements
