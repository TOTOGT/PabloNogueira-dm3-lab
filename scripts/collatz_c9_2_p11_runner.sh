#!/usr/bin/env bash
# scripts/collatz_c9_2_p11_runner.sh
#
# Runner for C9.2 weighted (1,1) consecutive-valuation probability experiments.
# Executes a recommended matrix of runs and stores results under results/c9_2/.
#
# Usage (from repo root):
#   bash scripts/collatz_c9_2_p11_runner.sh
#
# Optional env overrides:
#   SEED=42  (default)
#   OUT_DIR=results/c9_2  (default)
#   PYTHON=python3  (default)

set -euo pipefail

SEED="${SEED:-42}"
OUT_DIR="${OUT_DIR:-results/c9_2}"
PYTHON="${PYTHON:-python3}"
SAMPLER="scripts/collatz_c9_2_p11_sampler.py"

echo "=== C9.2 p11 runner  seed=${SEED}  out=${OUT_DIR} ==="

# ---------------------------------------------------------------------------
# Run 1: N=1e5 exhaustive (feasible; ~50k odd n in dyadic window [1e5, 2e5))
# ---------------------------------------------------------------------------
echo ""
echo "--- Run 1: N=100000 exhaustive (dyadic window) ---"
$PYTHON "$SAMPLER" \
  --N 100000 \
  --mode exhaustive \
  --seed "$SEED" \
  --bootstrap 1000 \
  --bootstrap-mode weighted \
  --out-dir "$OUT_DIR/run1_N1e5_exhaustive"

# Run 1b: same window with per-residue breakdown (M=4)
echo ""
echo "--- Run 1b: N=100000 exhaustive with M=4 per-residue breakdown ---"
$PYTHON "$SAMPLER" \
  --N 100000 \
  --mode exhaustive \
  --M 4 \
  --seed "$SEED" \
  --bootstrap 1000 \
  --bootstrap-mode weighted \
  --out-dir "$OUT_DIR/run1b_N1e5_exhaustive_M4"

# ---------------------------------------------------------------------------
# Run 2: N=1e6 random with max-samples=1e6
# ---------------------------------------------------------------------------
echo ""
echo "--- Run 2: N=1000000 random max-samples=1000000 ---"
$PYTHON "$SAMPLER" \
  --N 1000000 \
  --mode random \
  --max-samples 1000000 \
  --seed "$SEED" \
  --bootstrap 1000 \
  --bootstrap-mode weighted \
  --out-dir "$OUT_DIR/run2_N1e6_random"

# ---------------------------------------------------------------------------
# Run 3: N=1e6 exhaustive via stride (deterministic, ~50k samples)
# ---------------------------------------------------------------------------
echo ""
echo "--- Run 3: N=1000000 stride max-samples=50000 (deterministic) ---"
$PYTHON "$SAMPLER" \
  --N 1000000 \
  --mode stride \
  --max-samples 50000 \
  --seed "$SEED" \
  --bootstrap 500 \
  --bootstrap-mode block \
  --out-dir "$OUT_DIR/run3_N1e6_stride"

# ---------------------------------------------------------------------------
# Run 4: N=1e6 random with block bootstrap for comparison
# ---------------------------------------------------------------------------
echo ""
echo "--- Run 4: N=1000000 random block-bootstrap ---"
$PYTHON "$SAMPLER" \
  --N 1000000 \
  --mode random \
  --max-samples 200000 \
  --seed "$SEED" \
  --bootstrap 500 \
  --bootstrap-mode block \
  --out-dir "$OUT_DIR/run4_N1e6_block_bs"

echo ""
echo "=== All runs complete. Results in ${OUT_DIR}/ ==="
echo "Summary JSONs:"
find "$OUT_DIR" -name "*_summary.json" | sort | while read -r f; do
  echo "  $f"
done
