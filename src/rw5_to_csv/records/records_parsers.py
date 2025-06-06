from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from rw5_to_csv.records.bk import parse_bk_record
from rw5_to_csv.records.bp import parse_bp_record
from rw5_to_csv.records.gps import parse_gps_record
from rw5_to_csv.records.ls import parse_ls_record
from rw5_to_csv.records.oc import parse_oc_record
from rw5_to_csv.records.sp import parse_sp_record
from rw5_to_csv.records.ss import parse_ss_record

if TYPE_CHECKING:
    from rw5_to_csv.machine_state import MachineState
    from rw5_to_csv.records.record import RW5Row

RECORD_CSV_PARSERS: dict[str, Callable[[list[str], MachineState], list[RW5Row]]] = {
    "GPS": parse_gps_record,
    "LS": parse_ls_record,
    "SS": parse_ss_record,
    "BP": parse_bp_record,
    "OC": parse_oc_record,
    "SP": parse_sp_record,
    "BK": parse_bk_record,
}
