from __future__ import annotations

from logging import getLogger

from rw5_to_csv.machine_state import BacksightRow, MachineState
from rw5_to_csv.records.common import get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row
from rw5_to_csv.utils.crdb import get_crdb_point
from rw5_to_csv.utils.dms import dms_to_dd

logger = getLogger(__name__)


def parse_bk_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    """Parse BK (backsight) record.

    This creates a backsight entry in a seperate backsights list.

    Ex: `
        BK,OPTEMP1,BPCP5,BS120.5809,BC120.5809
        --P.C. mm Applied: 0.0000 (Reflectorless:foresight)
        `
    """  # noqa: DOC201
    first_line_params = get_standard_record_params_dict(command_block[0].strip())

    from_point_id = first_line_params["OP"]
    to_point_id = first_line_params["BP"]
    backsigt_angle = dms_to_dd(first_line_params["BS"])

    reflectorless = False
    if len(command_block) > 1:
        reflectorless = "(reflectorless:foresight)" in command_block[1].lower()

    machine_state.Backsights.append(BacksightRow(
        Reflectorless=reflectorless,
        FromPointID=from_point_id,
        ToPointID=to_point_id,
        BacksightAngleDD=backsigt_angle,
    ))

    # to point may not be in file, so see if we can get it from crdb
    new_records = []
    if to_point_id not in machine_state.Records and machine_state.crdb_path:
        crdb_record = get_crdb_point(to_point_id, crdb_path=machine_state.crdb_path)
        if crdb_record is not None:
            new_records = [crdb_record]

    return new_records
