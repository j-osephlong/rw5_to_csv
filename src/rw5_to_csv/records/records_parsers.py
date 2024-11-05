from __future__ import annotations

from collections.abc import Callable

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.gps import parse_gps_record
from rw5_to_csv.records.ls import parse_ls_record
from rw5_to_csv.records.record import RW5CSVRow
from rw5_to_csv.records.ss import parse_ss_record

RECORD_CSV_PARSERS: dict[str, Callable[[list[str], MachineState], RW5CSVRow | None]] = {
    "GPS": parse_gps_record,
    "LS": parse_ls_record,
    "SS": parse_ss_record,
}
