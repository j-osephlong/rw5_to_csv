"""Functions regarding the plotting of totalstation data on matplotlib."""

import math

import matplotlib.pyplot as plt  # v 3.3.2

from rw5_to_csv.machine_state import MachineState
from rw5_to_csv.records.record import RW5Row

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


def plot_ts_data(machine: MachineState):
    # setup figure
    extent = get_extent(list(machine.Records.values()))
    new_extent = (0, 0, 4, 4)
    fig, ax = plt.subplots(figsize=new_extent[2:], dpi=512)
    plt.axis("off")
    # create a plot for each OC record,
    # assumeing that OC records are a good tell for when a nmew system has
    #   been started.
    oc_records = [r for r in machine.Records.values() if r.RW5RecordType == "OC"]

    for oc_record in oc_records:
        assert oc_record.LocalX
        assert oc_record.LocalY
        # find all backsights
        backsights = [b for b in machine.Backsights if b.FromPointID == oc_record.PointID]
        backsight_points = [machine.Records[b.ToPointID] for b in backsights if b.ToPointID in machine.Records]
        # find all side shots
        sideshot_ids = [ss for ss, oc in machine.SideshotIDOccupiedPointID.items() if oc == oc_record.PointID]
        sideshots = [machine.Records[id] for id in sideshot_ids if id in machine.Records]

        #  add backsights
        for b in backsight_points:
            if not b.LocalX or not b.LocalY:
                continue
            from_scaled = scale_to_new_dimensions((float(oc_record.LocalX), float(oc_record.LocalY)), extent, new_extent)
            to_scaled = scale_to_new_dimensions((float(b.LocalX), float(b.LocalY)), extent, new_extent)
            ax.plot([from_scaled[0], to_scaled[0]], [from_scaled[1], to_scaled[1]], "r", linewidth=1, alpha=0.3)
            # plot bs point
            p = (float(b.LocalX), float(b.LocalY))
            scaled_p = scale_to_new_dimensions(p, extent, new_extent)
            ax.plot(scaled_p[0], scaled_p[1], "r^")
            # annotate marker with point id
            ax.text(scaled_p[0] + 0.15, scaled_p[1], b.PointID, ha="left", va="center", fontsize="xx-small", color="r")

        # add sideshot lines
        for ss in sideshots:
            if not ss.LocalX or not ss.LocalY:
                continue
            from_scaled = scale_to_new_dimensions((float(oc_record.LocalX), float(oc_record.LocalY)), extent, new_extent)
            to_scaled = scale_to_new_dimensions((float(ss.LocalX), float(ss.LocalY)), extent, new_extent)
            ax.plot([from_scaled[0], to_scaled[0]], [from_scaled[1], to_scaled[1]], "b", linewidth=1, alpha=0.1)
            p = (float(ss.LocalX), float(ss.LocalY))
            scaled_p = scale_to_new_dimensions(p, extent, new_extent)
            ax.plot(scaled_p[0], scaled_p[1], "bo", markersize=2)

        # plot oc
        p = (float(oc_record.LocalX), float(oc_record.LocalY))
        scaled_p = scale_to_new_dimensions(p, extent, new_extent)
        ax.plot(scaled_p[0], scaled_p[1], "g^")
        # add label for OC
        ax.text(scaled_p[0] + 0.15, scaled_p[1], oc_record.PointID, ha="left", va="center", fontsize="xx-small", color="g")

    fig.savefig("fig.png", bbox_inches="tight")
