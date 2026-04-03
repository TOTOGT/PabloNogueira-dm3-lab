"""
C9.2 Option 1 sampler: event_A = odd(n), event_B = T(n) < n, weight = 1.0.

Exhaustively enumerates all odd n in the window [N, 2N) and records the
per-residue (mod 2^M) mean log-drift log(T(n)/n), where T is the
fully-reduced odd-to-odd Syracuse step T(n) = (3n+1) / 2^v₂(3n+1).

Outputs
-------
scripts/out/c9_2_M{M}_N{N}.csv
    Columns: residue, count, mean_log_drift
    One row per odd residue class that has at least one observation.

scripts/out/c9_2_M{M}_N{N}_summary.json
    Aggregate statistics: global mean log drift, l2_variance, sparsity
    metrics, etc.

Golden-run command (M = 12, 14, 16; N = 100 000):
    python3 scripts/collatz_c9_2_sampling_option1.py --M 12 --N 100000
"""

import argparse
import csv
import json
import math
import os


# ---------------------------------------------------------------------------
# Syracuse / Collatz map helpers
# ---------------------------------------------------------------------------

def v2(k: int) -> int:
    """2-adic valuation of positive integer k."""
    v = 0
    while k & 1 == 0:
        k >>= 1
        v += 1
    return v


def collatz_shortcut(n: int) -> int:
    """
    Fully-reduced odd-to-odd Syracuse step.

    Returns (3n+1) / 2^v₂(3n+1), which is always odd.
    Defined only for odd n > 0.
    """
    m = 3 * n + 1
    return m >> v2(m)


# ---------------------------------------------------------------------------
# Sampler
# ---------------------------------------------------------------------------

def run(M: int, N: int, mode: str, seed: int, out_dir: str) -> None:
    modulus = 1 << M          # 2^M  (total residue classes mod 2^M)
    mask = modulus - 1
    window_start = N
    window_end = 2 * N

    os.makedirs(out_dir, exist_ok=True)

    # Per-residue accumulators (only odd residues will be populated)
    res_sum = [0.0] * modulus
    res_count = [0] * modulus

    global_sum = 0.0
    global_sq_sum = 0.0
    global_count = 0

    # Exhaustive: iterate every odd n in [window_start, window_end)
    # First odd number >= window_start:
    start_odd = window_start | 1
    for n in range(start_odd, window_end, 2):
        tn = collatz_shortcut(n)
        ld = math.log(tn / n)
        r = n & mask
        res_sum[r] += ld
        res_count[r] += 1
        global_sum += ld
        global_sq_sum += ld * ld
        global_count += 1

    # Global statistics
    global_mean = global_sum / global_count
    # l2_variance: empirical variance of individual log-drift observations
    l2_variance = global_sq_sum / global_count - global_mean ** 2

    # Per-residue means
    residues_with_data = [r for r in range(modulus) if res_count[r] > 0]
    n_with_data = len(residues_with_data)
    res_mean = {r: res_sum[r] / res_count[r] for r in residues_with_data}

    # Sparsity: fraction of residue classes whose mean deviates from
    # the global mean by more than sparse_threshold
    sparse_threshold = 0.05
    sparse_bad = sum(
        1 for r in residues_with_data
        if abs(res_mean[r] - global_mean) > sparse_threshold
    )

    # -------------------------------------------------------------------
    # Write CSV
    # -------------------------------------------------------------------
    csv_path = os.path.join(out_dir, f"c9_2_M{M}_N{N}.csv")
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["residue", "count", "mean_log_drift"])
        for r in residues_with_data:
            writer.writerow([r, res_count[r], f"{res_mean[r]:.10f}"])

    # -------------------------------------------------------------------
    # Write summary JSON
    # -------------------------------------------------------------------
    summary = {
        "M": M,
        "N": N,
        "window_end": window_end,
        "window_size": N,
        "mode": mode,
        "seed": seed,
        "n_residues_total": modulus,
        "n_residues_with_data": n_with_data,
        "global_mean_log_drift": round(global_mean, 6),
        "l2_variance": round(l2_variance, 3),
        "sparse_threshold": sparse_threshold,
        "sparse_bad": sparse_bad,
        "sparse_total": n_with_data,
        "sparse_fraction": round(sparse_bad / n_with_data, 3),
    }
    json_path = os.path.join(out_dir, f"c9_2_M{M}_N{N}_summary.json")
    with open(json_path, "w") as fh:
        json.dump(summary, fh, indent=2)

    # -------------------------------------------------------------------
    # Console summary
    # -------------------------------------------------------------------
    print(f"[M={M}] window [{window_start}, {window_end})  "
          f"odd samples: {global_count}")
    print(f"  global_mean_log_drift : {global_mean:.6f}  "
          f"(log(3/4) = {math.log(3/4):.6f})")
    print(f"  l2_variance           : {l2_variance:.3f}")
    print(f"  n_residues_with_data  : {n_with_data}")
    print(f"  sparse_fraction       : {sparse_bad / n_with_data:.3f}")
    print(f"  Written: {csv_path}")
    print(f"  Written: {json_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2 Option 1 sampler — per-residue log-drift statistics."
    )
    parser.add_argument("--M", type=int, required=True,
                        help="2-adic depth: modulus = 2^M")
    parser.add_argument("--N", type=int, required=True,
                        help="Window size; window = [N, 2N)")
    parser.add_argument("--out-dir", type=str, default="scripts/out",
                        metavar="DIR", help="Output directory (default: scripts/out)")
    parser.add_argument("--seed", type=int, default=42,
                        help="RNG seed recorded in summary (default: 42)")
    parser.add_argument("--mode", type=str, default="exhaustive",
                        choices=["exhaustive"],
                        help="Sampling mode (default: exhaustive)")
    args = parser.parse_args()
    run(args.M, args.N, args.mode, args.seed, args.out_dir)


if __name__ == "__main__":
    main()
