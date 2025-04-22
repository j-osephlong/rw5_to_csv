from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TypedDict


class RW5CSVRow(TypedDict):
    """Row of output file."""

    PointID: str
    Lat: float
    Lng: float
    Elevation: float
    LocalX: Decimal | None
    LocalY: Decimal | None
    LocalZ: Decimal | None
    HRMS: float | None
    VRMS: float | None
    Status: str | None
    Age: str | None
    NumSatellites: str | None
    HDOP: float | None
    VDOP: float | None
    PDOP: float | None
    TDOP: float | None
    GDOP: float | None
    Note: str
    RW5RecordType: str
    RodHeight: float | None
    InstrumentHeight: float | None
    InstrumentType: str
    DateTime: datetime.datetime | None
    Overwritten: bool


def get_standard_record_params_dict(record: str) -> dict[str, str]:
    """Return dict of params from record.

    Standard record:
    GPS,PN5050,LA45.502033173001,LN-66.064406766459,EL-13.312712,--SMFD/DMSE 2024
    Comma seperated params, with 2 char prefix as name of record.
    In the above record, PN is a param and its value is 5050
    """
    return {param[:2]: param[2:].strip() for param in record.split(",")[1:]}
