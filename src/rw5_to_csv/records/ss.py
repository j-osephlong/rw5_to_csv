from __future__ import annotations

from decimal import Decimal

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict


def parse_ss_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow:
    first_line_params = get_standard_record_params_dict(command_block[0])

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
        Fixed=None,
        Note=first_line_params["--"],
        RW5RecordType="SS",
        RodHeight=machine_state["HR"],
        InstrumentHeight=machine_state["HI"],
    )
