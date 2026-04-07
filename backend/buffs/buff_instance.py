"""
BuffInstance — Runtime model for an active buff.

Tracks the live state of a single applied BuffDefinition: remaining duration,
stack count, when it was applied, and an optional source identifier.

Public API:
    BuffInstance(definition, stack_count, remaining_duration, applied_timestamp, source)
    instance.tick(delta_time)  — advance time, clamp remaining_duration to 0
    instance.is_expired        — True when remaining_duration == 0 (non-permanent only)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from buffs.buff_definition import BuffDefinition


@dataclass(slots=True)
class BuffInstance:
    """Runtime state for a single active buff.

    Fields:
        definition         — the immutable template this instance derives from
        stack_count        — current number of stacks (1 ≤ stack_count ≤ definition.max_stacks)
        remaining_duration — seconds left before expiry; None for permanent buffs
        applied_timestamp  — time.monotonic() value recorded at application
        source             — optional identifier for what applied this buff (e.g. skill id)
    """

    definition: BuffDefinition
    stack_count: int = 1
    remaining_duration: Optional[float] = field(default=None, init=False)
    applied_timestamp: float = field(default_factory=time.monotonic)
    source: Optional[str] = None

    def __post_init__(self) -> None:
        self.remaining_duration = self.definition.duration_seconds

    def tick(self, delta_time: float) -> None:
        """Advance time by *delta_time* seconds.

        Reduces remaining_duration by delta_time and clamps it to 0.
        No-op for permanent buffs (remaining_duration is None).
        """
        if self.remaining_duration is None:
            return
        self.remaining_duration = max(0.0, self.remaining_duration - delta_time)

    @property
    def is_expired(self) -> bool:
        """True when the buff has run out of time.

        Always False for permanent buffs (remaining_duration is None).
        """
        if self.remaining_duration is None:
            return False
        return self.remaining_duration == 0.0
