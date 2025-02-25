from __future__ import annotations

import datetime


def get_date_time(command_block: list[str], tzinfo: datetime.tzinfo) -> datetime.datetime | None:
    # e.g. --DT05-17-2024
    date_line_match = [
        line for line in command_block if line.strip().startswith("--DT")
    ]
    # e.g. --TM11:24:29
    time_line_match = [
        line for line in command_block if line.strip().startswith("--TM")
    ]
    if date_line_match and time_line_match:
        fmt = "%m-%d-%Y %H:%M:%S"
        dt_str = date_line_match[0].removeprefix("--DT")
        tm_str = time_line_match[0].removeprefix("--TM")
        dt = datetime.datetime.strptime(f"{dt_str} {tm_str}", fmt)  # noqa: DTZ007
        return dt.replace(tzinfo=tzinfo)
    return None
