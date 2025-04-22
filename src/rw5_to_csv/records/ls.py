from __future__ import annotations

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict


def parse_ls_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow | None:
    ls_record_params = get_standard_record_params_dict(command_block[0])

    # if we have HI & HR in the record, it indicates a switch to total station shots and we can trust
    # these values as out instrument and rod heights.
    # if we only have HR, it indicates a switch to GPS, and we should not use the HR as rod height.
    # this type of LS record will come immediately after a comment-command in the previous command block that looks like
    # '--Entered Rover HR: 2.0000 m, Vertical'.
    # This (2.0000) is the rod height we want. Zero out instrument height.

    if "HI" in ls_record_params and "HR" in ls_record_params:
        machine_state["HI"] = float(ls_record_params["HI"])
        machine_state["HR"] = float(ls_record_params["HR"])
        machine_state["InstrumentType"] = "TotalStation"
    elif "HI" not in ls_record_params and "HR" in ls_record_params:
        assert len(machine_state["ProcessedCommandBlocks"]) > 0, """GPS LS record without a previous command is invalid."""  # noqa: E501
        if len(machine_state["ProcessedCommandBlocks"]) > 0:
            prev_command = machine_state["ProcessedCommandBlocks"][-1]
            rover_height_prefix = "--Entered Rover HR:"
            for line in prev_command:
                if line.startswith(rover_height_prefix):
                    machine_state["HR"] = float(
                        line.removeprefix(rover_height_prefix).split()[0],
                    )
        machine_state["HI"] = None
        machine_state["InstrumentType"] = "GPS"

    return None
