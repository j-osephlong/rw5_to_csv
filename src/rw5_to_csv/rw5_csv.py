"""rw5_csv.py .

First opened Nov 1st, 2024
Copyright (C) 2014 Joseph Long
"""

from __future__ import annotations

import csv
import datetime
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TypedDict

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_prism_applied, get_standard_record_params_dict
from rw5_to_csv.records.record import (
    RW5Row,
)
from rw5_to_csv.records.records_parsers import RECORD_CSV_PARSERS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


class RW5Prelude(TypedDict):
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


SKIP_LINES_WITH_PREFIXES = ["G0", "G1", "G2", "G3"]


def _prelude_get_equipment(command_blocks: list[list[str]]) -> str:
    equipment_prefix = "--Equipment:"
    equipment_strings = []
    for command in command_blocks:
        for line in command:
            if line.startswith(equipment_prefix):
                # skip items with same serial number as already observed
                if "SN:" in line:
                    serial_number_start_index = line.index("SN:") + 3
                    serial_number_end_index = line.index(",", serial_number_start_index)
                    serial_number = line[
                        serial_number_start_index:serial_number_end_index
                    ]
                    if next(
                        (es for es in list(equipment_strings) if serial_number in es),
                        None,
                    ):
                        continue
                if line in equipment_strings:
                    continue
                if "Demo" in line:
                    continue
                equipment_strings.append(line.removeprefix(equipment_prefix).strip())

    return ",\n".join(list(equipment_strings))


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
    equipment = _prelude_get_equipment(command_blocks)
    antenna_type = None
    rtk_method = None
    geoid_sep_file = None

    for line in mo_record:
        if line.startswith("--User Defined:"):
            user_defined = line.removeprefix("--User Defined:").strip()
        if line.startswith("--Antenna Type:"):
            antenna_type = line.removeprefix("--Antenna Type:").strip()
        if line.startswith("--RTK Method:"):
            rtk_method = line.removeprefix("--RTK Method:").strip()
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


def parse_command(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row] | None:
    """Create a CSV row form an RW5 command block.

    Returns
    -------
    CSV Record

    """
    record_type = command_block[0].split(",")[0]

    prism = get_prism_applied(command_block)
    machine_state.PrismApplied = prism or machine_state.PrismApplied

    if record_type in RECORD_CSV_PARSERS:
        return RECORD_CSV_PARSERS[record_type](command_block, machine_state)
    return None


def group_lines_into_command_blocks(lines: list[str]) -> list[list[str]]:
    """Group file lines into command blocks."""
    commands: list[list[str]] = []
    active_command = []

    """
    group lines in blocks of lines making up a command
    it's assumed that a command starts with a non-comment line, includes all following comment lines
    and ends before the next non comment line

    Example:
        GPS _____________________________   // Command starts
        --blahs blah blah
        --blahs blah blah blah
        --blah                              // Command ends
        GPS ____________________________    // New command starts

    Some lines start with prefixes that we want to ignore and not interrupt the record that they're within

    Example:
        GPS _____________________________   // Command starts
        --blahs blah blah
        G0 blah blah                        // Skip this line (prefix == G0)
        G1 blah blah                        // Skip this line
        G2 blah blah                        // Skip this line
        --blahs blah blah blah
        --blah                              // Command ends
        GPS ____________________________    // New command starts
    """

    stripped_lines = [line.strip() for line in lines]

    for line in stripped_lines:
        # skips lines with specific prefixes, act line they're not even there.
        if any(line.startswith(prefix) for prefix in SKIP_LINES_WITH_PREFIXES):
            continue

        line_is_comment = line.startswith("--")
        # If theres an active command and this line isn't comment
        #   Finish active command, start new command
        if len(active_command) > 0 and line_is_comment is False:
            commands.append(active_command)
            active_command = []

        # Append current line to active_command
        active_command.append(line)

    if len(active_command) > 0:
        commands.append(active_command)

    return commands


def convert(rw5_path: Path, output_path: Path | None, tzinfo: datetime._TzInfo | None = None, crdb_path: Path | None = None):
    """Convert rw5 file to a csv file."""  # noqa: DOC201
    machine_state = MachineState(
        tzinfo=tzinfo,
        crdb_path=crdb_path,
    )

    with rw5_path.open("r", encoding="iso8859-1") as input_file:
        command_blocks = group_lines_into_command_blocks(input_file.readlines())

    for command_block in command_blocks:
        command_rows = parse_command(command_block, machine_state)
        machine_state.ProcessedCommandBlocks.append(command_block)
        if not command_rows:
            continue

        for row in command_rows:
            # set some fields on record from machine state
            row.InstrumentHeight = machine_state.HI
            row.RodHeight = machine_state.HR
            row.InstrumentType = machine_state.InstrumentType
            row.PrismApplied = machine_state.PrismApplied

            # if we've seen a record with this point ID before, replace the old one
            if row.PointID in machine_state.Records:
                # set overwritten flag
                row.Overwritten = True
                machine_state.Records[row.PointID] = row
                # skip rest of iteration
                continue

            # we've never seen this point id before, so just add it to end of lists
            machine_state.Records[row.PointID] = row

    if output_path:
        with output_path.open("w") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=RW5Row.__annotations__.keys(),
                delimiter=",",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows([asdict(r) for r in machine_state.Records.values()])

    return machine_state
