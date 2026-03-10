#!/usr/bin/env python3
"""Parse opshin-uplc benchmark text output into unified CSV."""

import re
import sys

VM_NAME = "opshin"
HEADER = "vm,script,mean_ns,median_ns,min_ns,max_ns,stddev_ns,iterations"

UNIT_TO_NS = {"ns": 1, "us": 1_000, "ms": 1_000_000, "s": 1_000_000_000}

# Format from opshin bench_plutus_use_cases.py:
#   auction_1-1                           500 runs      1.23 ms  +/-   0.05 ms  [  1.10 ms ..   1.50 ms]
LINE_RE = re.compile(
    r"^\s+"
    r"(\S+)\s+"                            # name
    r"(\d+)\s+runs\s+"                     # iterations
    r"([\d.]+)\s+(ns|us|ms|s\s)\s+"        # mean + unit
    r"\+/-\s+"
    r"([\d.]+)\s+(ns|us|ms|s\s)\s+"        # stddev + unit
    r"\[\s*([\d.]+)\s+(ns|us|ms|s\s)\s+"   # min + unit
    r"\.\.\s+"
    r"([\d.]+)\s+(ns|us|ms|s\s)\s*\]",    # max + unit
)


def to_ns(value: str, unit: str) -> int:
    unit = unit.strip()
    return int(float(value) * UNIT_TO_NS.get(unit, 1))


def parse(log_path: str) -> None:
    print(HEADER)

    with open(log_path) as f:
        for line in f:
            m = LINE_RE.match(line)
            if not m:
                continue

            name = m.group(1)
            iterations = int(m.group(2))
            mean_ns = to_ns(m.group(3), m.group(4))
            stddev_ns = to_ns(m.group(5), m.group(6))
            min_ns = to_ns(m.group(7), m.group(8))
            max_ns = to_ns(m.group(9), m.group(10))

            print(
                f"{VM_NAME},{name},"
                f"{mean_ns},{mean_ns},{min_ns},{max_ns},"
                f"{stddev_ns},{iterations}"
            )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <opshin-raw.log>", file=sys.stderr)
        sys.exit(1)
    parse(sys.argv[1])
