from __future__ import annotations

from machine_state import MachineState
from records.record import RW5CSVRow, get_standard_record_params_dict


def parse_ls_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow | None:
    ls_record_params = get_standard_record_params_dict(command_block[0])

    if "HI" in ls_record_params:
        machine_state["HI"] = float(ls_record_params["HI"])
    if "HR" in ls_record_params:
        machine_state["HR"] = float(ls_record_params["HR"])

    return None
