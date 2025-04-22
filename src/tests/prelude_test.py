"""Tests for parsing the prelude of a RW5."""

from pathlib import Path
from tempfile import TemporaryDirectory

from rw5_to_csv.rw5_csv import prelude


def test_parse_prelude():
    prelude_lines = r"""JB,NM24116BLC240611,DT06-11-2024,TM14:22:14
    MO,AD0,UN1,SF1.00000000,EC0,EO0.0,AU0
    --SurvPC Version 6.08
    --CRD: Alphanumeric
    --User Defined: CANADA/NAD83/New Brunswick
    --Equipment: Carlson,  BRx7, SN:D2133624904116, FW:6.0Aa02a,1.18,0.53.210623
    --Antenna Type: [BRX7 Internal],RA0.0785m,SHMP0.0547m,L10.0701m,L20.0629m,--L1/L2/L5 Internal Antenna
    --Localization File: None
    --Geoid Separation File: C:\Carlson Projects\Data\Geoids\Canadian_cgg2013.gsb N10�01'00.0" W169�58'59.0" N89�58'59.0" W010�01'00.0"
    --Grid Adjustment File: None
    --GPS Scale: 1.00000000
    --Scale Point not used
    --RTK Method: RTCM V3.0, Device: Data Collector Internet, Network: NTRIP caneastvrsrtcm"""

    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "tmp.rw5"
        path.write_text(prelude_lines, encoding="utf-8")
        prelude_data = prelude(path)

        assert prelude_data["JobName"] == "24116BLC240611"
        assert prelude_data["Date"] == "06-11-2024"
        assert prelude_data["Time"] == "14:22:14"
        assert prelude_data["ISODateTime"] == "2024-06-11T14:22:14"
        assert (
            prelude_data["Equipment"]
            == "Carlson,  BRx7, SN:D2133624904116, FW:6.0Aa02a,1.18,0.53.210623"
        )
        assert (
            prelude_data["AntennaType"]
            == "[BRX7 Internal],RA0.0785m,SHMP0.0547m,L10.0701m,L20.0629m,--L1/L2/L5 Internal Antenna"
        )
        assert prelude_data["UserDefined"] == "CANADA/NAD83/New Brunswick"


def test_parse_prelude_missing_fields():
    prelude_text = r"""JB,NM24116BLC240611,DT06-11-2024,TM14:22:14
    MO,AD0,UN1,SF1.00000000,EC0,EO0.0,AU0"""

    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "tmp.rw5"
        path.write_text(prelude_text, encoding="utf-8")
        prelude_data = prelude(path)

        assert prelude_data["JobName"] == "24116BLC240611"
        assert prelude_data["Date"] == "06-11-2024"
        assert prelude_data["Time"] == "14:22:14"
        assert prelude_data["ISODateTime"] == "2024-06-11T14:22:14"
        assert not prelude_data["Equipment"]
        assert not prelude_data["AntennaType"]
        assert not prelude_data["UserDefined"]
