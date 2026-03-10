#!/bin/bash
set -euo pipefail

RUN_DIR="$1"
DATA_DIR="/bench/data/plutus_use_cases"
PROJECT_DIR="/bench/chrysalis"

echo "Chrysalis (.NET / BenchmarkDotNet)"

# Symlink canonical flat files into expected location
rm -rf "$PROJECT_DIR/benchmarks/data/plutus_use_cases"
ln -sf "$DATA_DIR" "$PROJECT_DIR/benchmarks/data/plutus_use_cases"

cd "$PROJECT_DIR"
dotnet run -c Release --project benchmarks/PlutusBench -- \
    --exporters json \
    2>&1 | tee "$RUN_DIR/chrysalis-raw.log"

# Copy BenchmarkDotNet artifacts
cp -r benchmarks/PlutusBench/BenchmarkDotNet.Artifacts/results/* "$RUN_DIR/" 2>/dev/null || true

# Parse into unified CSV
python3 /bench/parsers/parse_benchmarkdotnet.py "$RUN_DIR" > "$RUN_DIR/chrysalis.csv"
