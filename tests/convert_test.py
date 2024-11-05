from __future__ import annotations

from pathlib import Path

import pytest

from records.record import RW5CSVRow
from rw5_csv import convert, group_lines_into_command_blocks

test_rw5_files__convert: list[tuple[Path, int, int]] = [
    (Path("./tests/data/test.1.rw5"), 70, 0),
    (Path("./tests/data/test.2.rw5"), 4, 0),
    (Path("./tests/data/test.3.rw5"), 0, 161),
    (Path("./tests/data/test.4.rw5"), 25, 413),
    (Path("./tests/data/test.5.rw5"), 108, 73),
]
"""Path, GPS record count, SS record count."""


@pytest.mark.parametrize(
    "rw5_file_path,gps_record_count,ss_record_count",
    test_rw5_files__convert,
)
def test_convert(
    rw5_file_path: Path,
    gps_record_count: int,
    ss_record_count: int,
) -> None:
    """Test that each file produces the expected number of rows per record type."""
    csv_rows: list[RW5CSVRow] = convert(rw5_file_path, None)

    csv_gps_records = [row for row in csv_rows if row["RW5RecordType"] == "GPS"]
    csv_ss_records = [row for row in csv_rows if row["RW5RecordType"] == "SS"]

    assert len(csv_gps_records) == gps_record_count
    assert len(csv_ss_records) == ss_record_count


test_rw5_files__command_blocks: list[tuple[Path, int, int]] = [
    (Path("./tests/data/test.1.rw5"), 78, 1420),
    (Path("./tests/data/test.2.rw5"), 9, 145),
    (Path("./tests/data/test.3.rw5"), 187, 568),
    (Path("./tests/data/test.4.rw5"), 518, 1967),
    (Path("./tests/data/test.5.rw5"), 228, 2649),
]
"""Path, expected_num_records, expected_num_lines."""


@pytest.mark.parametrize(
    "rw5_file_path,expected_num_records,expected_num_lines",
    test_rw5_files__command_blocks,
)
def test_group_into_command_blocks(
    rw5_file_path: Path,
    expected_num_records: int,
    expected_num_lines: int,
):
    """Test that each file produces the expected number of command blocks in pre prcoessing."""
    lines = rw5_file_path.read_text().splitlines()

    command_blocks = group_lines_into_command_blocks(lines)
    assert len(command_blocks) == expected_num_records

    lines_in_blocks = sum(len(block) for block in command_blocks)
    assert lines_in_blocks == expected_num_lines
