#!/bin/bash
set -euo pipefail

RUN_DIR="$1"
DATA_DIR="/bench/data/plutus_use_cases"
BENCH_DIR="/bench/uplc-turbo"

echo "uplc-turbo (Rust / Criterion)"

# Symlink canonical flat files into expected location
rm -rf "$BENCH_DIR/crates/uplc/benches/use_cases/plutus_use_cases"
ln -sf "$DATA_DIR" "$BENCH_DIR/crates/uplc/benches/use_cases/plutus_use_cases"

cd "$BENCH_DIR"

# Run Criterion benchmark (binary already compiled in build stage)
find target/release/deps -name 'use_cases-*' -executable -type f | head -1 | \
    xargs -I{} {} --bench 2>&1 | tee "$RUN_DIR/uplc-turbo-raw.log"

# Copy Criterion JSON output
cp -r target/criterion "$RUN_DIR/criterion-output" 2>/dev/null || true

# Parse into unified CSV
python3 /bench/parsers/parse_criterion.py "$RUN_DIR/criterion-output" > "$RUN_DIR/uplc-turbo.csv"
