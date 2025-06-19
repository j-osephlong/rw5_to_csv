from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from rw5_to_csv.records.common import get_date_time, get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row
from rw5_to_csv.utils.crdb import get_crdb_point

if TYPE_CHECKING:
    from rw5_to_csv.machine_state import MachineState


def get_ss_offset(
    command_block: list[str],
) -> tuple[str | None, float | None]:
    """Check SS command block for comment record detailing a directional offset."""  # noqa: DOC201
    for line in command_block:
        offset = 0.0
        if line.startswith(("--Out Offset", "--In Offset", "--Right Offset", "--Left Offset")):
            offset = float(line.split(" Offset ")[-1].split(" ")[0])
        if line.startswith("--Out Offset"):
            return ("Out", offset)
        if line.startswith("--In Offset"):
            return ("In", offset)
        if line.startswith("--Right Offset"):
            return ("Right", offset)
        if line.startswith("--Left Offset"):
            return ("Left", offset)
    return (None, None)


def parse_ss_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    # CRDB required for total station data
    if not machine_state.crdb_path:
        return []
    # assert machine state
    assert len(machine_state.Backsights) > 0
    current_backsight = machine_state.Backsights[-1]
    occupied_point = machine_state.Records[current_backsight.OccupiedPointID]

    first_line_params = get_standard_record_params_dict(command_block[0])
    dt = get_date_time(command_block, machine_state.tzinfo or datetime.UTC)

    point_id = first_line_params["FP"]

    sd = float(first_line_params["SD"])  # slope distance a.k.a foresight distance

    # base record off of crdb file to get local coordinates
    record = get_crdb_point(point_id, machine_state.crdb_path)
    record.RW5RecordType = "SS"
    record.Note = first_line_params["--"]
    record.DateTime = dt
    record.ForesightDistance = sd
    # record offset if one exists
    record.OffsetDirection, record.OffsetDistance = get_ss_offset(command_block)

    # add sideshot to sideshot to occupied point dict
    machine_state.SideshotIDOccupiedPointID[point_id] = occupied_point.PointID

    return [record]
