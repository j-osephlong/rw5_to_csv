from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path

from rw5_to_csv.records.common import get_standard_record_params_dict
from rw5_to_csv.utils.command_blocks import group_lines_into_command_blocks


@dataclass
class RW5Prelude:
    """Fields from JB and MO records from start of RW5 file."""

    JobName: str
    Date: str
    Time: str
    ISODateTime: str
    UserDefined: str | None
    Equipment: str | None
    AntennaType: str | None
    RTKMethod: str | None
    GeoidSeperationFile: str | None


def _get_repeated_attr(command_blocks: list[list[str]], line_prefix: str) -> str:
    values = []  # all equipment strings that actually have shots after them
    pending_value = None  # current equipment string that may or may not actually get used

    for command in command_blocks:
        # ifthere is a pending equipment string, and this command block is a real shot
        if pending_value is not None and command[0].startswith(("GPS,", "SS,")):
            # add to list of equipment
            values.append(pending_value)
            # clear pending
            pending_value = None

        # search each command block for equipment strings
        for line in command:
            if line.startswith(line_prefix):
                # set as pending equipment string
                val = line.removeprefix(line_prefix).strip()
                # if line is already in equipment, skip
                if val not in values:
                    pending_value = val

    return ",\n".join(list(values))


def prelude(rw5_path: Path) -> RW5Prelude:
    """Get fields from the prelude of an RW5 file.

    Parses JB and MO records.
    """  # noqa: DOC201, DOC501
    command_blocks = []
    with rw5_path.open("r", encoding="iso8859-1") as input_file:
        command_blocks = group_lines_into_command_blocks(input_file.readlines())
    jb_record_matches = [
        block for block in command_blocks if block[0].split(",")[0] == "JB"
    ]
    if len(jb_record_matches) == 0:
        msg = "JB record not found."
        raise ValueError(msg)

    jb_record = jb_record_matches[0]

    jb_line_params = get_standard_record_params_dict(jb_record[0])

    name = jb_line_params["NM"]
    date = jb_line_params["DT"]
    date_obj = datetime.datetime.strptime(  # noqa: DTZ007
        date,
        "%m-%d-%Y",
    ).date()  # RW5 uses month-day-year
    time = jb_line_params["TM"]
    time_obj = datetime.datetime.strptime(  # noqa: DTZ007
        time,
        "%H:%M:%S",
    ).time()  # RW5 uses month-day-year
    date_time_iso = datetime.datetime.combine(date_obj, time_obj).isoformat()

    mo_record_matches = [
        block for block in command_blocks if block[0].split(",")[0] == "MO"
    ]
    if len(mo_record_matches) == 0:
        msg = "MO record not found."
        raise ValueError(msg)

    mo_record = mo_record_matches[0]

    user_defined = None
    equipment = _get_repeated_attr(command_blocks, "--Equipment:")
    antenna_type = _get_repeated_attr(command_blocks, "--Antenna Type:")
    rtk_method = _get_repeated_attr(command_blocks, "--RTK Method:")
    geoid_sep_file = None

    for line in mo_record:
        if line.startswith("--User Defined:"):
            user_defined = line.removeprefix("--User Defined:").strip()
        if line.startswith("--Geoid Separation File:"):
            geoid_sep_file = line.removeprefix("--Geoid Separation File:")
            geoid_sep_file = geoid_sep_file.split("\\")[-1].split(" ")[0]

    return RW5Prelude(
        JobName=name,
        Date=date,
        Time=time,
        ISODateTime=date_time_iso,
        UserDefined=user_defined,
        Equipment=equipment,
        AntennaType=antenna_type,
        RTKMethod=rtk_method,
        GeoidSeperationFile=geoid_sep_file,
    )
