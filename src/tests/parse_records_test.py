from collections.abc import Sequence
from decimal import Decimal

import pytest

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.bk import parse_bk_record
from rw5_to_csv.records.bp import parse_bp_record
from rw5_to_csv.records.gps import parse_gps_record
from rw5_to_csv.records.ls import parse_ls_record
from rw5_to_csv.records.oc import parse_oc_record
from rw5_to_csv.records.record import RW5Row
from rw5_to_csv.records.ss import parse_ss_record
from rw5_to_csv.utils.dms import dms_to_dd


@pytest.fixture
def default_machine_state():
    return MachineState()


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


GPS_RECORDS: list[tuple[Sequence[str], RW5Row]] = [
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
        RW5Row(
            PointID="5159",
            Lat=45.231320882856,
            Lng=-66.041962160406,
            Elevation=-1.648605,
            Note="TS",
            LocalX=Decimal("2533509.9182"),
            LocalY=Decimal("7376385.4778"),
            LocalZ=Decimal("18.1924"),
            Status="FIXED",
            Age="1.0",
            NumSatellites="27",
            HRMS=0.011,
            VRMS=0.022,
            HDOP=0.560,
            VDOP=0.767,
            PDOP=0.950,
            TDOP=0.550,
            GDOP=1.098,
            RW5RecordType="GPS",
        ),
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
        RW5Row(
            PointID="5132",
            Lat=45.230660296233,
            Lng=-65.490008603929,
            Elevation=80.214503,
            Note="UP/NEW",
            LocalX=Decimal("2553513.3414"),
            LocalY=Decimal("7376321.4786"),
            LocalZ=Decimal("-7.9573"),
            HRMS=0.014,
            VRMS=0.016,
            HDOP=0.541,
            VDOP=0.719,
            PDOP=0.900,
            TDOP=0.469,
            GDOP=1.015,
            Status="FIXED+",
            RW5RecordType="GPS",
            Age="1.0",
            NumSatellites="23",
        ),
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
        RW5Row(
            PointID="5100",
            Lat=45.230685893410,
            Lng=-65.491220056673,
            Elevation=88.171642,
            Note="MON/1380HPN LOC RTK",
            LocalX=Decimal("2553249.7300"),
            LocalY=Decimal("7376327.1276"),
            LocalZ=Decimal("0.0065"),
            HRMS=0.0057,
            VRMS=0.0092,
            HDOP=0.5302,
            VDOP=0.6754,
            PDOP=0.8586,
            Age="1.3000",
            NumSatellites="29",
            RW5RecordType="GPS",
        ),
    ),
]


@pytest.fixture
def ss_record():
    return """SS,OPTEMP1,FP7001,AR210.2811,ZE63.0014,SD23.750400,--BOLT
    --DT09-05-2023
    --TM07:07:32
    """.splitlines()


@pytest.mark.parametrize("gps_record,expected", GPS_RECORDS)
def test_parse_gps_record(gps_record, expected, default_machine_state: MachineState):
    row = parse_gps_record(gps_record, default_machine_state)
    print(gps_record)

    assert row == expected


def test_parse_ls_record_with_hi(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HI1.5450,HR2.0".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert default_machine_state.HI == 1.5450  # noqa: PLR2004


def test_parse_ls_record_with_hr(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    # HR type LS records always come after a command with an "--entered rover HR" comment line in it.
    default_machine_state.ProcessedCommandBlocks = [
        [
            "--Entered Rover HR: 2.0000 m, Vertical",
        ],
    ]
    record = "LS,HR1.4700".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert default_machine_state.HR == 2.0  # noqa: PLR2004


def test_parse_ls_record_with_hr_and_hi(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = "LS,HI1.5450,HR1.4700".splitlines()

    ret = parse_ls_record(record, default_machine_state)

    assert ret == []  # No return from this record
    assert default_machine_state.HI == 1.5450  # noqa: PLR2004
    assert default_machine_state.HR == 1.4700  # noqa: PLR2004


def test_parse_bp_record(default_machine_state: MachineState):
    """Test that the LS record changes the machine state."""
    record = """BP,PN2291_BASE_1,LA45.433488970572,LN-65.291159761295,EL7.3050,AG1.8500,PA0.0701,ATAPC,SRROVER,--
    --Entered Rover HR: 1.9900 m, Vertical
    """.splitlines()

    ret = parse_bp_record(record, default_machine_state)

    assert ret
    assert ret[0].RW5RecordType == "BP"
    assert ret[0].PointID == "2291_BASE_1"
    assert ret[0].Lat
    assert ret[0].Lng
    assert ret[0].Elevation
    assert abs(ret[0].Lat - 45.433488970572) < 0.0001
    assert abs(ret[0].Lng - -65.291159761295) < 0.0001
    assert abs(ret[0].Elevation - 7.3050) < 0.0001


def test_parse_ts_data(default_machine_state: MachineState):
    # parse OC
    ls_record = ["LS,HI1.6260,HR0.0000"]
    oc_record = ["OC,OP6006,N 7363380.72737,E 2534856.89371,EL24.738,--CP/MAG"]
    bk_record = ["BK,OP6006,BP6002,BS340.0906,BC261.3020"]
    ss_record = """SS,OP6006,FP5313,AR334.0406,ZE86.1931,SD57.888877,--BLDS
    --DT07-21-2021
    --TM13:26:13""".splitlines()

    ls_row = parse_ls_record(ls_record, default_machine_state)
    assert ls_row == []
    assert default_machine_state.HI and default_machine_state.HI - 1.6260 < 0.0001
    assert default_machine_state.HR == 0

    oc_row = parse_oc_record(oc_record, default_machine_state)
    assert oc_row
    assert oc_row[0].RW5RecordType == "OC"
    assert oc_row[0].PointID == "6006"
    assert oc_row[0].LocalX == Decimal("2534856.89371")
    assert oc_row[0].LocalY == Decimal("7363380.72737")
    assert oc_row[0].LocalZ == Decimal("24.738")
    assert oc_row[0].Note == "CP/MAG"

    # add row to machine state to make ss record work
    default_machine_state.Records["6006"] = oc_row[0]

    assert default_machine_state.OccupiedPointID == "6006"

    bk_row = parse_bk_record(bk_record, default_machine_state)
    assert len(bk_row) == 0  # bk doesn't add a point record
    assert len(default_machine_state.Backsights) > 0
    assert default_machine_state.Backsights[-1].BacksightAngleDD == dms_to_dd("340.0906")
    assert default_machine_state.Backsights[-1].FromPointID == "6006"
    assert default_machine_state.Backsights[-1].ToPointID == "6002"

    ss_row = parse_ss_record(ss_record, default_machine_state)
    assert ss_row
    assert ss_row[0].PointID == "5313"
    assert ss_row[0].RW5RecordType == "SS"
    assert ss_row[0].Note == "BLDS"
    assert default_machine_state.SideshotIDOccupiedPointID["5313"] == "6006"
