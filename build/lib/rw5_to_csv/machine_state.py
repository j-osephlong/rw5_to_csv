from __future__ import annotations

import datetime
from typing import Literal, TypedDict


class MachineState(TypedDict):
    """State of the machine at the point in time of a record."""

    ProcessedCommandBlocks: list[list[str]]
    HR: float | None
    """Machine measured rod height from LS command."""
    HI: float | None
    """Machine instrument height."""
    InstrumentType: Literal["GPS", "TotalStation", ""]
    tzinfo: datetime._TzInfo | None
