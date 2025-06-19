from __future__ import annotations

import dataclasses
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import datetime

    from rw5_to_csv.records.record import RW5Row


@dataclass
class BacksightRow:
    """Result of a BK record, drawing a backsight line."""

    Reflectorless: bool
    BacksightPointID: str
    OccupiedPointID: str
    BacksightAngleDD: float
    BacksightDistance: float


@dataclass
class MachineState:
    """State of the machine at the point in time of a record."""

    SideshotIDOccupiedPointID: dict[str, str] = dataclasses.field(default_factory=dict)
    Backsights: list[BacksightRow] = dataclasses.field(default_factory=list)
    """List of backsights. Current backsight is the last in the list."""
    Records: OrderedDict[str, RW5Row] = dataclasses.field(default_factory=OrderedDict)
    """Finalized CSV rows, indexed by point id."""
    ProcessedCommandBlocks: list[list[str]] = dataclasses.field(default_factory=list)
    HR: float | None = None
    """Machine measured rod height from LS command."""
    HI: float | None = None
    """Machine instrument height."""
    InstrumentType: Literal["GPS", "TotalStation", ""] = ""
    OccupiedPointID: str | None = None
    PrismApplied: str | None = None
    tzinfo: datetime._TzInfo | None = None
    crdb_path: Path | None = None
