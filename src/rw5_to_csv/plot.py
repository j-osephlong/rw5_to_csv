"""Functions regarding the plotting of totalstation data on matplotlib."""

import io
import math

import matplotlib.pyplot as plt  # v 3.3.2

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5Row
from rw5_to_csv.utils.crdb import get_crdb_point

Point2DType = tuple[float, float]
ExtentType = tuple[float, float, float, float]


def get_extent(rows: list[RW5Row]) -> ExtentType:
    minx = math.inf
    miny = math.inf
    maxx = -math.inf
    maxy = -math.inf

    for row in rows:
        if row.LocalX and row.LocalX < minx:
            minx = float(row.LocalX)
        if row.LocalX and row.LocalX > maxx:
            maxx = float(row.LocalX)
        if row.LocalY and row.LocalY < miny:
            miny = float(row.LocalY)
        if row.LocalY and row.LocalY > maxy:
            maxy = float(row.LocalY)

    return (minx, miny, maxx, maxy)


def scale_to_new_dimensions(p: Point2DType, old_extent: ExtentType, new_extent: ExtentType) -> Point2DType:
    old_range_x = old_extent[2] - old_extent[0]
    old_range_y = old_extent[3] - old_extent[1]
    new_range_x = new_extent[2] - new_extent[0]
    new_range_y = new_extent[3] - new_extent[1]

    scale = min(
        new_range_x / old_range_y,
        new_range_y / old_range_y,
    )

    margin_x = new_range_x - old_range_x * scale
    margin_y = new_range_y - old_range_y * scale

    scaled_x = new_extent[0] + ((p[0] - old_extent[0]) * scale) + margin_x / 2
    scaled_y = new_extent[1] + ((p[1] - old_extent[1]) * scale) + margin_y / 2
    return (scaled_x, scaled_y)


def plot_total_station_data(machine: MachineState) -> io.BytesIO:
    """Plot ts data with matplotlib.

    Returns BytesIO object containing png data.
    """  # noqa: DOC201, DOC501
    if not machine.crdb_path:
        msg = "CRDB file is required."
        raise ValueError(msg)
    # setup figure
    extent = get_extent(list(machine.Records.values()))
    new_extent = (0, 0, 10, 10)
    fig, ax = plt.subplots(figsize=new_extent[2:], dpi=128)
    plt.axis("off")
    # create a plot for each OC record,
    # assumeing that OC records are a good tell for when a nmew system has
    #   been started.
    oc_records = [r for r in machine.Records.values() if r.RW5RecordType == "OC"]

    for oc_record in oc_records:
        assert oc_record.LocalX is not None
        assert oc_record.LocalY is not None
        # find all backsights
        backsights = [b for b in machine.Backsights if b.OccupiedPointID == oc_record.PointID]
        backsight_points = [get_crdb_point(b.BacksightPointID, machine.crdb_path) for b in backsights]
        # find all side shots
        sideshot_ids = [ss for ss, oc in machine.SideshotIDOccupiedPointID.items() if oc == oc_record.PointID]
        sideshots = [machine.Records[id] for id in sideshot_ids if id in machine.Records]

        #  add backsights
        print(f"{backsight_points=}")
        for b in backsight_points:
            if not b.LocalX or not b.LocalY:
                continue
            from_scaled = scale_to_new_dimensions((float(oc_record.LocalX), float(oc_record.LocalY)), extent, new_extent)
            to_scaled = scale_to_new_dimensions((float(b.LocalX), float(b.LocalY)), extent, new_extent)
            ax.plot([from_scaled[0], to_scaled[0]], [from_scaled[1], to_scaled[1]], "r", linewidth=4, alpha=0.3)
            # plot bs point
            p = (float(b.LocalX), float(b.LocalY))
            scaled_p = scale_to_new_dimensions(p, extent, new_extent)
            ax.plot(scaled_p[0], scaled_p[1], "r^", alpha=0.7, markersize=22)
            # annotate marker with point id
            ax.text(scaled_p[0] + 0.25, scaled_p[1] - 0.2, b.PointID, ha="left", va="center", color="r", fontsize="xx-large")

        # add sideshot lines
        for ss in sideshots:
            if not ss.LocalX or not ss.LocalY:
                continue
            from_scaled = scale_to_new_dimensions((float(oc_record.LocalX), float(oc_record.LocalY)), extent, new_extent)
            to_scaled = scale_to_new_dimensions((float(ss.LocalX), float(ss.LocalY)), extent, new_extent)
            ax.plot([from_scaled[0], to_scaled[0]], [from_scaled[1], to_scaled[1]], "b", linewidth=4, alpha=0.1)

        # plot oc
        p = (float(oc_record.LocalX), float(oc_record.LocalY))
        scaled_p = scale_to_new_dimensions(p, extent, new_extent)
        ax.plot(scaled_p[0], scaled_p[1], "g^", alpha=0.7, markersize=22)
        # add label for OC
        ax.annotate(oc_record.PointID, (scaled_p[0] + 0.25, scaled_p[1]), ha="left", va="center", fontsize="xx-large", color="g")

        # add sideshot points (on top of everything because they're smaller)
        for ss in sideshots:
            if not ss.LocalX or not ss.LocalY:
                continue
            p = (float(ss.LocalX), float(ss.LocalY))
            scaled_p = scale_to_new_dimensions(p, extent, new_extent)
            ax.plot(scaled_p[0], scaled_p[1], "bo", markersize=10)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    return buffer
