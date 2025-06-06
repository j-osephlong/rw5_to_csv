"""Parsing of DMS (degrees, minutes, seconds) data."""

from __future__ import annotations

from typing import overload


@overload
def dms_to_dd(dms: tuple[float, float, float]) -> float: ...

@overload
def dms_to_dd(dms: str) -> float: ...


def dms_to_dd(dms: tuple[float, float, float] | str) -> float:
    """Degrees minutes seconds to decimal degrees."""
    if isinstance(dms, str):
        d, ms = dms.split(".", maxsplit=1)
        d = float(d)
        m = float(ms[:2])
        s = float(ms[2:].ljust(4, "0")) / 100
        return dms_to_dd((d, m, s))
    return dms[0] + dms[1] / 60 + dms[2] / 3600
