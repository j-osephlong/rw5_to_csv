from decimal import Decimal

import pytest

from machine_state import MachineState
from records.gps import parse_gps_record
from records.ls import parse_ls_record
from records.record import RW5CSVRow
from records.ss import parse_ss_record


@pytest.fixture
def default_machine_state():
    return MachineState(
        {
            "HI": None,
            "HR": None,
        },
    )


@pytest.fixture
def gps_record():
    return """GPS,PN5159,LA45.231320882856,LN-66.041962160406,EL-1.648605,--TS
    --GS,PN5159,N 7376385.4778,E 2533509.9182,EL18.1924,--TS
    --GT,PN5159,SW2318,ST239822499,EW2318,ET239824500
    --Valid Readings: 3 of 3
    --Fixed Readings: 3 of 3
    --Nor Min: 7376385.4704  Max: 7376385.4852
    --Eas Min: 2533509.9131  Max: 2533509.9242
    --Elv Min: 18.1859  Max: 18.1964
    --Nor Avg: 7376385.4778  SD: 0.0060
    --Eas Avg: 2533509.9182  SD: 0.0046
    --Elv Avg: 18.1924  SD: 0.0046
    --HRMS Avg: 0.0116 SD: 0.0006 Min: 0.0109 Max: 0.0123
    --VRMS Avg: 0.0226 SD: 0.0008 Min: 0.0220 Max: 0.0238
    --HDOP Avg: 0.5661  Min: 0.5596 Max: 0.5793
    --VDOP Avg: 0.7742 Min: 0.7673 Max: 0.7878
    --PDOP Avg: 0.9591 Min: 0.9497 Max: 0.9778
    --AGE Avg: 1.3333 Min: 1.0000 Max: 2.0000
    --Number of Satellites Avg: 25 Min: 23 Max: 27
    --HRMS:0.011, VRMS:0.022, STATUS:FIXED, SATS:27, AGE:1.0, PDOP:0.950, HDOP:0.560, VDOP:0.767, TDOP:0.550, GDOP:1.098
    """.splitlines()


@pytest.fixture
def ss_record():
    return """SS,OPTEMP1,FP7001,AR210.2811,ZE63.0014,SD23.750400,--BOLT
    --DT09-05-2023
    --TM07:07:32s
    """.splitlines()


def test_parse_gps_record(gps_record, default_machine_state: MachineState):

    row: RW5CSVRow = parse_gps_record(gps_record, default_machine_state)

    assert row["PointID"] == "5159"
    assert row["Lat"] == 45.231320882856  # noqa: PLR2004
    assert row["Lng"] == -66.041962160406  # noqa: PLR2004
    assert row["Elevation"] == -1.648605  # noqa: PLR2004
    assert row["Note"] == "TS"
    assert row["LocalX"] == Decimal("7376385.4778")
    assert row["LocalY"] == Decimal("2533509.9182")
    assert row["LocalZ"] == Decimal("18.1924")
    assert row["HRMS"] - 0.0116 < 0.01  # noqa: PLR2004
    assert row["VRMS"] - 0.0226 < 0.01  # noqa: PLR2004
    assert row["Fixed"] is True
    assert row["RW5RecordType"] == "GPS"
    assert row["InstrumentHeight"] is None
    assert row["RodHeight"] is None


def test_parse_gps_record_with_machine_state(
    gps_record,
    default_machine_state: MachineState,
):
    default_machine_state["HI"] = 1
    default_machine_state["HR"] = 2

    row: RW5CSVRow = parse_gps_record(gps_record, default_machine_state)

    assert row["InstrumentHeight"] == 1
    assert row["RodHeight"] == 2  # noqa: PLR2004


def test_parse_ls_record_with_hi(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HI1.5450".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert ret is None  # No return from this record
    assert default_machine_state["HI"] == 1.5450  # noqa: PLR2004


def test_parse_ls_record_with_hr(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HR1.4700".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert ret is None  # No return from this record
    assert default_machine_state["HR"] == 1.4700  # noqa: PLR2004


def test_parse_ls_record_with_hr_and_hi(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HI1.5450,HR1.4700".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert ret is None  # No return from this record
    assert default_machine_state["HI"] == 1.5450  # noqa: PLR2004
    assert default_machine_state["HR"] == 1.4700  # noqa: PLR2004


def test_parse_ss_record(ss_record, default_machine_state: MachineState):

    row: RW5CSVRow = parse_ss_record(ss_record, default_machine_state)

    assert row["PointID"] == "7001"
    assert row["Note"] == "BOLT"
    assert row["RW5RecordType"] == "SS"
    assert row["InstrumentHeight"] is None
    assert row["RodHeight"] is None
