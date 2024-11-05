from __future__ import annotations

from decimal import Decimal
from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5CSVRow, get_standard_record_params_dict

logger = getLogger(__file__)

HRMS_LINE_START = "--HRMS Avg:"
VRMS_LINE_START = "--VRMS Avg:"
FIXED_READINGS_LINE_START = "--Fixed Readings:"


def parse_gps_record(
    command_block: list[str],
    machine_state: MachineState,
) -> RW5CSVRow:
    logger.debug(command_block)

    first_line_params = get_standard_record_params_dict(command_block[0].strip())
    second_line_params = get_standard_record_params_dict(command_block[1].strip())

    # get hrms, vrms, and fixed status
    try:
        """Type A of the GPS record has the following comment-record:
        ` rw5
        --HRMS:0.006, VRMS:0.009, STATUS:FIXED, SATS:15, AGE:2.0, PDOP:0.880, HDOP:0.485, VDOP:0.734, TDOP:0.472, GDOP:0.999
        `
        """  # noqa: E501
        hrms_line_match = [
            line for line in command_block if line.strip().startswith("--HRMS:")
        ]
        if len(hrms_line_match) == 0:
            msg = "HRMS line not found."
            raise ValueError(msg)
        hrms_line = hrms_line_match[0]

        hrms_line_params = {
            param.split(":")[0]: param.split(":")[1].strip()
            for param in hrms_line.strip().removeprefix("--").split(", ")
        }

        # we never get this from type A record, set to None
        is_fixed = hrms_line_params["STATUS"] == "FIXED"
        hrms = float(hrms_line_params["HRMS"])
        vrms = float(hrms_line_params["VRMS"])
    except ValueError:
        """Type B does not but has individual records:
        `
        --Fixed Readings: 10 of 10
        --HRMS Avg: 0.0058 SD: 0.0004 Min: 0.0048 Max: 0.0062
        --VRMS Avg: 0.0086 SD: 0.0006 Min: 0.0071 Max: 0.0092
        `
        """
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
        hrms = float(
            hrms_line[
                len(HRMS_LINE_START) : hrms_line.find("SD:", len(HRMS_LINE_START))
            ].strip(),
        )

        """Parse VRMS Avg from line:
        --VRMS Avg: 0.0058 SD: 0.0004 Min: 0.0048 Max: 0.0062
        """
        vrms_line_match = [
            line for line in command_block if line.strip().startswith(VRMS_LINE_START)
        ]
        if len(vrms_line_match) == 0:
            msg = "HRMS line not found."
            raise ValueError(msg)
        vrms_line = vrms_line_match[0].strip()
        vrms = float(
            vrms_line[
                len(VRMS_LINE_START) : vrms_line.find("SD:", len(VRMS_LINE_START))
            ].strip(),
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
            msg = "HRMS line not found."
            raise ValueError(msg)
        fixed_readings_line = fixed_line_match[0].strip()
        fixed_readings = fixed_readings_line.removeprefix(
            FIXED_READINGS_LINE_START,
        ).strip()

        [fixed_readings_count, readings_count] = fixed_readings.split(" of ")
        is_fixed = fixed_readings_count == readings_count

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
