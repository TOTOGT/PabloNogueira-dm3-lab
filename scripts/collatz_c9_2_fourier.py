#!/usr/bin/env python3
"""C9.2 gold Fourier diagnostics helper — stdlib-only.

Reads the per-sample CSV produced by collatz_c9_2_sampling.py and computes
discrete Fourier diagnostics per residue class, writing:

  <output>/c9_2_M{M}_N{N}_fourier.json        — top-mode summary + metadata
  <output>/c9_2_M{M}_N{N}_fourier_modes.csv   — all Fourier modes (freq, amp, phase)

The DFT is computed over the sequence of per-class mean_event_A values ordered
by residue class r = 0, 1, ..., 2^M - 1.
"""

import argparse
import cmath
import csv
import json
import math
import os


def dft(signal: list[float]) -> list[complex]:
    """Naive O(N^2) DFT — adequate for 2^M ≤ 2^16 residue classes."""
    N = len(signal)
    result = []
    for k in range(N):
        s = sum(signal[n] * cmath.exp(-2j * math.pi * k * n / N) for n in range(N))
        result.append(s)
    return result


def run(csv_path: str, M: int, output_dir: str):
    modulus = 2 ** M

    # Read per-sample CSV and aggregate mean_event_A per residue
    class_sum: dict[int, float] = {}
    class_count: dict[int, int] = {}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = int(row["residue"])
            val = float(row["mean_traj_event_A"])
            class_sum[r] = class_sum.get(r, 0.0) + val
            class_count[r] = class_count.get(r, 0) + 1

    # Build signal ordered by residue 0..2^M-1
    signal = []
    for r in range(modulus):
        if class_count.get(r, 0) > 0:
            signal.append(class_sum[r] / class_count[r])
        else:
            signal.append(0.0)

    # Compute DFT
    spectrum = dft(signal)
    N = len(spectrum)

    # Derive base filename from csv_path
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    fourier_json_path = os.path.join(output_dir, base_name + "_fourier.json")
    fourier_modes_path = os.path.join(output_dir, base_name + "_fourier_modes.csv")

    # Write modes CSV
    modes = []
    with open(fourier_modes_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["freq_index", "amplitude", "phase_rad", "re", "im"])
        writer.writeheader()
        for k, c in enumerate(spectrum):
            amp = abs(c) / N
            phase = cmath.phase(c)
            modes.append({
                "freq_index": k,
                "amplitude": round(amp, 8),
                "phase_rad": round(phase, 8),
                "re": round(c.real / N, 8),
                "im": round(c.imag / N, 8),
            })
            writer.writerow(modes[-1])

    # Top modes by amplitude (skip DC component at k=0)
    non_dc = [m for m in modes if m["freq_index"] != 0]
    top_modes = sorted(non_dc, key=lambda x: x["amplitude"], reverse=True)[:10]

    # DC component (mean of signal)
    dc_amp = modes[0]["amplitude"] if modes else float("nan")

    # Write Fourier JSON
    fourier_summary = {
        "M": M,
        "modulus": modulus,
        "csv_source": csv_path,
        "signal_length": N,
        "dc_amplitude": round(dc_amp, 8),
        "top_10_non_dc_modes": top_modes,
        "modes_csv": fourier_modes_path,
    }
    with open(fourier_json_path, "w") as f:
        json.dump(fourier_summary, f, indent=2)

    print(f"[fourier] wrote {fourier_modes_path}")
    print(f"[fourier] wrote {fourier_json_path}")
    print(f"[fourier] M={M}, modulus={modulus}, DC amplitude={dc_amp:.6f}")
    if top_modes:
        print(f"[fourier] top non-DC mode: freq_index={top_modes[0]['freq_index']}, amplitude={top_modes[0]['amplitude']:.6f}")


def main():
    parser = argparse.ArgumentParser(description="C9.2 Fourier diagnostics helper")
    parser.add_argument("--csv", required=True, help="Path to per-sample CSV from sampler")
    parser.add_argument("--M", type=int, required=True, help="Dyadic window size (must match sampler)")
    parser.add_argument("--output", default="scripts/out", help="Output directory")
    args = parser.parse_args()
    run(args.csv, args.M, args.output)


if __name__ == "__main__":
    main()
