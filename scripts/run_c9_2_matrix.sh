#!/usr/bin/env bash
# run_c9_2_matrix.sh — run C9.2 sampler + Fourier diagnostics for M=12, 14, 16
#
# Usage:
#   bash scripts/run_c9_2_matrix.sh          # N=100000 (default)
#   bash scripts/run_c9_2_matrix.sh 500000   # custom N
#
# Output files land in scripts/out/:
#   c9_2_M{M}_N{N}.csv
#   c9_2_M{M}_N{N}_summary.json
#   c9_2_M{M}_N{N}_fourier.json
#   c9_2_M{M}_N{N}_fourier_modes.csv

set -euo pipefail

N="${1:-100000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for M in 12 14 16; do
    echo "========================================"
    echo " M=${M}  N=${N}"
    echo "========================================"
    python3 "${SCRIPT_DIR}/collatz_c9_2_sampling.py" --M "${M}" --N "${N}"
    python3 "${SCRIPT_DIR}/collatz_c9_2_fourier.py"  --M "${M}" --N "${N}"
    echo
done

echo "All done. Output files are in: ${SCRIPT_DIR}/out/"
