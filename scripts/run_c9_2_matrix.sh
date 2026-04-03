#!/usr/bin/env bash
# run_c9_2_matrix.sh — run the Collatz C9.2 empirical pipeline for M=12,14,16
#
# Usage:
#   bash scripts/run_c9_2_matrix.sh
#
# Set N (sample count), SEED, and OUTDIR via environment variables, e.g.:
#   N=50000 bash scripts/run_c9_2_matrix.sh
#
# Outputs (per M value)
#   $OUTDIR/c9_2_M{M}_N{N}.csv
#   $OUTDIR/c9_2_M{M}_N{N}_summary.json
#   $OUTDIR/c9_2_M{M}_N{N}_fourier.json
#   $OUTDIR/c9_2_M{M}_N{N}_fourier_modes.csv

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${OUTDIR:-$REPO_ROOT/scripts/out}"
N="${N:-100000}"
SEED="${SEED:-42}"

SAMPLER="$REPO_ROOT/scripts/collatz_c9_2_sampling.py"
FOURIER="$REPO_ROOT/scripts/collatz_c9_2_fourier.py"

mkdir -p "$OUTDIR"

echo "=== Collatz C9.2 matrix run: N=$N seed=$SEED ==="
echo "Output directory: $OUTDIR"
echo ""

# Summary table header
printf "%-4s | %-8s | %-12s | %-12s | %-16s | %s\n" \
    "M" "N" "mean_hat_p" "l2_variance" "sparse_fraction" "runtime"
printf "%s\n" "-------------------------------------------------------------------"

for M in 12 14 16; do
    echo ""
    echo "=== Sampling: M=$M ==="
    python3 "$SAMPLER" \
        --N "$N" \
        --M "$M" \
        --window-type dyadic \
        --seed "$SEED" \
        --output "$OUTDIR" || {
        echo "ERROR: sampler failed for M=$M (script: $SAMPLER)" >&2
        exit 1
    }

    CSV="$OUTDIR/c9_2_M${M}_N${N}.csv"
    if [ ! -f "$CSV" ]; then
        echo "ERROR: expected CSV not found: $CSV" >&2
        exit 1
    fi

    echo "=== Fourier: M=$M ==="
    python3 "$FOURIER" \
        --csv "$CSV" \
        --M "$M" \
        --output "$OUTDIR" || {
        echo "ERROR: fourier script failed for M=$M (script: $FOURIER)" >&2
        exit 1
    }
done

echo ""
echo "=== All runs complete. Artifacts in $OUTDIR ==="
ls -lh "$OUTDIR"
