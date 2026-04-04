"""J6 — Affix Data Model"""

from dataclasses import dataclass

__all__ = ["AffixModel"]


@dataclass(frozen=True)
class AffixModel:
    """
    Immutable representation of a single affix definition.

    For multi-tier affixes the mapper creates one ``AffixModel`` per tier,
    naming them ``<affix_id>_t1``, ``<affix_id>_t2``, etc.

    Attributes
    ----------
    affix_id:
        Unique identifier for this affix (including tier suffix if applicable).
    stat_type:
        The stat that this affix modifies (e.g. ``"fire_resistance"``).
    min_value:
        Minimum roll value.
    max_value:
        Maximum roll value.
    """

    affix_id: str
    stat_type: str
    min_value: float
    max_value: float

    def __post_init__(self) -> None:
        if not self.affix_id:
            raise ValueError("affix_id must not be empty")
        if not self.stat_type:
            raise ValueError("stat_type must not be empty")
        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) must be <= max_value ({self.max_value})"
            )

    @property
    def midpoint(self) -> float:
        """Return the average of min and max values."""
        return (self.min_value + self.max_value) / 2.0

    def to_dict(self) -> dict:
        return {
            "affix_id": self.affix_id,
            "stat_type": self.stat_type,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
