#!/usr/bin/env python
import argparse
from utility import alphas_to_pin_nums
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="convert from plain text to canute native format")

parser.add_argument('--in', action='store', dest='in_file',
                    help="text file to convert", required=True)
parser.add_argument('--out', action='store', dest='out_file',
                    help="canute file to write", required=True)

args = parser.parse_args()

with open(args.in_file) as fh:
    lines = fh.readlines()

with open(args.out_file, 'w') as fh:
    for line in lines:
        line = line.strip()
        pin_nums = alphas_to_pin_nums(line)
        joined = ','.join([str(x) for x in pin_nums])
        fh.write(joined + "\n")
