from __future__ import annotations

from typing import Callable

from machine_state import MachineState
from records.gps import parse_gps_record
from records.ls import parse_ls_record
from records.record import RW5CSVRow
from records.ss import parse_ss_record

RECORD_CSV_PARSERS: dict[str, Callable[[list[str], MachineState], RW5CSVRow | None]] = {
    "GPS": parse_gps_record,
    "LS": parse_ls_record,
    "SS": parse_ss_record,
}
