from __future__ import annotations

from pathlib import Path

import pytest

from rw5_to_csv.convert import convert, group_lines_into_command_blocks

test_rw5_files__convert: list[dict] = [
    {
        "rw5": Path("./src/tests/data/ss.test.rw5"),
        "crdb": Path("./src/tests/data/ss.test.crdb"),
        "num_overwritten": 1,
        "num_gps_records": 10,
        "num_bp_records": 1,
        "num_ss_records": 3,
        "num_oc_records": 1,
        "num_command_blocks": 23,
        "num_backsights": 1,
    },
    {
        "rw5": Path("./src/tests/data/gps-short-stats.test.rw5"),
        "crdb": None,
        "num_overwritten": 0,
        "num_gps_records": 24,
        "num_bp_records": 1,
        "num_ss_records": 0,
        "num_oc_records": 0,
        "num_command_blocks": 28,
        "num_backsights": 0,
    },
    {
        "rw5": Path("./src/tests/data/gps-long-stats_overwritten-shots.test.rw5"),
        "crdb": None,
        "num_overwritten": 4,
        "num_gps_records": 27,
        "num_bp_records": 1,
        "num_ss_records": 0,
        "num_oc_records": 0,
        "num_command_blocks": 42,
        "num_backsights": 0,
    },
    {
        "rw5": Path("./src/tests/data/gps-multiple-bp.test.rw5"),
        "crdb": None,
        "num_overwritten": 0,
        "num_gps_records": 11,
        "num_bp_records": 2,
        "num_ss_records": 0,
        "num_oc_records": 0,
        "num_command_blocks": 18,
        "num_backsights": 0,
    },
]
"""Path, GPS record count, SS record count, BP record count."""


@pytest.mark.parametrize(
    "data",
    test_rw5_files__convert,
)
def test_convert(
    data: dict,
) -> None:
    """Test that each file produces the expected number of rows per record type."""
    machine = convert(data["rw5"], None, crdb_path=data["crdb"])

    csv_gps_records = [row for row in machine.Records.values() if row.RW5RecordType == "GPS"]
    csv_bp_records = [row for row in machine.Records.values() if row.RW5RecordType == "BP"]
    csv_ss_records = [row for row in machine.Records.values() if row.RW5RecordType == "SS"]
    csv_oc_records = [row for row in machine.Records.values() if row.RW5RecordType == "OC"]
    csv_overwritten_records = [row for row in machine.Records.values() if row.Overwritten]

    assert len(csv_gps_records) == data["num_gps_records"]
    assert len(csv_bp_records) == data["num_bp_records"]
    assert len(csv_ss_records) == data["num_ss_records"]
    assert len(csv_oc_records) == data["num_oc_records"]
    assert len(csv_overwritten_records) == data["num_overwritten"]
    assert len(machine.Backsights) == data["num_backsights"]

    lines = data["rw5"].read_text().splitlines()

    command_blocks = group_lines_into_command_blocks(lines)
    assert len(command_blocks) == data["num_command_blocks"]
