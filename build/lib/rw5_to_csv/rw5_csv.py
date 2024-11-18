"""rw5_csv.py .

First opened Nov 1st, 2024
Copyright (C) 2014 Joseph Long
"""

from __future__ import annotations

import argparse
import csv
import datetime
import logging
import pprint
import sys
from pathlib import Path
from typing import TypedDict

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict
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
    SerialNumber: str | None
    AntennaType: str | None


SKIP_LINES_WITH_PREFIXES = ["G0", "G1", "G2", "G3"]


def get_prelude(rw5_path: Path) -> RW5Prelude:
    """Get fields from the prelude of an RW5 file.

    Parses JB and MO records.
    """
    command_blocks = []
    with rw5_path.open("r") as input_file:
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
    equipment = None
    serial_number = None
    antenna_type = None

    for line in mo_record:
        if line.startswith("--User Defined:"):
            user_defined = line.removeprefix("--User Defined:").strip()
        if line.startswith("--Equipment:"):
            equipment = line.removeprefix("--Equipment:").strip()
            serial_number_start_index = equipment.index("SN:") + 3
            serial_number_end_index = equipment.index(",", serial_number_start_index)
            serial_number = equipment[serial_number_start_index:serial_number_end_index]
        if line.startswith("--Antenna Type:"):
            antenna_type = line.removeprefix("--Antenna Type:").strip()

    return RW5Prelude(
        JobName=name,
        Date=date,
        Time=time,
        ISODateTime=date_time_iso,
        UserDefined=user_defined,
        Equipment=equipment,
        SerialNumber=serial_number,
        AntennaType=antenna_type,
    )


def parse_command(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow | None:
    """Create a CSV row form an RW5 command block.

    Returns
    -------
    CSV Record

    """
    record_type = command_block[0].split(",")[0]

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

    return commands  # noqa: DOC201


def convert(rw5_path: Path, output_path: Path | None):
    """Convert rw5 file to a csv file."""
    machine_state = MachineState(
        {
            "HI": None,
            "HR": None,
        },
    )

    command_blocks = []

    with rw5_path.open("r") as input_file:
        command_blocks.extend(group_lines_into_command_blocks(input_file.readlines()))

    parsed_commands: list[RW5CSVRow] = []

    for command_block in command_blocks:
        parsed_command = parse_command(command_block, machine_state)
        if parsed_command:
            parsed_commands.append(parsed_command)

    if output_path:
        with output_path.open("w") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=RW5CSVRow.__annotations__.keys(),
                delimiter=",",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(parsed_commands)

    return parsed_commands


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RW5 files to CSV files.")
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    parser.add_argument("--prelude", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    if args.prelude:
        prelude = get_prelude(input_path)
        logger.info(pprint.pformat(prelude))
    else:
        convert(input_path, output_path)
