#!/usr/bin/env python3
"""
C9.2 Collatz Fourier diagnostics (stdlib only).

Reads a CSV produced by collatz_c9_2_sampling.py, reconstructs the
per-class hat_p sequence, and computes its Discrete Fourier Transform.

Output files (written to --output directory):
  c9_2_M{M}_N{N}_fourier.json        summary of DFT: DC, L2-AC norm, dominant modes
  c9_2_M{M}_N{N}_fourier_modes.csv   full per-mode table (k, amplitude, phase, re, im)

Usage:
  python3 collatz_c9_2_fourier.py \\
      --csv scripts/out/c9_2_M12_N100000.csv --M 12 --output scripts/out
"""

import argparse
import csv
import json
import math
import os


def dft(x):
    """Compute the DFT of real sequence x via the definition (O(N^2)).

    Returns a list of (re, im) tuples, one per frequency bin.
    """
    N = len(x)
    result = []
    for k in range(N):
        re = sum(x[n] * math.cos(2 * math.pi * k * n / N) for n in range(N))
        im = -sum(x[n] * math.sin(2 * math.pi * k * n / N) for n in range(N))
        result.append((re, im))
    return result


def main():
    parser = argparse.ArgumentParser(description="C9.2 Collatz Fourier diagnostics")
    parser.add_argument("--csv", required=True, help="Input CSV from collatz_c9_2_sampling.py")
    parser.add_argument("--M", type=int, required=True, help="Number of classes")
    parser.add_argument("--output", type=str, default="scripts/out", help="Output directory")
    args = parser.parse_args()

    M = args.M
    os.makedirs(args.output, exist_ok=True)

    # Derive base name and N from the CSV filename (pattern: c9_2_M{M}_N{N})
    csv_basename = os.path.splitext(os.path.basename(args.csv))[0]
    N = None
    for part in csv_basename.split("_"):
        if part.startswith("N"):
            try:
                N = int(part[1:])
            except ValueError:
                pass
    if N is None:
        import warnings
        warnings.warn(
            f"Could not parse N from filename '{csv_basename}'; N will be null in output."
        )

    # Aggregate per-class event_A counts from the CSV
    class_A = {}
    class_counts = {}
    with open(args.csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = int(row["class"])
            class_A[c] = class_A.get(c, 0) + int(row["event_A"])
            class_counts[c] = class_counts.get(c, 0) + 1

    hat_p = [
        class_A.get(c, 0) / class_counts[c] if c in class_counts and class_counts[c] > 0 else 0.0
        for c in range(M)
    ]

    # DFT of the hat_p sequence
    X = dft(hat_p)
    amplitudes = [math.sqrt(r ** 2 + i ** 2) for r, i in X]
    phases = [math.atan2(i, r) for r, i in X]

    # DC component (k=0), normalised by M
    dc_amplitude = amplitudes[0] / M if M > 0 else 0.0

    # L2 norm of the AC components (k >= 1)
    l2_ac = math.sqrt(sum(amplitudes[k] ** 2 for k in range(1, M)))

    # Top-3 dominant AC modes by amplitude
    ac_modes_sorted = sorted(range(1, M), key=lambda k: amplitudes[k], reverse=True)
    dominant_modes = ac_modes_sorted[: min(3, len(ac_modes_sorted))]

    fourier_result = {
        "M": M,
        "N": N,
        "dc_amplitude": dc_amplitude,
        "l2_ac_norm": l2_ac,
        "dominant_modes": dominant_modes,
        "dominant_amplitudes": [amplitudes[k] for k in dominant_modes],
        "hat_p": hat_p,
    }

    fourier_path = os.path.join(args.output, f"{csv_basename}_fourier.json")
    with open(fourier_path, "w") as f:
        json.dump(fourier_result, f, indent=2)

    modes_csv_path = os.path.join(args.output, f"{csv_basename}_fourier_modes.csv")
    with open(modes_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["k", "amplitude", "phase", "re", "im"])
        for k in range(M):
            writer.writerow([k, amplitudes[k], phases[k], X[k][0], X[k][1]])

    print(f"Wrote {fourier_path}")
    print(f"Wrote {modes_csv_path}")
    print(
        f"M={M} dc={dc_amplitude:.6f} l2_ac={l2_ac:.6e} "
        f"dominant_modes={dominant_modes}"
    )


if __name__ == "__main__":
    main()
