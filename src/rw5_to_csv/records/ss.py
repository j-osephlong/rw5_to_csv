from __future__ import annotations

import datetime
import math
from decimal import Decimal
from typing import TYPE_CHECKING

from rw5_to_csv.records.common import get_date_time, get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row
from rw5_to_csv.utils.dms import dms_to_dd

if TYPE_CHECKING:
    from rw5_to_csv.machine_state import MachineState


def get_ss_offset(
    command_block: list[str],
) -> tuple[str | None, float | None]:
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
    # assert machine state
    assert machine_state.HR is not None
    assert machine_state.HI is not None
    assert len(machine_state.Backsights) > 0
    current_backsight = machine_state.Backsights[-1]
    occupied_point = machine_state.Records[current_backsight.FromPointID]
    bk_point = machine_state.Records[current_backsight.ToPointID]
    assert occupied_point.LocalX is not None
    assert occupied_point.LocalY is not None
    assert occupied_point.LocalZ is not None
    assert bk_point.LocalX is not None
    assert bk_point.LocalY is not None
    assert bk_point.LocalZ is not None

    first_line_params = get_standard_record_params_dict(command_block[0])
    dt = get_date_time(command_block, machine_state.tzinfo or datetime.UTC)

    point_id = first_line_params["FP"]

    # add sideshot to sideshot to occupied point dict
    machine_state.SideshotIDOccupiedPointID[point_id] = occupied_point.PointID

    ar = dms_to_dd(first_line_params["AR"])
    ze = dms_to_dd(first_line_params["ZE"])
    sd = float(first_line_params["SD"])

    # convert angles to rads
    bs_rad = math.radians(current_backsight.BacksightAngleDD)
    ar_rad = math.radians(ar)
    ze_rad = math.radians(ze)

    # cotangent is equal to 1 / tan
    bs_azimuth_dd = 1 / math.tan(
        math.radians(
            (bk_point.LocalY - occupied_point.LocalY)
            / (bk_point.LocalX - occupied_point.LocalX),
        ),
    )

    # normalize it
    bk_x_greater = bk_point.LocalX > occupied_point.LocalX
    bk_y_greater = bk_point.LocalY > occupied_point.LocalY
    # Quad 4
    if bk_x_greater and not bk_y_greater:
        bs_azimuth_dd = 180 - bs_azimuth_dd
    # Quad 3
    elif not bk_x_greater and not bk_y_greater:
        bs_azimuth_dd = 180 + bs_azimuth_dd  # noqa: PLR6104
    # Quad 2
    elif not bk_x_greater and bk_y_greater:
        bs_azimuth_dd = bs_azimuth_dd + 360  # noqa: PLR6104

    # azimuth to side shot
    ss_angle_rad = ar_rad - bs_rad
    # normalize to be within [0, 2pi)
    if ss_angle_rad >= 2 * math.pi:
        ss_angle_rad -= 2 * math.pi

    fs_azimuth_rad = math.radians(bs_azimuth_dd) + (ss_angle_rad)

    # calc horizontal distance
    hd = sd * math.sin(ze_rad)

    easting_delta = hd * math.sin(fs_azimuth_rad)
    northing_delta = hd * math.cos(fs_azimuth_rad)
    elevation_delta = sd * math.cos(ze_rad) - (machine_state.HR - machine_state.HI)

    easting = occupied_point.LocalX + Decimal(easting_delta)
    northing = occupied_point.LocalY + Decimal(northing_delta)
    elevation = occupied_point.LocalZ + Decimal(elevation_delta)

    record = RW5Row(
        PointID=point_id,
        Note=first_line_params["--"],
        RW5RecordType="SS",
        DateTime=dt,
        LocalX=easting,
        LocalY=northing,
        LocalZ=elevation,
    )

    # record offset if one exists
    record.OffsetDirection, record.OffsetDistance = get_ss_offset(command_block)

    return [record]
