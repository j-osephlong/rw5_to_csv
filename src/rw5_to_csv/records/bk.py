from __future__ import annotations

import math
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
    # CRDB required for total station data
    if not machine_state.crdb_path:
        return []

    first_line_params = get_standard_record_params_dict(command_block[0].strip())

    oc_point_id = first_line_params["OP"]
    bs_point_id = first_line_params["BP"]
    backsigt_angle = dms_to_dd(first_line_params["BS"])

    op_point = get_crdb_point(oc_point_id, machine_state.crdb_path)
    bs_point = get_crdb_point(bs_point_id, machine_state.crdb_path)
    assert op_point.LocalX
    assert op_point.LocalY
    assert op_point.LocalZ
    assert bs_point.LocalX
    assert bs_point.LocalY
    assert bs_point.LocalZ

    backsight_distance = math.sqrt(
        ((op_point.LocalX - bs_point.LocalX) ** 2)
        + ((op_point.LocalY - bs_point.LocalY) ** 2)
        + ((op_point.LocalZ - bs_point.LocalZ) ** 2),
    )

    reflectorless = False
    if len(command_block) > 1:
        reflectorless = "(reflectorless:foresight)" in command_block[1].lower()

    machine_state.Backsights.append(BacksightRow(
        Reflectorless=reflectorless,
        BacksightPointID=bs_point_id,
        OccupiedPointID=oc_point_id,
        BacksightAngleDD=backsigt_angle,
        BacksightDistance=backsight_distance,
    ))

    return []
