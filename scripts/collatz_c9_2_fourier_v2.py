"""
C9.2 Fourier analysis (v2) — 2-adic Fourier signature of per-residue log drifts.

Reads the per-residue mean log-drift CSV produced by
collatz_c9_2_sampling_option1.py, orders the odd residue classes by value,
and computes their DFT.  The spectrum is inspected for a dominant mode
after discarding the lowest `low_cut_fraction` of frequencies (near-DC
removal).

Key output metrics
------------------
dominant_fourier_mode
    1-indexed rank of the mode with the highest amplitude in the
    post-low-cut one-sided amplitude spectrum.  A value of 1 means there
    is a single clear dominant mode (mode rank 1 out of all kept modes).

avg_rms_ratio
    Ratio of the dominant mode's normalised amplitude to the RMS of all
    other kept amplitudes:
        avg_rms_ratio = A_max / rms(A_k  for k in kept, k != dominant)
    where  A_k = |F_k| / N  (1/N-normalised DFT amplitude).

Outputs
-------
<out-dir>/c9_2_M{M}_N{N}_fourier_modes.csv
    Columns: mode_index, frequency, amplitude, phase_rad

<out-dir>/c9_2_M{M}_N{N}_fourier.json
    Summary: dominant_fourier_mode, avg_rms_ratio, dominant_freq,
    dominant_amplitude, and provenance fields.

Golden-run command (after the sampler has been run):
    python3 scripts/collatz_c9_2_fourier_v2.py \\
        --input scripts/out/c9_2_M12_N100000.csv \\
        --out-dir scripts/out --low-cut-fraction 0.125
"""

import argparse
import csv
import json
import math
import os
import re

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:  # pragma: no cover
    _HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Pure-Python fallback FFT (Cooley-Tukey, power-of-two only)
# ---------------------------------------------------------------------------

def _fft_py(x: list) -> list:
    """Iterative Cooley-Tukey FFT for real or complex input, length = 2^k."""
    n = len(x)
    if n == 1:
        return list(x)

    # Bit-reversal permutation
    out = list(x)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            out[i], out[j] = out[j], out[i]

    # Cooley-Tukey butterfly
    length = 2
    while length <= n:
        half = length >> 1
        angle = -2.0 * math.pi / length
        w_base = complex(math.cos(angle), math.sin(angle))
        for i in range(0, n, length):
            w = complex(1.0, 0.0)
            for k in range(half):
                t = w * out[i + k + half]
                out[i + k + half] = out[i + k] - t
                out[i + k] = out[i + k] + t
                w *= w_base
        length <<= 1

    return out


def _compute_fft(values: list) -> list:
    """Return complex DFT of `values` (list of floats), length need not be 2^k."""
    if _HAS_NUMPY:
        return np.fft.fft(values).tolist()

    n = len(values)
    # Pad to next power of two for the pure-Python path
    p = 1
    while p < n:
        p <<= 1
    padded = list(values) + [0.0] * (p - n)
    full = _fft_py(padded)
    return full[:n]


# ---------------------------------------------------------------------------
# Main analysis routine
# ---------------------------------------------------------------------------

