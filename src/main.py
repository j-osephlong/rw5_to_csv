import argparse
import logging
import pprint
from pathlib import Path

from rw5_to_csv import convert, prelude

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RW5 files to CSV files.")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--crdb", required=False)
    parser.add_argument("--prelude", action="store_true")
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
        machine = convert(input_path, output_path, crdb_path=input_crdb_path)
        if output_path is None:
            logger.info(pprint.pformat(machine))
