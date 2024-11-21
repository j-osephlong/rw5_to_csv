from decimal import Decimal

import pytest

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.gps import parse_gps_record
from rw5_to_csv.records.ls import parse_ls_record
from rw5_to_csv.records.record import RW5CSVRow
from rw5_to_csv.records.ss import parse_ss_record
from rw5_to_csv.rw5_csv import parse_command


@pytest.fixture
def default_machine_state():
    return MachineState(
        {
            "HI": None,
            "MeasuredHR": None,
            "EnteredHR": None,
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


GPS_RECORDS: list[tuple[str, RW5CSVRow]] = [
    (
        """GPS,PN5159,LA45.231320882856,LN-66.041962160406,EL-1.648605,--TS
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
        """.splitlines(),
        {
            "PointID": "5159",
            "Lat": 45.231320882856,
            "Lng": -66.041962160406,
            "Elevation": -1.648605,
            "Note": "TS",
            "LocalX": Decimal("7376385.4778"),
            "LocalY": Decimal("2533509.9182"),
            "LocalZ": Decimal("18.1924"),
            "HRMS": 0.011,
            "VRMS": 0.022,
            "HDOP": 0.560,
            "VDOP": 0.767,
            "PDOP": 0.950,
            "Fixed": True,
            "RW5RecordType": "GPS",
            "InstrumentHeight": None,
            "MeasuredRodHeight": None,
            "EnteredRodHeight": None,
        },
    ),
    (
        """GPS,PN5132,LA45.230660296233,LN-65.490008603929,EL80.214503,--UP/NEW
        --GS,PN5132,N 7376321.4786,E 2553513.3414,EL-7.9573,--UP/NEW
        --GT,PN5132,SW2334,ST134156400,EW2334,ET134159400
        --Valid Readings: XY: 3 Z: 3
        --Nor Min: 7376321.4691  Max: 7376321.4848
        --Eas Min: 2553513.3363  Max: 2553513.3487
        --Elv Min: -7.9769  Max: -7.9190
        --Nor Avg: 7376321.4786  SD: 0.0068
        --Eas Avg: 2553513.3414  SD: 0.0053
        --Elv Avg: -7.9573  SD: 0.0271
        --HRMS Avg: 0.0120 SD: 0.0023 Min: 0.0087 Max: 0.0136
        --VRMS Avg: 0.0144 SD: 0.0022 Min: 0.0113 Max: 0.0160
        --HDOP Avg: 0.5398  Min: 0.5390 Max: 0.5412
        --VDOP Avg: 0.7168 Min: 0.7157 Max: 0.7190
        --PDOP Avg: 0.8973 Min: 0.8960 Max: 0.8999
        --AGE Avg: 1.0000 Min: 1.0000 Max: 1.0000
        --Number of Satellites Avg: 22 Min: 22 Max: 23
        --Pole Incline Min: 16.2485 Max: 17.0817 Average: 16.7516
        --Incline adjustments disabled
        --HRMS:0.014, VRMS:0.016, STATUS:FIXED+, SATS:23, AGE:1.0, PDOP:0.900, HDOP:0.541, VDOP:0.719, TDOP:0.469, GDOP:1.015
        --DT09-30-2024
        --TM10:15:48
        """.splitlines(),
        {
            "PointID": "5132",
            "Lat": 45.230660296233,
            "Lng": -65.490008603929,
            "Elevation": 80.214503,
            "Note": "UP/NEW",
            "LocalX": Decimal("7376321.4786"),
            "LocalY": Decimal("2553513.3414"),
            "LocalZ": Decimal("-7.9573"),
            "HRMS": 0.014,
            "VRMS": 0.016,
            "HDOP": 0.541,
            "VDOP": 0.719,
            "PDOP": 0.900,
            "Fixed": True,
            "RW5RecordType": "GPS",
            "InstrumentHeight": None,
            "MeasuredRodHeight": None,
            "EnteredRodHeight": None,
        },
    ),
    (
        """GPS,PN5100,LA45.230685893410,LN-65.491220056673,EL88.171642,--MON/1380HPN LOC RTK
        --GS,PN5100,N 7376327.1276,E 2553249.7300,EL0.0065,--MON/1380HPN LOC RTK
        --GT,PN5100,SW2334,ST127922600,EW2334,ET127932600
        --Valid Readings: XY: 10 Z: 10
        --Nor Min: 7376327.1264  Max: 7376327.1292
        --Eas Min: 2553249.7287  Max: 2553249.7321
        --Elv Min: 0.0030  Max: 0.0107
        --Nor Avg: 7376327.1276  SD: 0.0009
        --Eas Avg: 2553249.7300  SD: 0.0010
        --Elv Avg: 0.0065  SD: 0.0024
        --HRMS Avg: 0.0057 SD: 0.0004 Min: 0.0050 Max: 0.0062
        --VRMS Avg: 0.0092 SD: 0.0006 Min: 0.0083 Max: 0.0099
        --HDOP Avg: 0.5302  Min: 0.5302 Max: 0.5302
        --VDOP Avg: 0.6754 Min: 0.6754 Max: 0.6755
        --PDOP Avg: 0.8586 Min: 0.8586 Max: 0.8587
        --AGE Avg: 1.3000 Min: 1.0000 Max: 2.0000
        --Number of Satellites Avg: 29 Min: 29 Max: 29
        --Pole Incline Min: 0.3659 Max: 0.4026 Average: 0.3830
        --Incline adjustments disabled
        --DT09-30-2024
        --TM08:32:05
        """.splitlines(),
        {
            "PointID": "5100",
            "Lat": 45.230685893410,
            "Lng": -65.491220056673,
            "Elevation": 88.171642,
            "Note": "MON/1380HPN LOC RTK",
            "LocalX": Decimal("7376327.1276"),
            "LocalY": Decimal("2553249.7300"),
            "LocalZ": Decimal("0.0065"),
            "HRMS": 0.0057,
            "VRMS": 0.0092,
            "HDOP": 0.5302,
            "VDOP": 0.6754,
            "PDOP": 0.8586,
            "Fixed": None,
            "RW5RecordType": "GPS",
            "InstrumentHeight": None,
            "MeasuredRodHeight": None,
            "EnteredRodHeight": None,
        },
    ),
]

RECORDS_WITH_ROVER_HEIGHT_COMMAND = [
    (
        """BP,PN3488_BASE_1,LA45.160537361211,LN-66.025824934287,EL-0.7430,AG1.5000,PA0.1319,ATAPC,SRROVER,--
    --Entered Rover HR: 2.0000 m, Vertical""".splitlines(),
        2.0,
    ),
    (
        """SS,OP6001,FP5310,AR159.3803,ZE90.3544,SD127.242488,--CP/6000
    --DT07-21-2021
    --TM12:08:28
    --Equipment:   Hemisphere GNSS,  S321, SN:D1726-02310-01-068, FW:5.6Aa09,4.10,1.30.170620
    --GPS Scale: 1.00000000
    --Scale Point not used
    --Entered Rover HR: 2.0000 m, Vertical""".splitlines(),
        2.0,
    ),
    (
        """LS,HR1.9201
    --Entered Rover HR: 2.0000 m, Vertical""".splitlines(),
        2.0,
    ),
    (
        """GPS,PN5149,LA45.230275729975,LN-65.484613177769,EL84.043167,--SMFD/228 19?? BENT
    --GS,PN5149,N 7376205.3661,E 2553817.9310,EL-4.1350,--SMFD/228 19?? BENT
    G0,2024/09/30 13:58:07,(Average) - Base ID read at rover: 0
    G1,BP0,PN5149,DX233.30107,DY39.76847,DZ-59.92493
    G2,VX0.00001576,VY0.00005938,VZ0.00005581
    G3,XY-0.00001254,XZ0.00000538,YZ-0.00003406
    --HRMS Avg: 0.0063 SD: 0.0001 Min: 0.0061 Max: 0.0063
    --VRMS Avg: 0.0096 SD: 0.0001 Min: 0.0094 Max: 0.0097
    --HDOP Avg: 0.6804  Min: 0.6804 Max: 0.6804
    --VDOP Avg: 0.9354 Min: 0.9353 Max: 0.9354
    --PDOP Avg: 1.1566 Min: 1.1566 Max: 1.1566
    --AGE Avg: 1.0000 Min: 1.0000 Max: 1.0000
    --RTK Method: Auto, Device: Internal Radio
    --Entered Rover HR: 2.0000 m, Vertical""".splitlines(),
        2.0,
    ),
]
"""Record, expected entered HR value."""


@pytest.mark.parametrize(
    "command,expected_entered_hr",
    RECORDS_WITH_ROVER_HEIGHT_COMMAND,
)
def test_handle_rover_height_command(
    command,
    expected_entered_hr,
    default_machine_state: MachineState,
):
    """Ensure that all commands that have Entered Rover HR command are handled, and machine state is set."""
    print(default_machine_state)
    parse_command([l.strip() for l in command], default_machine_state)
    print(default_machine_state)
    assert default_machine_state["EnteredHR"] == expected_entered_hr


@pytest.fixture
def ss_record():
    return """SS,OPTEMP1,FP7001,AR210.2811,ZE63.0014,SD23.750400,--BOLT
    --DT09-05-2023
    --TM07:07:32s
    """.splitlines()


@pytest.mark.parametrize("gps_record,expected", GPS_RECORDS)
def test_parse_gps_record(gps_record, expected, default_machine_state: MachineState):
    row: RW5CSVRow = parse_gps_record(gps_record, default_machine_state)

    assert row == expected


def test_parse_gps_record_with_machine_state(
    gps_record,
    default_machine_state: MachineState,
):
    default_machine_state["HI"] = 1
    default_machine_state["MeasuredHR"] = 2

    row: RW5CSVRow = parse_gps_record(gps_record, default_machine_state)

    assert row["InstrumentHeight"] == 1
    assert row["MeasuredRodHeight"] == 2  # noqa: PLR2004


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
    assert default_machine_state["MeasuredHR"] == 1.4700  # noqa: PLR2004


def test_parse_ls_record_with_hr_and_hi(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HI1.5450,HR1.4700".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert ret is None  # No return from this record
    assert default_machine_state["HI"] == 1.5450  # noqa: PLR2004
    assert default_machine_state["MeasuredHR"] == 1.4700  # noqa: PLR2004


def test_parse_ss_record(ss_record, default_machine_state: MachineState):

    row: RW5CSVRow = parse_ss_record(ss_record, default_machine_state)

    assert row["PointID"] == "7001"
    assert row["Note"] == "BOLT"
    assert row["RW5RecordType"] == "SS"
    assert row["InstrumentHeight"] is None
    assert row["MeasuredRodHeight"] is None
