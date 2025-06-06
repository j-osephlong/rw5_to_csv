from __future__ import annotations

from decimal import Decimal
from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row

logger = getLogger(__name__)


def parse_sp_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    """Parse store point record.

    Ex:
        `SP,PNTEMP1,N 7366892.8468,E 2532861.8206,EL45.2120,--`
    """  # noqa: DOC201
    first_line_params = get_standard_record_params_dict(command_block[0].strip())

    return_rows = [
        RW5Row(
            PointID=first_line_params["PN"],
            LocalX=Decimal(first_line_params["E "]),
            LocalY=Decimal(first_line_params["N "]),
            LocalZ=Decimal(first_line_params["EL"]),
            Note=first_line_params["--"],
            RW5RecordType="SP",
        ),
    ]

    return return_rows
