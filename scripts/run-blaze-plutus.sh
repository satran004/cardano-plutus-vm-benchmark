#!/bin/bash
set -euo pipefail

RUN_DIR="$1"
DATA_DIR="/bench/data/plutus_use_cases"
BENCH_DIR="/bench/blaze-plutus"

echo "blaze-plutus (TypeScript / Vitest bench)"

# Symlink canonical flat files into expected location
rm -rf "$BENCH_DIR/packages/blaze-plutus/bench/plutus_use_cases"
ln -sf "$DATA_DIR" "$BENCH_DIR/packages/blaze-plutus/bench/plutus_use_cases"

cd "$BENCH_DIR/packages/blaze-plutus"

# Run vitest bench with JSON reporter
bun run vitest bench --run --reporter=json \
    2>"$RUN_DIR/blaze-plutus-stderr.log" \
    1>"$RUN_DIR/blaze-plutus-raw.json" || true

# Fallback: if JSON reporter fails, run with default reporter
if [[ ! -s "$RUN_DIR/blaze-plutus-raw.json" ]]; then
    echo "JSON reporter failed, falling back to default output"
    bun run vitest bench --run \
        2>&1 | tee "$RUN_DIR/blaze-plutus-raw.log"
fi

# Parse into unified CSV
python3 /bench/parsers/parse_vitest.py "$RUN_DIR" > "$RUN_DIR/blaze-plutus.csv"
