from __future__ import annotations

from decimal import Decimal
from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row

logger = getLogger(__name__)


def parse_oc_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    """Parse OC record and sets occupied point.

    Ex:
        `OC,OPTEMP1,N 7366892.84678,E 2532861.82060,EL45.212,--`
    """  # noqa: DOC201
    first_line_params = get_standard_record_params_dict(command_block[0].strip())
    point_id = first_line_params["OP"]

    machine_state.OccupiedPointID = point_id
    return [RW5Row(
        PointID=point_id,
        LocalX=Decimal(first_line_params["E "]),
        LocalY=Decimal(first_line_params["N "]),
        LocalZ=Decimal(first_line_params["EL"]),
        Note=first_line_params["--"],
        RW5RecordType="OC",
    )]
