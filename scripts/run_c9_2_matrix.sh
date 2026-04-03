#!/usr/bin/env bash
set -euo pipefail
OUTDIR=scripts/out
mkdir -p "$OUTDIR"
SAMPLER=scripts/collatz_c9_2_sampling.py
FOURIER=scripts/collatz_c9_2_fourier.py
for M in 12 14 16; do
  echo "=== sampling M=$M ==="
  python3 "$SAMPLER" --N 100000 --M "$M" --window-type dyadic --output "$OUTDIR"
  CSV="$OUTDIR/c9_2_M${M}_N100000.csv"
  if [ ! -f "$CSV" ]; then
    echo "Missing CSV: $CSV" >&2
    exit 1
  fi
  echo "=== fourier M=$M ==="
  python3 "$FOURIER" --csv "$CSV" --M "$M" --output "$OUTDIR"
done
echo "Done. Artifacts in $OUTDIR"
