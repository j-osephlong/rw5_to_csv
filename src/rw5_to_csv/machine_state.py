from __future__ import annotations

from typing import TypedDict


class MachineState(TypedDict):
    """State of the machine at the point in time of a record."""

    MeasuredHR: float | None
    """Machine measured rod height from LS command."""
    EnteredHR: float | None
    """Machine rod height."""
    HI: float | None
    """Machine instrument height."""