def run(input_csv: str, out_dir: str, low_cut_fraction: float) -> None:
    # ------------------------------------------------------------------
    # Load per-residue mean log drifts
    # ------------------------------------------------------------------
    records = []
    with open(input_csv, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            records.append((int(row["residue"]),
                            int(row["count"]),
                            float(row["mean_log_drift"])))

    if not records:
        raise ValueError(f"No data found in {input_csv}")

    # Infer M from the maximum residue (all residues are odd, max < 2^M)
    max_residue = max(r for r, _, _ in records)
    M = max_residue.bit_length()   # smallest M such that 2^M > max_residue

    # Sort odd residues in ascending order; build the signal vector
    records.sort(key=lambda x: x[0])
    residues = [r for r, _, _ in records]
    values = [v for _, _, v in records]
    N_pts = len(values)   # number of odd residue classes with data = 2^(M-1)

    # ------------------------------------------------------------------
    # DFT
    # ------------------------------------------------------------------
    F = _compute_fft(values)
    # 1/N-normalised amplitudes (one-sided: index 0 to N_pts//2 inclusive)
    N_inv = 1.0 / N_pts
    half = N_pts // 2

    amplitudes = []
    phases = []
    for k in range(N_pts // 2 + 1):
        if _HAS_NUMPY:
            c = complex(F[k])
        else:
            c = F[k]
        amp = abs(c) * N_inv
        ph = math.atan2(c.imag, c.real)
        amplitudes.append(amp)
        phases.append(ph)

    # ------------------------------------------------------------------
    # Low-cut filter: discard modes 0 … floor(N_pts * low_cut_fraction)
    # Mode 0 (DC) is always excluded regardless of low_cut_fraction.
    # ------------------------------------------------------------------
    low_cut_idx = max(1, int(N_pts * low_cut_fraction))
    kept_indices = list(range(low_cut_idx, half + 1))

    if not kept_indices:
        raise ValueError("low_cut_fraction too large: no modes remain after filtering.")

    kept_amps = [amplitudes[k] for k in kept_indices]

    # ------------------------------------------------------------------
    # Dominant mode: rank 1 = highest amplitude among kept modes
    # ------------------------------------------------------------------
    dom_local = int(max(range(len(kept_amps)), key=lambda i: kept_amps[i]))
    dom_global = kept_indices[dom_local]

    dom_amp = amplitudes[dom_global]
    dom_freq = dom_global / N_pts          # cycles per residue-spacing

    # avg_rms_ratio: dominant / RMS of all other kept amplitudes
    others = [a for i, a in zip(kept_indices, kept_amps) if i != dom_global]
    if others:
        rms_others = math.sqrt(sum(a * a for a in others) / len(others))
        avg_rms_ratio = dom_amp / rms_others if rms_others > 0.0 else float("inf")
    else:
        avg_rms_ratio = float("inf")

    # Rank of dominant mode (always 1 by construction; reported for clarity)
    dominant_fourier_mode = 1

    # ------------------------------------------------------------------
    # Derive N from filename for output naming
    # ------------------------------------------------------------------
    base = os.path.basename(input_csv)
    m = re.search(r"c9_2_M(\d+)_N(\d+)", base)
    if m:
        M_str, N_str = m.group(1), m.group(2)
        stem = f"c9_2_M{M_str}_N{N_str}"
    else:
        stem = os.path.splitext(base)[0]

    os.makedirs(out_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Write fourier_modes CSV
    # ------------------------------------------------------------------
    modes_path = os.path.join(out_dir, f"{stem}_fourier_modes.csv")
    with open(modes_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["mode_index", "frequency", "amplitude", "phase_rad"])
        for k in kept_indices:
            writer.writerow([
                k,
                f"{k / N_pts:.8f}",
                f"{amplitudes[k]:.10f}",
                f"{phases[k]:.8f}",
            ])

    # ------------------------------------------------------------------
    # Write fourier JSON
    # ------------------------------------------------------------------
    fourier = {
        "stem": stem,
        "M": M,
        "n_residues_with_data": N_pts,
        "low_cut_fraction": low_cut_fraction,
        "low_cut_index": low_cut_idx,
        "n_kept_modes": len(kept_indices),
        "dominant_fourier_mode": dominant_fourier_mode,
        "dominant_mode_index": dom_global,
        "dominant_freq": round(dom_freq, 8),
        "dominant_amplitude": round(dom_amp, 8),
        "avg_rms_ratio": round(avg_rms_ratio, 3),
    }
    json_path = os.path.join(out_dir, f"{stem}_fourier.json")
    with open(json_path, "w") as fh:
        json.dump(fourier, fh, indent=2)

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print(f"[{stem}]  N_pts={N_pts}  low_cut={low_cut_idx}  "
          f"kept={len(kept_indices)} modes")
    print(f"  dominant_fourier_mode : {dominant_fourier_mode}  "
          f"(index {dom_global}, freq {dom_freq:.5f})")
    print(f"  dominant_amplitude    : {dom_amp:.6f}")
    print(f"  avg_rms_ratio         : {avg_rms_ratio:.3f}")
    print(f"  Written: {modes_path}")
    print(f"  Written: {json_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2 Fourier v2 — 2-adic Fourier analysis of per-residue "
                    "log-drift data."
    )
    parser.add_argument("--input", required=True, metavar="CSV",
                        help="Per-residue CSV from collatz_c9_2_sampling_option1.py")
    parser.add_argument("--out-dir", type=str, default="scripts/out",
                        metavar="DIR", help="Output directory (default: scripts/out)")
    parser.add_argument("--low-cut-fraction", type=float, default=0.125,
                        metavar="F",
                        help="Fraction of lowest frequencies to discard before "
                             "finding the dominant mode (default: 0.125)")
    args = parser.parse_args()
    run(args.input, args.out_dir, args.low_cut_fraction)


if __name__ == "__main__":
    main()
