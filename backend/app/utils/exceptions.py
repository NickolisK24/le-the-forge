"""
Domain exceptions for The Forge.

All custom exceptions inherit from ForgeError so the global error handler
can catch them uniformly and return structured JSON responses.
"""


class ForgeError(Exception):
    """Base exception for all Forge domain errors."""
    status_code = 400

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class BuildValidationError(ForgeError):
    """Raised when a build is incomplete or invalid for simulation."""
    status_code = 422


class SimulationError(ForgeError):
    """Raised when a simulation fails unexpectedly."""
    status_code = 500


class CraftingError(ForgeError):
    """Base for crafting-related errors."""
    status_code = 400


class InsufficientForgePotentialError(CraftingError):
    """Raised when forge potential is too low for the requested action."""

    def __init__(self, needed: int, available: int):
        super().__init__(
            f"Insufficient Forge Potential. Need {needed}, have {available}."
        )
        self.needed = needed
        self.available = available
