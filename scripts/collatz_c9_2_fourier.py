#!/usr/bin/env python3
"""
Collatz C9.2 Fourier analysis.

Reads the per-sample CSV produced by collatz_c9_2_sampling.py, reconstructs
hat_p as a function of dyadic residue class r ∈ [0, 2^M), then applies a
radix-2 Cooley-Tukey FFT (pure stdlib, O(N log N)) to obtain the frequency
spectrum.  Reports the top Fourier modes by magnitude and writes full
spectrum data to disk.

Usage
-----
    python3 collatz_c9_2_fourier.py \\
        --csv out/c9_2_M12_N100000.csv \\
        --M 12 \\
        --output out/

Output files (written to --output directory)
--------------------------------------------
    <stem>_fourier.json      -- full spectrum + summary (JSON)
    <stem>_fourier_modes.csv -- top-k modes sorted by magnitude (CSV)

Key fields in fourier.json
--------------------------
    mean_hat_p   : mean of hat_p signal
    rms_absF     : RMS of |F_k| over k = 1 … N-1  (AC energy)
    dc_magnitude : |F_0| (DC component)
    top_modes    : list of {rank, k, magnitude, phase, re, im}
    spectrum     : full list of {k, re, im, magnitude, phase}
"""

import argparse
import cmath
import csv
import json
import math
import os


# ---------------------------------------------------------------------------
# Radix-2 Cooley-Tukey FFT  (N must be a power of 2)
# ---------------------------------------------------------------------------

def _fft_recursive(signal: list) -> list:
    """Return the DFT of *signal* using the radix-2 Cooley-Tukey algorithm."""
    N = len(signal)
    if N == 1:
        return [complex(signal[0])]
    if N & (N - 1):
        raise ValueError(f"FFT length must be a power of 2, got {N}")

    even = _fft_recursive(signal[0::2])
    odd = _fft_recursive(signal[1::2])

    half = N >> 1
    twiddle = [cmath.exp(-2j * cmath.pi * k / N) * odd[k] for k in range(half)]
    return (
        [even[k] + twiddle[k] for k in range(half)]
        + [even[k] - twiddle[k] for k in range(half)]
    )


def fft(signal: list) -> list:
    """
    Compute the FFT of *signal* (length must be a power of 2).

    Uses an iterative wrapper around the recursive Cooley-Tukey kernel to
    avoid Python recursion-limit issues for large M (e.g. M=16 → 65536 pts).
    """
    import sys
    N = len(signal)
    if N & (N - 1):
        raise ValueError(f"FFT length must be a power of 2, got {N}")
    old_limit = sys.getrecursionlimit()
    # Each level halves N; depth = log2(N).  Add headroom.
    depth = N.bit_length()
    sys.setrecursionlimit(max(old_limit, depth * 4 + 256))
    try:
        return _fft_recursive(signal)
    finally:
        sys.setrecursionlimit(old_limit)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collatz C9.2 Fourier analysis"
    )
    parser.add_argument(
        "--csv", required=True,
        help="Input CSV produced by collatz_c9_2_sampling.py"
    )
    parser.add_argument(
        "--M", type=int, required=True,
        help="Window parameter: dyadic modulus = 2^M"
    )
    parser.add_argument(
        "--output", default="scripts/out",
        help="Output directory (default: scripts/out)"
    )
    parser.add_argument(
        "--top-modes", type=int, default=20,
        help="Number of top AC Fourier modes to report (default: 20)"
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    mod = 1 << args.M     # 2^M
    csv_path = args.csv
    stem = os.path.splitext(os.path.basename(csv_path))[0]
    fourier_json_path = os.path.join(args.output, f"{stem}_fourier.json")
    fourier_modes_csv_path = os.path.join(args.output, f"{stem}_fourier_modes.csv")

    # ------------------------------------------------------------------
    # Build hat_p signal: one value per residue class r in [0, 2^M)
    # ------------------------------------------------------------------
    bucket_count = [0] * mod
    bucket_hit = [0] * mod

    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            residue = int(row["residue"]) & (mod - 1)
            bucket_count[residue] += 1
            bucket_hit[residue] += int(row["reached_1"])

    hat_p_signal = [
        (bucket_hit[r] / bucket_count[r]) if bucket_count[r] > 0 else 0.0
        for r in range(mod)
    ]
    mean_hat_p = sum(hat_p_signal) / mod

    # ------------------------------------------------------------------
    # FFT
    # ------------------------------------------------------------------
    if mod > (1 << 16):
        print(
            f"Warning: mod={mod} is very large; FFT may be slow in pure Python."
        )

    dft_vals = fft(hat_p_signal)

    # ------------------------------------------------------------------
    # Build spectrum records
    # ------------------------------------------------------------------
    spectrum = []
    for k, c in enumerate(dft_vals):
        spectrum.append({
            "k": k,
            "re": c.real,
            "im": c.imag,
            "magnitude": abs(c),
            "phase": cmath.phase(c),
        })

    # rms_absF: RMS of AC magnitudes (k >= 1)
    ac_magnitudes = [s["magnitude"] for s in spectrum[1:]]
    rms_absF = math.sqrt(
        sum(m * m for m in ac_magnitudes) / len(ac_magnitudes)
    ) if ac_magnitudes else 0.0

    # Top AC modes sorted by descending magnitude
    ac_modes_sorted = sorted(spectrum[1:], key=lambda s: s["magnitude"], reverse=True)
    top_k = min(args.top_modes, len(ac_modes_sorted))
    top_modes = [
        {
            "rank": rank,
            "k": s["k"],
            "magnitude": s["magnitude"],
            "phase": s["phase"],
            "re": s["re"],
            "im": s["im"],
        }
        for rank, s in enumerate(ac_modes_sorted[:top_k], start=1)
    ]

    # ------------------------------------------------------------------
    # Write fourier.json
    # ------------------------------------------------------------------
    fourier_json = {
        "M": args.M,
        "mod": mod,
        "csv": csv_path,
        "mean_hat_p": mean_hat_p,
        "rms_absF": rms_absF,
        "dc_magnitude": spectrum[0]["magnitude"],
        "top_modes": top_modes,
        "spectrum": spectrum,
    }
    with open(fourier_json_path, "w") as fh:
        json.dump(fourier_json, fh, indent=2)

    # ------------------------------------------------------------------
    # Write fourier_modes.csv
    # ------------------------------------------------------------------
    with open(fourier_modes_csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["rank", "k", "magnitude", "phase", "re", "im"]
        )
        writer.writeheader()
        for mode in top_modes:
            writer.writerow({
                "rank": mode["rank"],
                "k": mode["k"],
                "magnitude": f"{mode['magnitude']:.8f}",
                "phase": f"{mode['phase']:.8f}",
                "re": f"{mode['re']:.8f}",
                "im": f"{mode['im']:.8f}",
            })

    print(
        f"M={args.M} "
        f"mean_hat_p={mean_hat_p:.6f} "
        f"rms_absF={rms_absF:.6f} "
        f"dc={spectrum[0]['magnitude']:.6f}"
    )
    print(f"Fourier JSON     : {fourier_json_path}")
    print(f"Fourier modes CSV: {fourier_modes_csv_path}")


if __name__ == "__main__":
    main()
