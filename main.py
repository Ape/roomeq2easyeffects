#!/usr/bin/env python3

import argparse
import collections
import json
import pathlib
import re


FILTER_PATTERN = (
    r"Filter\s+\d+: ON\s+PK\s+Fc\s+"
    r"(?P<freq>\d+\.\d+) Hz\s+"
    r"Gain\s+(?P<gain>-?\d+\.\d+) dB\s+Q\s+"
    r"(?P<q>\d+\.\d+)"
)


Filter = collections.namedtuple("Filter", "freq gain q")


def main(args):
    filters = []

    with args.file.open() as file:
        for line in file:
            if match := re.match(FILTER_PATTERN, line):
                values = (float(x) for x in match.groupdict().values())
                filters.append(Filter(*values))

    output = {
        "output": {
            "blocklist": [],
            "equalizer": {
                "input-gain": args.gain,
                "mode": "IIR",
                "num-bands": len(filters),
                "output-gain": 0.0,
                "split-channels": False,
                "left": {},
                "right": {},
            },
            "plugins_order": [
                "equalizer",
            ],
        }
    }

    for i, item in enumerate(filters):
        band = {
            "frequency": item.freq,
            "gain": item.gain,
            "q": item.q,
            "mode": "RLC (BT)",
            "type": "Bell",
            "slope": "x1",
            "mute": False,
            "solo": False,
        }

        for channel in ["left", "right"]:
            output["output"]["equalizer"][channel][f"band{i}"] = band

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Room EQ Wizard filter file to EasyEffects preset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("file", type=pathlib.Path,
                        help="Room EQ filter file path")
    parser.add_argument("--gain", type=float, default=-2.0,
                        help="input gain for headroom")

    args = parser.parse_args()

    main(args)
