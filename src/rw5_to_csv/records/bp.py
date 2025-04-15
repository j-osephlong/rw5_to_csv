from __future__ import annotations

from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict

logger = getLogger(__file__)


def parse_bp_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow | None:
    logger.debug(command_block)

    first_line_params = get_standard_record_params_dict(command_block[0].strip())

    return RW5CSVRow(
        PointID=first_line_params["PN"],
        Lat=float(first_line_params["LA"]),
        Lng=float(first_line_params["LN"]),
        Elevation=float(first_line_params["EL"]),
        LocalX=None,
        LocalY=None,
        LocalZ=None,
        HRMS=None,
        VRMS=None,
        HDOP=None,
        VDOP=None,
        PDOP=None,
        TDOP=None,
        GDOP=None,
        Status=None,
        NumSatellites=None,
        Age=None,
        Note=first_line_params["--"],
        RW5RecordType="BP",
        RodHeight=machine_state["HR"],
        InstrumentHeight=machine_state["HI"],
        InstrumentType=machine_state["InstrumentType"],
        DateTime=None,
    )
