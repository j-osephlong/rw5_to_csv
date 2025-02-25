from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from rw5_to_csv.records.common import get_date_time
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict

if TYPE_CHECKING:
    from rw5_to_csv.machine_state import MachineState


def parse_ss_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow:
    first_line_params = get_standard_record_params_dict(command_block[0])
    dt = get_date_time(command_block, machine_state["tzinfo"] or datetime.UTC)

    return RW5CSVRow(
        PointID=first_line_params["FP"],
        Lat=0,
        Lng=0,
        Elevation=0,
        LocalX=Decimal(0),
        LocalY=Decimal(0),
        LocalZ=Decimal(0),
        HRMS=None,
        VRMS=None,
        VDOP=None,
        HDOP=None,
        PDOP=None,
        TDOP=None,
        GDOP=None,
        Status=None,
        NumSatellites=None,
        Age=None,
        Note=first_line_params["--"],
        RW5RecordType="SS",
        RodHeight=machine_state["HR"],
        InstrumentHeight=machine_state["HI"],
        InstrumentType=machine_state["InstrumentType"],
        DateTime=dt,
    )
