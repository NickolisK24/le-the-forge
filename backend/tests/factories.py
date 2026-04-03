"""
Shared domain-object factories for Phase K+ tests.

Usage
-----
    from tests.factories import skill, enemy, target, multi_target_state

All factories accept keyword overrides so tests only specify what matters.
Zero imports from Flask — pure domain helpers.
"""

from __future__ import annotations

from data.models.skill_model import SkillModel
from data.models.enemy_model import EnemyModel
from data.models.affix_model import AffixModel
from state.state_engine import SimulationState
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager
from state.multi_target_state import MultiTargetState


# ---------------------------------------------------------------------------
# Data-layer factories
# ---------------------------------------------------------------------------

def skill(
    skill_id: str = "fireball",
    base_damage: float = 100.0,
    cooldown: float = 1.0,
    mana_cost: float = 10.0,
    **kw,
) -> SkillModel:
    """Return a SkillModel with sensible defaults."""
    return SkillModel(
        skill_id=skill_id,
        base_damage=base_damage,
        cooldown=cooldown,
        mana_cost=mana_cost,
        **kw,
    )


def enemy(
    enemy_id: str = "dummy",
    max_health: float = 1000.0,
    armor: float = 0.0,
    **kw,
) -> EnemyModel:
    """Return an EnemyModel with sensible defaults."""
    return EnemyModel(
        enemy_id=enemy_id,
        max_health=max_health,
        armor=armor,
        **kw,
    )


def affix(
    affix_id: str = "x_t1",
    stat_type: str = "fire_resistance",
    min_value: float = 10.0,
    max_value: float = 20.0,
) -> AffixModel:
    """Return an AffixModel with sensible defaults."""
    return AffixModel(
        affix_id=affix_id,
        stat_type=stat_type,
        min_value=min_value,
        max_value=max_value,
    )


# ---------------------------------------------------------------------------
# Phase H simulation-state factory
# ---------------------------------------------------------------------------

def sim_state(
    player_health: float = 1000.0,
    target_health: float = 5000.0,
    elapsed_time: float = 0.0,
    **kw,
) -> SimulationState:
    """Return a SimulationState ready for single-target simulation."""
    return SimulationState(
        player_health=player_health,
        target_health=target_health,
        elapsed_time=elapsed_time,
        **kw,
    )


# ---------------------------------------------------------------------------
# Phase I multi-target factories
# ---------------------------------------------------------------------------

def target(
    target_id: str = "t1",
    max_health: float = 1000.0,
    position_index: int = 0,
    **kw,
) -> TargetEntity:
    """Return a TargetEntity with sensible defaults."""
    return TargetEntity(
        target_id=target_id,
        max_health=max_health,
        position_index=position_index,
        **kw,
    )


def target_manager(n: int = 3, hp: float = 1000.0) -> TargetManager:
    """Return a TargetManager with *n* targets at sequential positions."""
    mgr = TargetManager()
    for i in range(n):
        mgr.spawn(TargetEntity(
            target_id=f"t{i + 1}",
            max_health=hp,
            position_index=i,
        ))
    return mgr


def multi_target_state(
    n: int = 3,
    hp: float = 1000.0,
    player_hp: float = 1000.0,
) -> MultiTargetState:
    """Return a MultiTargetState with *n* targets at sequential positions."""
    mgr = target_manager(n=n, hp=hp)
    return MultiTargetState(manager=mgr, player_health=player_hp)
