#!/usr/bin/env python3
"""
collatz_c9_2_fourier_v2.py
Fourier analysis for C9.2 observable (Option 1 semantics locked).
- Reads CSV produced by collatz_c9_2_sampling_option1.py
- Computes FFT on the observable time series
- Outputs:
  * c9_2_M{M}_N{N}_fourier.json   (summary statistics)
  * c9_2_M{M}_N{N}_fourier_modes.csv (frequency, amplitude, phase)
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True,
                        help="Input CSV from sampler (c9_2_M{M}_N{N}.csv)")
    parser.add_argument("--out-dir", type=str, required=True,
                        help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Parse M and N from filename (e.g. c9_2_M12_N100000.csv)
    stem = input_path.stem
    M = int(stem.split("_M")[1].split("_N")[0])
    N = int(stem.split("_N")[1])

    # Load sampler output
    df = pd.read_csv(input_path)
    # Observable series: 1 if condition met, 0 otherwise (locked Option 1)
    series = df["observable"].values.astype(float)

    # Compute FFT
    fft_vals = np.fft.fft(series)
    freqs = np.fft.fftfreq(N, d=1.0)
    amps = np.abs(fft_vals) / N
    phases = np.angle(fft_vals)

    # Keep only positive frequencies + DC
    pos = freqs >= 0
    modes_df = pd.DataFrame({
        "frequency": freqs[pos],
        "amplitude": amps[pos],
        "phase": phases[pos]
    }).sort_values("amplitude", ascending=False)

    # Summary JSON
    summary = {
        "M": M,
        "N": N,
        "mean_observable": float(series.mean()),
        "max_amplitude": float(modes_df["amplitude"].max()),
        "dominant_frequency": float(modes_df.iloc[1]["frequency"]) if len(modes_df) > 1 else 0.0,
        "spectral_gap_estimate": (
            float(modes_df.iloc[1]["amplitude"] / modes_df.iloc[0]["amplitude"])
            if len(modes_df) > 1 else 0.0
        )
    }

    # Save outputs with exact required filenames
    json_path = out_dir / f"c9_2_M{M}_N{N}_fourier.json"
    csv_path = out_dir / f"c9_2_M{M}_N{N}_fourier_modes.csv"

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    modes_df.to_csv(csv_path, index=False)

    print(f"Fourier v2 complete")
    print(f"   JSON  -> {json_path}")
    print(f"   CSV   -> {csv_path}")
    print(f"   Mean observable: {summary['mean_observable']:.6f}")
    print(f"   Dominant freq : {summary['dominant_frequency']:.6f}")
    print(f"   Spectral gap est: {summary['spectral_gap_estimate']:.6f}")


if __name__ == "__main__":
    main()
