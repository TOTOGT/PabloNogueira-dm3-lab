#!/usr/bin/env python3
"""
C9.2 Fourier diagnostics (stdlib only).

Reads the per-class CSV produced by collatz_c9_2_sampling.py and computes the
Discrete Fourier Transform of the hat_p sequence indexed by residue class.

Uses a pure-Python iterative Cooley-Tukey radix-2 FFT (O(n log n)) so it
remains fast even for M=16 (65 536 classes).

Input (auto-located from --M / --N):
    <indir>/c9_2_M{M}_N{N}.csv

Outputs:
    <indir>/c9_2_M{M}_N{N}_fourier.json        global Fourier stats
    <indir>/c9_2_M{M}_N{N}_fourier_modes.csv   top-k modes ranked by amplitude

Usage:
    python3 collatz_c9_2_fourier.py --M 12 --N 100000
    python3 collatz_c9_2_fourier.py --M 14 --N 500000 --top 32
"""

import argparse
import cmath
import csv
import json
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_INDIR = os.path.join(_SCRIPT_DIR, "out")


# ---------------------------------------------------------------------------
# FFT  (iterative Cooley-Tukey, radix-2, DIT)
# ---------------------------------------------------------------------------

def _bit_reverse_copy(a: list) -> list:
    n = len(a)
    bits = int(round(math.log2(n)))
    result = [0.0] * n
    for i in range(n):
        rev = 0
        x = i
        for _ in range(bits):
            rev = (rev << 1) | (x & 1)
            x >>= 1
        result[rev] = a[i]
    return result


def fft(x: list) -> list:
    """
    Iterative radix-2 Cooley-Tukey FFT.
    len(x) must be a power of 2.
    Returns list of complex values.
    """
    n = len(x)
    if n == 0:
        return []
    # Pad to power-of-2 if needed (shouldn't happen for 2^M classes)
    assert (n & (n - 1)) == 0, "FFT length must be a power of 2"

    A = [complex(v) for v in _bit_reverse_copy(x)]

    length = 2
    while length <= n:
        w_len = cmath.exp(-2j * math.pi / length)
        for i in range(0, n, length):
            w = complex(1.0)
            half = length >> 1
            for j in range(half):
                u = A[i + j]
                v = A[i + j + half] * w
                A[i + j]        = u + v
                A[i + j + half] = u - v
                w *= w_len
        length <<= 1

    return A


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2 Fourier diagnostics on per-class hat_p values"
    )
    parser.add_argument("--M", type=int, required=True,
                        help="Bit depth used in sampling")
    parser.add_argument("--N", type=int, required=True,
                        help="Sample count used in sampling")
    parser.add_argument("--indir", type=str, default=_DEFAULT_INDIR,
                        help="Input/output directory (default: <script_dir>/out)")
    parser.add_argument("--top", type=int, default=20,
                        help="Number of top AC modes to include in modes CSV (default: 20)")
    args = parser.parse_args()

    M, N = args.M, args.N
    base = f"c9_2_M{M}_N{N}"
    csv_in           = os.path.join(args.indir, f"{base}.csv")
    fourier_json     = os.path.join(args.indir, f"{base}_fourier.json")
    fourier_modes_csv = os.path.join(args.indir, f"{base}_fourier_modes.csv")

    if not os.path.exists(csv_in):
        print(
            f"ERROR: {csv_in} not found. "
            "Run collatz_c9_2_sampling.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    modulus = 1 << M

    # ---- read hat_p indexed by class --------------------------------------
    hat_p = [float("nan")] * modulus
    with open(csv_in, newline="") as f:
        for row in csv.DictReader(f):
            r   = int(row["class"])
            val = row["hat_p"]
            hat_p[r] = float(val) if val.lower() != "nan" else float("nan")

    valid_vals = [v for v in hat_p if not math.isnan(v)]
    n_valid    = len(valid_vals)
    fill_val   = sum(valid_vals) / n_valid if valid_vals else 0.0

    # Replace NaN (empty even classes) with the mean before DFT
    hat_p_filled = [v if not math.isnan(v) else fill_val for v in hat_p]

    print(f"[C9.2 Fourier] M={M}  N={N}  modulus={modulus}", flush=True)
    print(
        f"[C9.2 Fourier] Valid classes: {n_valid}/{modulus} "
        f"(NaN fill={fill_val:.6f})",
        flush=True,
    )
    print("[C9.2 Fourier] Running FFT...", flush=True)

    X = fft(hat_p_filled)

    magnitudes = [abs(c) for c in X]
    phases     = [cmath.phase(c) for c in X]

    # ---- power stats -------------------------------------------------------
    total_power = sum(m * m for m in magnitudes)
    dc_power    = magnitudes[0] ** 2
    ac_power    = total_power - dc_power

    # Sort AC modes (k >= 1) by magnitude descending
    ac_indexed = sorted(
        ((k, magnitudes[k]) for k in range(1, modulus)),
        key=lambda t: t[1],
        reverse=True,
    )
    top_ac = ac_indexed[: args.top]

    # ---- write fourier_modes.csv -------------------------------------------
    with open(fourier_modes_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "k", "magnitude", "phase_rad", "re", "im"])
        for rank, (k, mag) in enumerate(top_ac):
            writer.writerow([
                rank, k, mag, phases[k],
                X[k].real, X[k].imag,
            ])

    # ---- write fourier.json -----------------------------------------------
    top1_k   = ac_indexed[0][0]   if ac_indexed else None
    top1_mag = ac_indexed[0][1]   if ac_indexed else None

    summary = {
        "M":                  M,
        "N":                  N,
        "modulus":            modulus,
        "n_valid_classes":    n_valid,
        "nan_fill_value":     fill_val,
        "dc_magnitude":       magnitudes[0],
        "dc_power":           dc_power,
        "ac_power":           ac_power,
        "total_power":        total_power,
        "ac_power_fraction":  ac_power / total_power if total_power > 0 else 0.0,
        "top_ac_mode_k":      top1_k,
        "top_ac_magnitude":   top1_mag,
        "csv_in":             csv_in,
        "fourier_modes_csv":  fourier_modes_csv,
    }

    with open(fourier_json, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"[C9.2 Fourier] Written: {fourier_modes_csv}")
    print(f"[C9.2 Fourier] Written: {fourier_json}")
    print(
        f"[C9.2 Fourier] DC mag={magnitudes[0]:.6f}  "
        f"AC power fraction={summary['ac_power_fraction']:.6f}  "
        f"top AC mode k={top1_k}  mag={top1_mag:.6f}"
    )


if __name__ == "__main__":
    main()
