from __future__ import annotations

import datetime
from decimal import Decimal
from logging import getLogger

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.common import get_date_time, get_standard_record_params_dict
from rw5_to_csv.records.record import RW5Row

logger = getLogger(__name__)

HRMS_LINE_START = "--HRMS Avg:"
VRMS_LINE_START = "--VRMS Avg:"
NUM_SATELLITES_LINE_START = "--Number of Satellites Avg:"
AGE_LINE_START = "--AGE Avg:"
HDOP_LINE_START = "--HDOP Avg:"
VDOP_LINE_START = "--VDOP Avg:"
PDOP_LINE_START = "--PDOP Avg:"
FIXED_READINGS_LINE_START = "--Fixed Readings:"


def _get_hrms_line_params(command_block: list[str]) -> dict[str, str] | None:
    hrms_line_match = [
        line for line in command_block if line.strip().startswith("--HRMS:")
    ]
    if len(hrms_line_match) > 0:
        # Type A parsing.
        hrms_line = hrms_line_match[0]
        return {
            param.split(":")[0]: param.split(":")[1].strip()
            for param in hrms_line.strip().removeprefix("--").split(", ")
        }
    return None


def _get_hrms(command_block: list[str]) -> float:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
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
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
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


def _get_status(command_block: list[str]) -> str | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return hrms_line_params["STATUS"]
    return None


def _get_number_of_satellites(command_block: list[str]) -> str | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return hrms_line_params["SATS"]

    sats_line_match = [
        line for line in command_block if line.strip().startswith(NUM_SATELLITES_LINE_START)
    ]
    if len(sats_line_match) == 0:
        return None

    sats_line = sats_line_match[0].strip()
    return (
        sats_line[
            len(NUM_SATELLITES_LINE_START) : sats_line.find("Min:", len(NUM_SATELLITES_LINE_START))
        ].strip()
    )


def _get_age_of_corrections(command_block: list[str]) -> str | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return hrms_line_params["AGE"]

    age_line_match = [
        line for line in command_block if line.strip().startswith(AGE_LINE_START)
    ]
    if len(age_line_match) == 0:
        return None

    age_line = age_line_match[0].strip()
    return (
        age_line[
            len(AGE_LINE_START) : age_line.find("Min:", len(AGE_LINE_START))
        ].strip()
    )


def _get_hdop(command_block: list[str]) -> float | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return float(hrms_line_params["HDOP"])

    # Type B parsing.
    logger.info("Type A parsing for HDOP failed, HDOP line not found. Trying Type B.")
    hdop_line_match = [
        line for line in command_block if line.strip().startswith(HDOP_LINE_START)
    ]
    if len(hdop_line_match) == 0:
        logger.info(
            "Type B parsing for HDOP failed, HDOP line not found. Returning None.",
        )
        return None
    """Parse HDOP Avg from line:
        --HDOP Avg: 0.0058 Min: 0.0048 Max: 0.0062
        """
    hdop_line = hdop_line_match[0].strip()
    return float(
        hdop_line[
            len(HDOP_LINE_START) : hdop_line.find("Min:", len(HDOP_LINE_START))
        ].strip(),
    )


def _get_vdop(command_block: list[str]) -> float | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return float(hrms_line_params["VDOP"])

    # Type B parsing.
    logger.info("Type A parsing for VDOP failed, VDOP line not found. Trying Type B.")
    vdop_line_match = [
        line for line in command_block if line.strip().startswith(VDOP_LINE_START)
    ]
    if len(vdop_line_match) == 0:
        logger.info(
            "Type B parsing for VDOP failed, VDOP line not found. Returning None.",
        )
        return None
    """Parse VDOP Avg from line:
        --VDOP Avg: 0.0058 Min: 0.0048 Max: 0.0062
        """
    vdop_line = vdop_line_match[0].strip()
    return float(
        vdop_line[
            len(VDOP_LINE_START) : vdop_line.find("Min:", len(VDOP_LINE_START))
        ].strip(),
    )


def _get_pdop(command_block: list[str]) -> float | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return float(hrms_line_params["PDOP"])

    # Type B parsing.
    logger.info("Type A parsing for PDOP failed, PDOP line not found. Trying Type B.")
    pdop_line_match = [
        line for line in command_block if line.strip().startswith(PDOP_LINE_START)
    ]
    if len(pdop_line_match) == 0:
        logger.info(
            "Type B parsing for PDOP failed, PDOP line not found. Returning None.",
        )
        return None
    """Parse PDOP Avg from line:
        --PDOP Avg: 0.0058 Min: 0.0048 Max: 0.0062
        """
    pdop_line = pdop_line_match[0].strip()
    return float(
        pdop_line[
            len(PDOP_LINE_START) : pdop_line.find("Min:", len(PDOP_LINE_START))
        ].strip(),
    )


def _get_tdop(command_block: list[str]) -> float | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return float(hrms_line_params["TDOP"])
    return None


def _get_gdop(command_block: list[str]) -> float | None:
    hrms_line_params = _get_hrms_line_params(command_block)
    if hrms_line_params:
        # Type A parsing.
        return float(hrms_line_params["GDOP"])
    return None


def parse_gps_record(
    command_block: list[str],
    machine_state: MachineState,
) -> list[RW5Row]:
    logger.debug(command_block)

    first_line_params = get_standard_record_params_dict(command_block[0].strip())
    second_line_params = get_standard_record_params_dict(command_block[1].strip())

    # get hrms, vrms, and fixed status
    try:
        hrms = _get_hrms(command_block)
        vrms = _get_vrms(command_block)
        status = _get_status(command_block)
        hdop = _get_hdop(command_block)
        vdop = _get_vdop(command_block)
        pdop = _get_pdop(command_block)
        tdop = _get_tdop(command_block)
        gdop = _get_gdop(command_block)
        num_sats = _get_number_of_satellites(command_block)
        age = _get_age_of_corrections(command_block)
        dt = get_date_time(command_block, machine_state.tzinfo or datetime.UTC)
    except ValueError:
        logger.exception("Skipping record.")
        return []

    return [RW5Row(
        PointID=first_line_params["PN"],
        Lat=float(first_line_params["LA"]),
        Lng=float(first_line_params["LN"]),
        Elevation=float(first_line_params["EL"]),
        LocalX=Decimal(second_line_params["E "]),
        LocalY=Decimal(second_line_params["N "]),
        LocalZ=Decimal(second_line_params["EL"]),
        HRMS=hrms,
        VRMS=vrms,
        HDOP=hdop,
        VDOP=vdop,
        PDOP=pdop,
        TDOP=tdop,
        GDOP=gdop,
        Status=status,
        NumSatellites=num_sats,
        Age=age,
        Note=first_line_params["--"],
        RW5RecordType="GPS",
        DateTime=dt,
    )]
