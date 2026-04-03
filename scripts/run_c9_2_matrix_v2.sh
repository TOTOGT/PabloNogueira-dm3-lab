#!/usr/bin/env bash
# run_c9_2_matrix_v2.sh
# Runner for the C9.2 pipeline (sampler → Fourier v2).
#
# Usage:
#   ./scripts/run_c9_2_matrix_v2.sh <sampler_script> --M <M> --N <N> [--seed <seed>]
#
# Example:
#   ./scripts/run_c9_2_matrix_v2.sh scripts/collatz_c9_2_sampling_option1.py --M 8 --N 10000

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SAMPLER="${1:?Usage: $0 <sampler_script> --M <M> --N <N> [--seed <seed>]}"
shift

# Parse --M and --N (and optional --seed) from remaining args
M=""
N=""
SEED="42"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --M) M="$2"; shift 2 ;;
        --N) N="$2"; shift 2 ;;
        --seed) SEED="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$M" || -z "$N" ]]; then
    echo "Error: --M and --N are required" >&2
    exit 1
fi

OUT_DIR="${REPO_ROOT}/scripts/out"
mkdir -p "${OUT_DIR}"

echo "=== C9.2 Pipeline v2 ==="
echo "    Sampler : ${SAMPLER}"
echo "    M=${M}  N=${N}  seed=${SEED}"
echo "    Out dir : ${OUT_DIR}"
echo ""

# Step 1: Run sampler
echo "[1/2] Running sampler..."
python3 "${REPO_ROOT}/${SAMPLER}" \
    --M "${M}" \
    --N "${N}" \
    --out-dir "${OUT_DIR}" \
    --seed "${SEED}"

CSV_FILE="${OUT_DIR}/c9_2_M${M}_N${N}.csv"
if [[ ! -f "${CSV_FILE}" ]]; then
    echo "Error: expected sampler output not found: ${CSV_FILE}" >&2
    exit 1
fi
echo "    -> ${CSV_FILE}"

# Step 2: Run Fourier v2
echo "[2/2] Running Fourier v2..."
python3 "${SCRIPT_DIR}/collatz_c9_2_fourier_v2.py" \
    --input "${CSV_FILE}" \
    --out-dir "${OUT_DIR}"

echo ""
echo "=== Pipeline complete ==="
echo "Artifacts in ${OUT_DIR}:"
ls -lh "${OUT_DIR}/c9_2_M${M}_N${N}"* 2>/dev/null || true
