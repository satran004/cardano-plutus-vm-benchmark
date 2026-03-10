#!/bin/bash
set -euo pipefail

RUN_DIR="$1"
DATA_DIR="/bench/data/plutus_use_cases"
BENCH_DIR="/bench/opshin"

echo "opshin-uplc (Python)"

cd "$BENCH_DIR"

# Patch the hardcoded BENCH_DIR path to use canonical data
sed -i "s|os.path.expanduser.*plutus_use_cases.*|\"${DATA_DIR}\"|" bench_plutus_use_cases.py

# Run benchmark
python3 bench_plutus_use_cases.py 2>&1 | tee "$RUN_DIR/opshin-raw.log"

# Parse into unified CSV
python3 /bench/parsers/parse_opshin.py "$RUN_DIR/opshin-raw.log" > "$RUN_DIR/opshin.csv"
