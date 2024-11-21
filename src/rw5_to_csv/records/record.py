from __future__ import annotations

from decimal import Decimal
from typing import TypedDict

from rw5_to_csv.machine_state import MachineState


class RW5CSVRow(TypedDict):
    """Row of output file."""

    PointID: str
    Lat: float
    Lng: float
    Elevation: float
    LocalX: Decimal
    LocalY: Decimal
    LocalZ: Decimal
    HRMS: float | None
    VRMS: float | None
    Fixed: bool | None
    HDOP: float | None
    VDOP: float | None
    PDOP: float | None
    Note: str
    RW5RecordType: str
    MeasuredRodHeight: float | None
    EnteredRodHeight: float | None
    InstrumentHeight: float | None


def get_standard_record_params_dict(record: str) -> dict[str, str]:
    """Return dict of params from record.

    Standard record:
    GPS,PN5050,LA45.502033173001,LN-66.064406766459,EL-13.312712,--SMFD/DMSE 2024
    Comma seperated params, with 2 char prefix as name of record.
    In the above record, PN is a param and its value is 5050
    """
    return {param[:2]: param[2:].strip() for param in record.split(",")[1:]}


def handle_machine_state_rover_height(
    command_block: list[str],
    machine_state: MachineState,
) -> None:
    """Check for enetered rover height comment command."""
    rover_height_prefix = "--Entered Rover HR:"
    for line in command_block:
        if line.startswith(rover_height_prefix):
            machine_state["EnteredHR"] = float(
                line.removeprefix(rover_height_prefix).split()[0],
            )
