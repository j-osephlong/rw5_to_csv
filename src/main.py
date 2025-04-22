import argparse
import logging
import pprint
from pathlib import Path

from rw5_to_csv import convert, prelude

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert RW5 files to CSV files.")
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    parser.add_argument("--prelude", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    if args.prelude:
        p = prelude(input_path)
        logger.info(pprint.pformat(p))
    else:
        convert(input_path, output_path)
