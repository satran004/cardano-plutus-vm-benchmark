#!/usr/bin/env python3
"""Parse Vitest bench JSON or text output into unified CSV."""

import json
import os
import re
import sys

VM_NAME = "blaze-plutus"
HEADER = "vm,script,mean_ns,median_ns,min_ns,max_ns,stddev_ns,iterations"

# Vitest text output line pattern (fallback)
# name       x ops/sec    +-x% (N runs)    avg: x ms
TEXT_RE = re.compile(
    r"^\s*(\S+)\s+"                     # name
    r"([\d,.]+)\s+ops/sec\s+"           # ops/sec
    r"[±+-]?\s*([\d.]+)%\s+"            # rme%
    r"\((\d+)\s+runs?\)\s+"             # runs
    r"avg:\s*([\d.]+)\s*(ns|us|ms|s)",  # avg time + unit
    re.MULTILINE,
)

UNIT_TO_NS = {"ns": 1, "us": 1_000, "ms": 1_000_000, "s": 1_000_000_000}


def parse_json(json_path: str) -> None:
    """Parse Vitest bench JSON reporter output."""
    print(HEADER)

    with open(json_path) as f:
        data = json.load(f)

    test_results = data.get("testResults", [])
    for suite in test_results:
        for result in suite.get("assertionResults", []):
            bench = result.get("benchmarkResult")
            if not bench:
                continue

            name = result.get("ancestorTitles", [""])[-1] if result.get(
                "ancestorTitles"
            ) else result.get("fullName", "unknown")
            # Use the test title as name (last part)
            name = result.get("title", name)

            # Vitest bench reports mean in seconds
            mean_s = bench.get("mean", 0)
            min_s = bench.get("min", 0)
            max_s = bench.get("max", 0)
            samples = bench.get("samples", 0)

            mean_ns = int(mean_s * 1e9)
            min_ns = int(min_s * 1e9)
            max_ns = int(max_s * 1e9)

            # Compute stddev from RME (relative margin of error) if available
            rme = bench.get("rme", 0)
            stddev_ns = int(mean_ns * rme / 100) if rme else 0

            median_ns = int(bench.get("p50", mean_s) * 1e9)

            print(
                f"{VM_NAME},{name},"
                f"{mean_ns},{median_ns},{min_ns},{max_ns},"
                f"{stddev_ns},{samples}"
            )


def parse_text(log_path: str) -> None:
    """Parse Vitest bench default text output (fallback)."""
    print(HEADER)

    with open(log_path) as f:
        content = f.read()

    for m in TEXT_RE.finditer(content):
        name = m.group(1)
        iterations = int(m.group(4))
        avg_val = float(m.group(5))
        unit = m.group(6)
        rme_pct = float(m.group(3))

        mean_ns = int(avg_val * UNIT_TO_NS[unit])
        stddev_ns = int(mean_ns * rme_pct / 100)

        print(
            f"{VM_NAME},{name},"
            f"{mean_ns},{mean_ns},0,0,"
            f"{stddev_ns},{iterations}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <run-dir>", file=sys.stderr)
        sys.exit(1)

    run_dir = sys.argv[1]
    json_path = os.path.join(run_dir, "blaze-plutus-raw.json")
    log_path = os.path.join(run_dir, "blaze-plutus-raw.log")

    if os.path.isfile(json_path) and os.path.getsize(json_path) > 0:
        parse_json(json_path)
    elif os.path.isfile(log_path):
        parse_text(log_path)
    else:
        print(HEADER)
        print("Warning: no blaze-plutus output found", file=sys.stderr)
