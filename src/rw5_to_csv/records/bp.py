from __future__ import annotations

from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row

logger = getLogger(__name__)


def parse_bp_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    first_line_params = get_standard_record_params_dict(command_block[0].strip())

    return [RW5Row(
        PointID=first_line_params["PN"],
        Lat=float(first_line_params["LA"]),
        Lng=float(first_line_params["LN"]),
        Elevation=float(first_line_params["EL"]),
        Note=first_line_params["--"],
        RW5RecordType="BP",
    )]
