from __future__ import annotations

from decimal import Decimal
from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict

logger = getLogger(__file__)

HRMS_LINE_START = "--HRMS Avg:"
VRMS_LINE_START = "--VRMS Avg:"
FIXED_READINGS_LINE_START = "--Fixed Readings:"


def _get_hrms(command_block: list[str]) -> float:
    hrms_line_match = [
        line for line in command_block if line.strip().startswith("--HRMS:")
    ]
    if len(hrms_line_match) > 0:
        # Type A parsing.
        hrms_line = hrms_line_match[0]
        hrms_line_params = {
            param.split(":")[0]: param.split(":")[1].strip()
            for param in hrms_line.strip().removeprefix("--").split(", ")
        }
        return float(hrms_line_params["HRMS"])

    # Type B parsing.
    logger.info("Type A parsing for HRMS failed, HRMS line not found. Trying Type B.")
    hrms_line_match = [
        line for line in command_block if line.strip().startswith(HRMS_LINE_START)
    ]
    if len(hrms_line_match) == 0:
        msg = "HRMS line not found."
        raise ValueError(msg)
    """Parse HRMS Avg from line:
        --HRMS Avg: 0.0058 SD: 0.0004 Min: 0.0048 Max: 0.0062
        """
    hrms_line = hrms_line_match[0].strip()
    return float(
        hrms_line[
            len(HRMS_LINE_START) : hrms_line.find("SD:", len(HRMS_LINE_START))
        ].strip(),
    )


def _get_vrms(command_block: list[str]) -> float:
    hrms_line_match = [
        line for line in command_block if line.strip().startswith("--HRMS:")
    ]
    if len(hrms_line_match) > 0:
        # Type A parsing.
        hrms_line = hrms_line_match[0]
        hrms_line_params = {
            param.split(":")[0]: param.split(":")[1].strip()
            for param in hrms_line.strip().removeprefix("--").split(", ")
        }
        return float(hrms_line_params["VRMS"])

    # Type B parsing.
    logger.info("Type A parsing for VRMS failed, VRMS line not found. Trying Type B.")
    vrms_line_match = [
        line for line in command_block if line.strip().startswith(VRMS_LINE_START)
    ]
    if len(vrms_line_match) == 0:
        msg = "VRMS line not found."
        raise ValueError(msg)
    """Parse VRMS Avg from line:
        --VRMS Avg: 0.0058 SD: 0.0004 Min: 0.0048 Max: 0.0062
        """
    vrms_line = vrms_line_match[0].strip()
    return float(
        vrms_line[
            len(VRMS_LINE_START) : vrms_line.find("SD:", len(VRMS_LINE_START))
        ].strip(),
    )


def _get_fixed(command_block: list[str]) -> bool | None:
    hrms_line_match = [
        line for line in command_block if line.strip().startswith("--HRMS:")
    ]
    if len(hrms_line_match) > 0:
        # Type A parsing.
        hrms_line = hrms_line_match[0]
        hrms_line_params = {
            param.split(":")[0]: param.split(":")[1].strip()
            for param in hrms_line.strip().removeprefix("--").split(", ")
        }
        return hrms_line_params["STATUS"] in {"FIXED", "FIXED+"}

    # Type B parsing.
    logger.info(
        "Type A parsing for fixed status failed, fixed status line not found. Trying Type B.",
    )
    """Parse fixed status (when # readings == # fixedd readings):
        --Fixed Readings: 10 of 10
        """
    fixed_line_match = [
        line
        for line in command_block
        if line.strip().startswith(FIXED_READINGS_LINE_START)
    ]
    if len(fixed_line_match) == 0:
        logger.info(
            "Type B parsing for fixed status failed, fixed status line not found. Returning None.",
        )
        return None
    fixed_readings_line = fixed_line_match[0].strip()
    fixed_readings = fixed_readings_line.removeprefix(
        FIXED_READINGS_LINE_START,
    ).strip()

    [fixed_readings_count, readings_count] = fixed_readings.split(" of ")
    return fixed_readings_count == readings_count


def parse_gps_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow | None:
    logger.debug(command_block)

    first_line_params = get_standard_record_params_dict(command_block[0].strip())
    second_line_params = get_standard_record_params_dict(command_block[1].strip())

    # get hrms, vrms, and fixed status
    try:
        hrms = _get_hrms(command_block)
        vrms = _get_vrms(command_block)
        is_fixed = _get_fixed(command_block)
    except ValueError:
        logger.exception("Skipping record.")
        return None

    return RW5CSVRow(
        PointID=first_line_params["PN"],
        Lat=float(first_line_params["LA"]),
        Lng=float(first_line_params["LN"]),
        Elevation=float(first_line_params["EL"]),
        LocalX=Decimal(second_line_params["N "]),
        LocalY=Decimal(second_line_params["E "]),
        LocalZ=Decimal(second_line_params["EL"]),
        HRMS=hrms,
        VRMS=vrms,
        Fixed=is_fixed,
        Note=first_line_params["--"],
        RW5RecordType="GPS",
        RodHeight=machine_state["HR"],
        InstrumentHeight=machine_state["HI"],
    )
