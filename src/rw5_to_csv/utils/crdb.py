import sqlite3
from decimal import Decimal
from pathlib import Path

from rw5_to_csv.records.record import RW5Row


def get_crdb_point(point_id: str, crdb_path: Path) -> RW5Row:
    """Retieves a shot from the crdb file by point id.

    Returns an RW5 row based off of db record.

    Raises ValueError if no row found.
    """  # noqa: DOC201, DOC501
    crdb_connection = sqlite3.connect(crdb_path)
    crdb_connection.row_factory = sqlite3.Row
    cursor = crdb_connection.cursor()
    crdb_query = cursor.execute("SELECT * FROM Coordinates WHERE P like ?", (point_id,))
    crdb_row: sqlite3.Row = crdb_query.fetchone()

    # skip if no crdbrow
    if not crdb_row or crdb_row["E"] is None or crdb_row["N"] is None:
        msg = f"CRDB has no shot with point id {point_id}."
        raise ValueError(msg)

    return RW5Row(
        PointID=point_id,
        RW5RecordType="",
        Note=crdb_row["D"],
        LocalX=Decimal(crdb_row["E"]),
        LocalY=Decimal(crdb_row["N"]),
        LocalZ=Decimal(crdb_row["Z"]),
    )
