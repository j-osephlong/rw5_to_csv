from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RW5Row:
    """Row of output file."""

    PointID: str
    Note: str
    RW5RecordType: str
    Lat: float | None = None
    Lng: float | None = None
    Elevation: float | None = None
    LocalX: Decimal | None = None
    LocalY: Decimal | None = None
    LocalZ: Decimal | None = None
    HRMS: float | None = None
    VRMS: float | None = None
    Status: str | None = None
    Age: str | None = None
    NumSatellites: str | None = None
    HDOP: float | None = None
    VDOP: float | None = None
    PDOP: float | None = None
    TDOP: float | None = None
    GDOP: float | None = None
    DateTime: datetime.datetime | None = None
    Overwritten: bool = False
    # Machine state
    RodHeight: float | None = None
    """Set by machine state."""
    InstrumentHeight: float | None = None
    """Set by machine state."""
    InstrumentType: str | None = None
    """Set by machine state."""
    PrismApplied: str | None = None
    """Set by machine state."""
    OffsetDirection: str | None = None
    OffsetDistance: float | None = None
