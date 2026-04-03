"""
C9.2 Fourier Analysis v2: DFT of per-residue mean log-drift hat_p[a].

Reads the CSV produced by collatz_c9_2_sampling_option1.py, computes the
per-residue mean log-drift hat_p[a] for each odd residue a mod 2^M, then
computes the (real) Discrete Fourier Transform of the hat_p vector.

Sparsity baseline: **A (relative to mean drift)**
  A coefficient is considered sparse if
      abs(hat_p[a] - mean_hat_p) >= threshold
  where threshold = std(hat_p).

Outputs (in --out-dir):
  c9_2_M{M}_N{N}_fourier.json  -- top-k DFT magnitudes + summary metrics

Summary metrics reported:
  M, N, global_mean_log_drift, mean_hat_p, l2_variance_empirical,
  avg_rms_ratio, sparse_fraction
"""

import argparse
import csv
import json
import math
import os


# ---------------------------------------------------------------------------
# DFT over Z/n (pure Python, no numpy dependency)
# ---------------------------------------------------------------------------

def dft_real(x: list[float]) -> list[complex]:
    """Compute DFT of a real sequence x of length n."""
    n = len(x)
    result = []
    tau = 2.0 * math.pi / n
    for k in range(n):
        re = sum(x[j] * math.cos(tau * k * j) for j in range(n))
        im = sum(-x[j] * math.sin(tau * k * j) for j in range(n))
        result.append(complex(re, im))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2 Fourier v2: DFT of per-residue drift, sparse baseline A."
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Path to the CSV file produced by the sampler")
    parser.add_argument("--out-dir", type=str, default="scripts/out",
                        help="Directory to write output files (default: scripts/out)")
    parser.add_argument("--top-k", type=int, default=20,
                        help="Number of top DFT magnitudes to include in output (default: 20)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Read CSV and accumulate per-residue statistics
    # -----------------------------------------------------------------------
    residue_logs: dict[int, list[float]] = {}
    total_samples = 0
    global_sum = 0.0

    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a = int(row["residue"])
            ld = float(row["log_drift"])
            residue_logs.setdefault(a, []).append(ld)
            global_sum += ld
            total_samples += 1

    if total_samples == 0:
        raise ValueError("CSV file contains no data rows.")

    global_mean_log_drift = global_sum / total_samples

    # -----------------------------------------------------------------------
    # Compute hat_p[a] = per-residue mean log-drift
    # -----------------------------------------------------------------------
    residues = sorted(residue_logs.keys())
    hat_p: dict[int, float] = {
        a: sum(residue_logs[a]) / len(residue_logs[a]) for a in residues
    }

    n_res = len(residues)
    mean_hat_p = sum(hat_p.values()) / n_res
    l2_variance_empirical = sum((hat_p[a] - mean_hat_p) ** 2 for a in residues) / n_res
    std_hat_p = math.sqrt(l2_variance_empirical)

    # -----------------------------------------------------------------------
    # Sparse fraction (baseline A): relative to mean drift
    # threshold = std(hat_p)
    # -----------------------------------------------------------------------
    threshold = std_hat_p
    n_sparse = sum(1 for a in residues if abs(hat_p[a] - mean_hat_p) >= threshold)
    sparse_fraction = n_sparse / n_res if n_res > 0 else float("nan")

    # -----------------------------------------------------------------------
    # DFT of hat_p vector (ordered by sorted residue index)
    # -----------------------------------------------------------------------
    hat_p_vec = [hat_p[a] for a in residues]
    dft_coeffs = dft_real(hat_p_vec)

    magnitudes = [abs(c) for c in dft_coeffs]

    # avg_rms_ratio: RMS of non-DC modes / |DC mode|
    dc_mag = magnitudes[0]
    non_dc_mags = magnitudes[1:]
    rms_non_dc = math.sqrt(sum(m ** 2 for m in non_dc_mags) / len(non_dc_mags)) if non_dc_mags else 0.0
    avg_rms_ratio = rms_non_dc / dc_mag if dc_mag > 0 else float("nan")

    # Top-k DFT entries by magnitude
    indexed = sorted(enumerate(magnitudes), key=lambda x: x[1], reverse=True)
    top_k = [
        {"k": idx, "magnitude": mag, "re": dft_coeffs[idx].real, "im": dft_coeffs[idx].imag}
        for idx, mag in indexed[: args.top_k]
    ]

    # -----------------------------------------------------------------------
    # Derive M, N from filename (best-effort)
    # -----------------------------------------------------------------------
    basename = os.path.basename(args.input)   # e.g. c9_2_M8_N10000.csv
    M_val: int | None = None
    N_val: int | None = None
    try:
        name_no_ext = os.path.splitext(basename)[0]
        parts = name_no_ext.split("_")
        for p in parts:
            if p.startswith("M") and p[1:].isdigit():
                M_val = int(p[1:])
            elif p.startswith("N") and p[1:].isdigit():
                N_val = int(p[1:])
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # Build output JSON
    # -----------------------------------------------------------------------
    output = {
        "M": M_val,
        "N": N_val,
        "input_file": args.input,
        "total_samples": total_samples,
        "num_odd_residues": n_res,
        "sparse_baseline": "A",
        "sparse_threshold": threshold,
        "global_mean_log_drift": global_mean_log_drift,
        "mean_hat_p": mean_hat_p,
        "l2_variance_empirical": l2_variance_empirical,
        "std_hat_p": std_hat_p,
        "avg_rms_ratio": avg_rms_ratio,
        "sparse_fraction": sparse_fraction,
        "n_sparse": n_sparse,
        "dft_dc_magnitude": dc_mag,
        "dft_rms_non_dc": rms_non_dc,
        f"top_{args.top_k}_dft": top_k,
        "hat_p": {str(a): hat_p[a] for a in residues},
    }

    # Determine output filename from input filename
    out_name = os.path.splitext(basename)[0] + "_fourier.json"
    out_path = os.path.join(args.out_dir, out_name)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written: {out_path}")
    print(f"  global_mean_log_drift : {global_mean_log_drift:.6f}")
    print(f"  mean_hat_p            : {mean_hat_p:.6f}")
    print(f"  l2_variance_empirical : {l2_variance_empirical:.8f}")
    print(f"  avg_rms_ratio         : {avg_rms_ratio:.6f}")
    print(f"  sparse_fraction (A)   : {sparse_fraction:.4f}  (threshold={threshold:.6f})")


if __name__ == "__main__":
    main()
