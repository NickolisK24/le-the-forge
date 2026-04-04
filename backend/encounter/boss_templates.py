"""
Boss Template System (Step 106).

Defines reusable encounter templates for common boss archetypes.
Each template provides a pre-configured EncounterConfig with phases,
spawn waves, and boss stats.

  BossTemplate     — frozen descriptor for a boss encounter
  load_template    — build an EncounterConfig from a BossTemplate
  TEMPLATES        — registry of built-in templates
"""

from __future__ import annotations

from dataclasses import dataclass, field

from encounter.downtime import DowntimeWindow
from encounter.enemy import EncounterEnemy, EnemyArchetype
from encounter.phases import EncounterPhase, PhaseModifiers, PhaseTransitionType
from encounter.spawn_controller import SpawnWave
from encounter.state_machine import EncounterConfig
from encounter.multi_target import HitDistribution, MultiHitConfig


@dataclass(frozen=True)
class BossTemplate:
    """
    Descriptor for a boss encounter template.

    name              — unique template identifier
    boss_health       — boss max health
    boss_armor        — boss flat armor
    boss_resistances  — dict of resistance values
    boss_shield       — optional absorb shield
    fight_duration    — max fight length (seconds)
    tick_size         — simulation tick size
    phases            — phase definitions
    spawn_waves       — enemy wave definitions (enemies built fresh each load)
    downtime_windows  — forced downtime periods
    """
    name:              str
    boss_health:       float
    boss_armor:        float             = 0.0
    boss_resistances:  dict[str, float]  = field(default_factory=dict)
    boss_shield:       float             = 0.0
    fight_duration:    float             = 60.0
    tick_size:         float             = 0.1
    phases:            tuple[EncounterPhase, ...] = field(default_factory=tuple)
    spawn_wave_specs:  tuple[dict, ...]  = field(default_factory=tuple)
    downtime_specs:    tuple[dict, ...]  = field(default_factory=tuple)


def load_template(
    template: BossTemplate,
    base_damage: float = 100.0,
    hit_config:  MultiHitConfig | None = None,
) -> EncounterConfig:
    """
    Build a fresh EncounterConfig from *template*.

    Creates new EncounterEnemy objects on each call so encounters
    start from full health every time.
    """
    boss = EncounterEnemy(
        max_health=template.boss_health,
        current_health=template.boss_health,
        armor=template.boss_armor,
        resistances=dict(template.boss_resistances),
        shield=template.boss_shield,
        max_shield=template.boss_shield,
        name=template.name,
    )

    # Build spawn waves fresh each call
    waves: list[SpawnWave] = []
    for spec in template.spawn_wave_specs:
        enemies = [
            EncounterEnemy(
                max_health=float(spec["health"]),
                current_health=float(spec["health"]),
                armor=float(spec.get("armor", 0.0)),
                name=spec.get("name", "add"),
            )
            for _ in range(spec.get("count", 1))
        ]
        waves.append(SpawnWave(
            name=spec.get("name", "wave"),
            spawn_time=float(spec["spawn_time"]),
            enemies=enemies,
        ))

    downtime: list[DowntimeWindow] = [
        DowntimeWindow(
            name=d.get("name", "downtime"),
            start_time=float(d["start_time"]),
            end_time=float(d["end_time"]),
        )
        for d in template.downtime_specs
    ]

    cfg_hit = hit_config or MultiHitConfig(rng_hit=0.0, rng_crit=99.0)

    return EncounterConfig(
        enemies=[boss],
        fight_duration=template.fight_duration,
        tick_size=template.tick_size,
        base_damage=base_damage,
        hit_config=cfg_hit,
        phases=list(template.phases),
        spawn_waves=waves,
        downtime_windows=downtime,
    )


# ---------------------------------------------------------------------------
# Built-in templates
# ---------------------------------------------------------------------------

TRAINING_DUMMY = BossTemplate(
    name="training_dummy",
    boss_health=1_000_000.0,
    boss_armor=0.0,
    fight_duration=60.0,
)

STANDARD_BOSS = BossTemplate(
    name="standard_boss",
    boss_health=50_000.0,
    boss_armor=500.0,
    boss_resistances={"fire": 40.0, "cold": 40.0, "physical": 20.0},
    fight_duration=120.0,
    phases=(
        EncounterPhase(
            "enrage", PhaseTransitionType.HEALTH_BELOW, 30.0,
            PhaseModifiers(damage_bonus_pct=25.0),
        ),
    ),
)

SHIELDED_BOSS = BossTemplate(
    name="shielded_boss",
    boss_health=30_000.0,
    boss_armor=300.0,
    boss_shield=5_000.0,
    boss_resistances={"fire": 50.0, "void": 60.0},
    fight_duration=90.0,
)

ADD_FIGHT = BossTemplate(
    name="add_fight",
    boss_health=20_000.0,
    boss_armor=200.0,
    fight_duration=60.0,
    spawn_wave_specs=(
        {"name": "wave_1", "spawn_time": 10.0, "health": 2000.0, "count": 3},
        {"name": "wave_2", "spawn_time": 30.0, "health": 3000.0, "count": 2},
    ),
)

MOVEMENT_BOSS = BossTemplate(
    name="movement_boss",
    boss_health=40_000.0,
    boss_armor=400.0,
    fight_duration=90.0,
    downtime_specs=(
        {"name": "move_1", "start_time": 15.0, "end_time": 18.0},
        {"name": "move_2", "start_time": 45.0, "end_time": 48.0},
    ),
)

TEMPLATES: dict[str, BossTemplate] = {
    t.name: t for t in [
        TRAINING_DUMMY, STANDARD_BOSS, SHIELDED_BOSS, ADD_FIGHT, MOVEMENT_BOSS,
    ]
}
