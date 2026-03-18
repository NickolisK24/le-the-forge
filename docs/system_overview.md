# System Overview

The Forge is a backend-driven simulation platform that evaluates character builds and provides actionable insights.

---

## Core Pipeline

Player Input
↓
Stat Engine
↓
Combat Simulation
↓
Defense Simulation
↓
Analysis Layer
↓
Optimization Engine
↓
Recommendations
↓
Frontend Visualization

---

## Core Systems

### Build Simulation

Calculates:

* DPS
* damage variance
* survivability
* effective health pool

---

### Crafting Predictor

Simulates:

* crafting success rates
* fracture probabilities
* expected outcomes

---

### Optimization Engine

Determines:

* best stat upgrades
* most impactful changes
* defensive improvements

---

## Source of Truth

All calculations occur in the backend.

Frontend responsibilities:

* input handling
* API communication
* visualization
