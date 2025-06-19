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

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_prism_applied
from rw5_to_csv.records.record import (
    RW5Row,
)
from rw5_to_csv.records.records_parsers import RECORD_CSV_PARSERS
from rw5_to_csv.utils.command_blocks import group_lines_into_command_blocks

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


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


def convert(rw5_path: Path, output_path: Path | None, tzinfo: datetime._TzInfo | None = None, crdb_path: Path | None = None, ignore_missing_shots: bool = False):
    """Convert rw5 file to a csv file."""  # noqa: DOC201
    machine_state = MachineState(
        tzinfo=tzinfo,
        crdb_path=crdb_path,
    )

    with rw5_path.open("r", encoding="iso8859-1") as input_file:
        command_blocks = group_lines_into_command_blocks(input_file.readlines())

    for command_block in command_blocks:
        try:
            command_rows = parse_command(command_block, machine_state)
        except KeyError:
            if ignore_missing_shots:
                continue
            raise
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
