import argparse
import logging
import pprint
from pathlib import Path

from rw5_to_csv import convert, prelude
from rw5_to_csv.plot import plot_total_station_data
from rw5_to_csv.total_station import get_total_station_stations

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RW5 files to CSV files.")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--crdb", required=False)
    parser.add_argument("--prelude", action="store_true")
    parser.add_argument("--backsights", action="store_true")
    parser.add_argument("--tsstations", action="store_true")
    parser.add_argument("--tsplot", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input)
    input_crdb_path = None
    if args.crdb:
        input_crdb_path = Path(args.crdb)
    output_path = Path(args.output) if args.output else None
    if args.prelude:
        p = prelude(input_path)
        logger.info(pprint.pformat(p))
    else:
        machine = convert(input_path, output_path if not args.tsplot else None, crdb_path=input_crdb_path)
        if args.backsights:
            logger.info(pprint.pformat(machine.Backsights))
        if args.tsstations:
            logger.info(pprint.pformat(get_total_station_stations(machine)))
        if args.tsplot and output_path:
            image_bytes = plot_total_station_data(machine)
            output_path.write_bytes(image_bytes.read())
