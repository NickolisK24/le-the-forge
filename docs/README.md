# The Forge – Documentation

Welcome to the official documentation for **The Forge**.

The Forge is a **simulation-driven analysis platform** for Last Epoch, designed to evaluate builds, predict crafting outcomes, and provide optimization insights using backend-driven engines.

---

## 📚 Documentation Index

* system-overview.md → High-level architecture and data flow
* data-models.md → Core data structures used across the system
* engine-architecture.md → Backend engine structure and responsibilities
* simulation-design.md → Mathematical and simulation logic
* development-roadmap.md → Step-by-step implementation plan
* passive-tree.md → Passive tree system design

---

## 🧠 Core Philosophy

The Forge is built around:

* Deterministic calculations
* Monte Carlo simulations
* Data-driven recommendations

---

## ⚠️ Key Architectural Rule

The backend is the **single source of truth**.

The frontend:

* sends input
* receives results
* renders UI

It does **not** perform game calculations.

---

## 🎯 Goal

To become a high-quality theorycrafting tool for the Last Epoch community and a flagship portfolio project demonstrating full-stack engineering and simulation systems.
