from dataclasses import dataclass
from typing import Self

from rw5_to_csv.machine_state import BacksightRow, MachineState
from rw5_to_csv.records.record import RW5Row


@dataclass
class TSStation:
    """Dataclass describing a totalstation system."""

    OccupiedPoint: RW5Row
    BacksightPoint: RW5Row
    Backsight: BacksightRow
    ForesightPoints: list[RW5Row]

    @classmethod
    def build(cls, machine_state: MachineState, occupied_point_id: str) -> Self:
        """Build an object given a machine and oc point id."""  # noqa: DOC201, DOC501
        occupied_point = machine_state.Records[occupied_point_id]

        side_shots = [
            machine_state.Records[side_shot_id]
            for side_shot_id, _occupied_point_id
            in machine_state.SideshotIDOccupiedPointID.items() if _occupied_point_id == occupied_point_id
        ]

        backsight = next((i for i in machine_state.Backsights if i.OccupiedPointID == occupied_point_id), None)
        if backsight is None:
            msg = f"Missing backsight for occupied point {occupied_point_id}."
            raise ValueError(msg)
        backsight_point = machine_state.Records[backsight.BacksightPointID]

        return cls(
            OccupiedPoint=occupied_point,
            ForesightPoints=side_shots,
            Backsight=backsight,
            BacksightPoint=backsight_point,
        )


def get_total_station_stations(machine_state: MachineState) -> list[TSStation]:
    """Return list of TSStation objects, each describing a total station station."""  # noqa: DOC201
    # get all occupied point records as they each are the core of a system.
    oc_records = [record for record in machine_state.Records.values() if record.RW5RecordType == "OC"]
    return [TSStation.build(machine_state, oc.PointID) for oc in oc_records]
