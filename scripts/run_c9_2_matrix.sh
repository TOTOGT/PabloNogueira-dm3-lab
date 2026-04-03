#!/usr/bin/env bash
set -euo pipefail

OUTDIR=scripts/out
mkdir -p "$OUTDIR"

SAMPLER=scripts/collatz_c9_2_sampling.py
FOURIER=scripts/collatz_c9_2_fourier.py

for M in 12 14 16; do
  echo "=== RUNNING sampling M=$M ==="
  python3 "$SAMPLER" --N 100000 --M "$M" --window-type dyadic --output "$OUTDIR" || {
    echo "Sampler failed for M=$M; check script path: $SAMPLER"
    exit 1
  }

  CSV="$OUTDIR/c9_2_M${M}_N100000.csv"
  if [ -f "$CSV" ]; then
    echo "=== RUNNING fourier M=$M ==="
    python3 "$FOURIER" --csv "$CSV" --M "$M" --output "$OUTDIR" || {
      echo "Fourier helper failed for M=$M; check script path: $FOURIER"
      exit 1
    }
  else
    echo "Expected CSV not found: $CSV"
    exit 1
  fi
done

echo "All runs complete. Artifacts in $OUTDIR"
