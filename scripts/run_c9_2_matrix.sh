#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/out"
mkdir -p "$OUT_DIR"

N="${N:-1000}"
WINDOW_TYPE="${WINDOW_TYPE:-dyadic}"
START="${START:-1}"
END="${END:-1000}"
SAMPLE_RATE="${SAMPLE_RATE:-1.0}"
SEED="${SEED:-42}"

for M in 12 14 16; do
    echo "=== Running C9.2 sampling: M=$M N=$N ==="
    python3 "$SCRIPT_DIR/collatz_c9_2_sampling.py" \
        --M "$M" \
        --N "$N" \
        --window-type "$WINDOW_TYPE" \
        --start "$START" \
        --end "$END" \
        --sample-rate "$SAMPLE_RATE" \
        --seed "$SEED" \
        --output "$OUT_DIR/c9_2_M${M}_N${N}.csv"

    CSV="$OUT_DIR/c9_2_M${M}_N${N}.csv"
    if [ -f "$CSV" ]; then
        echo "=== Running C9.2 Fourier analysis: M=$M N=$N ==="
        python3 "$SCRIPT_DIR/collatz_c9_2_fourier.py" \
            --input "$CSV" \
            --output-dir "$OUT_DIR"
    else
        echo "Warning: expected output $CSV not found, skipping Fourier step."
    fi
done

echo "=== All matrix runs complete ==="
