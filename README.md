# The Forge

A build optimization and combat simulation toolkit for **Last Epoch**. The Forge helps players plan character builds, simulate damage output against specific enemies, optimize gear through crafting probability analysis, and compare builds — all backed by a deterministic Python simulation engine with 9,900+ tests.

Built as both a community tool and an engineering portfolio project demonstrating full-stack development, simulation systems, and data-driven game analysis.

---

## Features

### Build Planner
- Create and edit character builds with class/mastery selection
- Interactive passive tree with real game node positions, BFS path validation, and hexagonal node rendering
- Skill tree specialization with node point allocation
- Paper-doll gear editor with item picker, unique items, and idol support
- Leveling path tracker — scrollable timeline recording passive allocation order per level

### Stat Engine (8-Layer Pipeline)
- Deterministic stat resolution: Base → Flat → Increased% → More Multipliers → Conversions → Derived → Registry Derived → Conditional
- Equipment set management with slot validation and affix-to-stat routing
- Passive node stat emission with keystone bonuses
- Buff/debuff system with stack behavior and duration decay
- Conditional stat bonuses (while moving, against bosses, enemy frozen, etc.)
- Derived stats: EHP, armor mitigation, dodge chance, health/mana regen

### Combat Simulation
- Skill execution engine computing per-hit damage, crit-weighted average hit, and DPS
- Enemy defense engine applying per-type resistance, armor mitigation, and penetration
- Time-based combat loop with priority-ordered skill rotation and cooldown tracking
- Mana resource gating — skills require mana to cast, mana regenerates per tick
- Ailment DPS (Ignite, Bleed, Poison) computed from proc chance and scaling stats
- Monte Carlo damage variance simulation
- Multi-target encounter simulation with boss phases, spawn waves, and downtime

### Crafting Simulator
- Forging potential cost model with RNG simulation
- Affix tier system with 1,000+ affix definitions
- Monte Carlo simulation across thousands of craft attempts
- Strategy comparison and optimal path search
- Probability visualization with timeline and outcome charts

### Community & Analysis
- Community builds browser with filtering, voting, and comparison
- Build comparison tool (side-by-side stat/DPS/EHP)
- Best-in-slot search engine with weighted affix targeting
- Meta snapshot showing class distribution and trending builds
- Build optimizer with stat sensitivity analysis and upgrade recommendations

### Authentication & Profiles
- Discord OAuth2 login with JWT session management
- User profiles with build history

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| State Management | Zustand, TanStack Query |
| Charts | Recharts |
| Backend | Python 3.11, Flask |
| Database | PostgreSQL 15 |
| Cache / Rate Limiting | Redis 7, Flask-Limiter |
| ORM | SQLAlchemy + Flask-Migrate (Alembic) |
| Auth | Flask-Dance (Discord OAuth2), Flask-JWT-Extended |
| Validation | Marshmallow |
| Testing | pytest (9,900+ tests) |
| Desktop | Electron (optional) |
| Deployment | Docker Compose |

---

## Project Structure

```
le-the-forge/
├── backend/                    Python Flask API + simulation engines
│   ├── app/
│   │   ├── combat/             Combat simulation loop (scenario, simulator)
│   │   ├── constants/          Game constants (crit caps, defense values)
│   │   ├── domain/             Pure domain models + calculators
│   │   │   ├── calculators/    Stateless math (damage, crit, speed, ailments)
│   │   │   └── registries/     O(1) lookup (affix, skill, enemy)
│   │   ├── enemies/            Enemy defense engine
│   │   ├── engines/            Core computation (stat, combat, craft, defense)
│   │   ├── game_data/          Backend-specific JSON + data pipeline
│   │   ├── models/             SQLAlchemy ORM models
│   │   ├── routes/             Flask API endpoints
│   │   ├── schemas/            Marshmallow request/response validation
│   │   ├── services/           Service layer (DB + engine orchestration)
│   │   ├── skills/             Skill execution engine
│   │   └── stats/              Derived + conditional stat layers
│   ├── builds/                 Build definition subsystems
│   ├── buffs/                  Buff lifecycle engine
│   ├── conditions/             Condition model + evaluator
│   ├── encounter/              Multi-enemy encounter system
│   ├── modifiers/              Conditional modifier engine
│   ├── state/                  Simulation state tracking
│   └── tests/                  9,900+ tests
├── frontend/                   React TypeScript UI
│   └── src/
│       ├── components/         Feature components (build, craft, encounter, etc.)
│       ├── lib/                API client, simulation, game data
│       ├── pages/              Route pages
│       ├── store/              Zustand state stores
│       └── types/              TypeScript type definitions
├── data/                       Canonical game data (JSON)
│   ├── classes/                Class definitions, skill trees
│   ├── combat/                 Damage types
│   ├── entities/               Enemy profiles
│   └── items/                  Affixes, base items, crafting rules
├── docs/                       Documentation + screenshots
├── electron/                   Desktop app (Electron wrapper)
├── scripts/                    Utility scripts
├── docker-compose.yml
├── ARCHITECTURE.md             (in backend/) Detailed pipeline reference
├── CONTRIBUTING.md
├── CHANGELOG.md
├── ROADMAP.md
└── LICENSE                     MIT
```

---

## Local Development Setup

### Prerequisites

- Docker Desktop (for PostgreSQL + Redis)
- Python 3.11+
- Node.js 20+

### Quick Start

```bash
# Clone and configure
git clone https://github.com/NickolisK24/le-the-forge.git
cd le-the-forge
cp .env.example .env

# Start database and cache
docker compose up -d db redis

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db upgrade
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask run --port=5050 --debug
```

In a second terminal:

```bash
# Frontend
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:5050/api

### Alternative: Full Docker

```bash
docker compose up --build

# First run only — seed the database
docker compose exec -e PYTHONPATH=/app backend flask db upgrade
docker compose exec -e PYTHONPATH=/app backend flask seed
```

### Running Tests

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

---

## Screenshots

| Page | Screenshot |
|------|-----------|
| Home | ![Home](docs/screenshots/20260323_184859_01_home.png) |
| Community Builds | ![Builds](docs/screenshots/20260323_184859_02_builds.png) |
| Build Planner | ![Build Planner](docs/screenshots/20260323_184859_03_build_new.png) |
| Craft Simulator | ![Craft Simulator](docs/screenshots/20260323_184859_04_craft.png) |
| Build Comparison | ![Compare](docs/screenshots/20260323_184859_05_compare.png) |

---

## What's Coming

From the [roadmap](ROADMAP.md):

- **Phase 4 — Optimization Engine** *(in progress)*: Stat sensitivity analysis, offensive/defensive ranking, upgrade efficiency scoring
- **Phase 5 — Skill Tree UI**: Visual skill tree with mastery gates and node tooltips
- **Phase 6 — Full Build Import**: Gear/passive/skill import from external formats
- **Phase 7 — Advanced Analysis**: Boss encounter simulations, corruption scaling, gear upgrade ranking
- **Phase 8 — Community Tools**: Build comparison tools, meta analytics, shared build reports

Long-term: advanced crafting prediction models, community build databases, encounter-specific optimization, native desktop packaging.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, branch conventions, architecture overview, and PR checklist.

---

## License

[MIT](LICENSE)
