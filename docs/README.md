# The Forge – Documentation

Welcome to the official documentation for **The Forge**.

The Forge is a **simulation-driven analysis platform** for Last Epoch, designed to evaluate builds, predict crafting outcomes, and provide optimization insights using backend-driven engines.

---

## 📚 Documentation Index

* [architecture.md](architecture.md) → System overview, engine structure, and simulation math
* [data_models.md](data_models.md) → Core data structures used across the system
* [api_reference.md](api_reference.md) → Full REST API reference with request/response schemas
* [passive_tree.md](passive_tree.md) → Passive tree system design
* [development_roadmap.md](development_roadmap.md) → Master development roadmap and feature plan
* [development_phases.md](development_phases.md) → GitHub workflow phases guide

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
