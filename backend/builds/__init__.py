"""
builds — Build Definition System (Phase E).

Provides a standalone, DB-free representation of a player build
and a pipeline that converts it into numeric stats for encounter simulation.

Public API
----------
from builds.build_definition  import BuildDefinition, BuildMetadata
from builds.gear_system        import GearItem, GearAffix, VALID_SLOTS
from builds.buff_system        import Buff, BuffSystem
from builds.passive_system     import PassiveNode, PassiveSystem
from builds.stat_modifiers     import StatModifier, StatModifierEngine, ModifierType
from builds.build_stats_engine import BuildStatsEngine
from builds.serializers        import export_json, import_json, export_url, import_url
"""
