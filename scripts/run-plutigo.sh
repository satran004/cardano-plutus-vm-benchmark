#!/bin/bash
set -euo pipefail

RUN_DIR="$1"
DATA_DIR="/bench/data/plutus_use_cases"
BENCH_DIR="/bench/plutigo"

echo "Plutigo (Go / testing.B)"

# Symlink canonical flat files into expected location for the test binary
mkdir -p "$BENCH_DIR/tests"
rm -rf "$BENCH_DIR/tests/bench"
ln -sf "$DATA_DIR" "$BENCH_DIR/tests/bench"

cd "$BENCH_DIR"

# Run compiled Go test binary with benchmark flags
./plutigo-bench \
    -test.bench=BenchmarkFlatFiles \
    -test.benchmem \
    -test.run='^$' \
    -test.count=1 \
    -test.benchtime=5s \
    2>&1 | tee "$RUN_DIR/plutigo-raw.log"

# Parse into unified CSV
python3 /bench/parsers/parse_go_bench.py "$RUN_DIR/plutigo-raw.log" > "$RUN_DIR/plutigo.csv"
