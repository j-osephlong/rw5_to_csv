from __future__ import annotations

import datetime


def get_date_time(command_block: list[str], tzinfo: datetime.tzinfo) -> datetime.datetime | None:
    # e.g. --DT05-17-2024
    date_line_match = [
        line.strip() for line in command_block if line.strip().startswith("--DT")
    ]
    # e.g. --TM11:24:29
    time_line_match = [
        line.strip() for line in command_block if line.strip().startswith("--TM")
    ]
    if date_line_match and time_line_match:
        fmt = "%m-%d-%Y %H:%M:%S"
        dt_str = date_line_match[0].removeprefix("--DT")
        tm_str = time_line_match[0].removeprefix("--TM")
        dt = datetime.datetime.strptime(f"{dt_str} {tm_str}", fmt)  # noqa: DTZ007
        return dt.replace(tzinfo=tzinfo)
    return None


def get_standard_record_params_dict(record: str) -> dict[str, str]:
    """Return dict of params from record.

    Standard record:
    GPS,PN5050,LA45.502033173001,LN-66.064406766459,EL-13.312712,--SMFD/DMSE 2024
    Comma seperated params, with 2 char prefix as name of record.
    In the above record, PN is a param and its value is 5050
    """  # noqa: DOC201
    return {param[:2]: param[2:].strip() for param in record.split(",")}


def get_prism_applied(command_block: list[str]) -> str | None:
    """Checks record for a prism changed notice, and returns the label if one exists."""  # noqa: D401, DOC201
    prism = None
    for line in command_block:
        if not line.startswith("--P.C. mm Applied:"):
            continue
        prism = line.split("(", maxsplit=1)[-1].split(":", maxsplit=1)[0]
    return prism
