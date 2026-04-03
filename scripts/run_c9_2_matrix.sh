#!/usr/bin/env env bash
# C9.2 matrix runner — runs sampler + Fourier diagnostics for M=12,14,16
# Usage: ./scripts/run_c9_2_matrix.sh [N] [OUTPUT_DIR] [SEED]
set -euo pipefail

N="${1:-100000}"
OUTPUT_DIR="${2:-scripts/out}"
SEED="${3:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${OUTPUT_DIR}"

for M in 12 14 16; do
  echo "=== Running M=${M} N=${N} ==="
  python3 "${SCRIPT_DIR}/collatz_c9_2_sampling.py" \
    --N "${N}" --M "${M}" --window-type dyadic \
    --output "${OUTPUT_DIR}" --seed "${SEED}"

  python3 "${SCRIPT_DIR}/collatz_c9_2_fourier.py" \
    --csv "${OUTPUT_DIR}/c9_2_M${M}_N${N}.csv" \
    --M "${M}" --output "${OUTPUT_DIR}"

  echo "--- M=${M} done ---"
done

echo ""
echo "=== All runs complete. Output files in ${OUTPUT_DIR}: ==="
ls -lh "${OUTPUT_DIR}"
