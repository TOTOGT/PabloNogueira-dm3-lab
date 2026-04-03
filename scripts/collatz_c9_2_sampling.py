#!/usr/bin/env python3
"""
Collatz C9.2 empirical sampling pipeline.

For each of N uniformly-sampled positive integers, computes Collatz
trajectory statistics grouped by dyadic residue class (n mod 2^M) and
by 2-adic valuation v2(n).  Produces a per-sample CSV and an aggregate
summary JSON suitable for downstream Fourier analysis.

Usage
-----
    python3 collatz_c9_2_sampling.py --N 100000 --M 12 --window-type dyadic --output out/

Output files (written to --output directory)
--------------------------------------------
    c9_2_M{M}_N{N}.csv        -- one row per sample
    c9_2_M{M}_N{N}_summary.json -- aggregate statistics

Columns in CSV
--------------
    n           : sampled integer
    residue     : n mod 2^M  (dyadic residue class)
    v2_xi       : 2-adic valuation of n
    stopping_time : Collatz steps to reach 1 (capped at max_steps)
    reached_1   : 1 if stopping_time < max_steps, else 0

Aggregate fields in summary JSON
---------------------------------
    mean_hat_p      : mean of per-bucket empirical hit rate
    l2_variance     : variance of hat_p values across filled buckets
    sparse_fraction : fraction of residue buckets with zero samples
    runtime         : wall-clock seconds
    per_v2_bucket   : per-residue {hat_p, count} mapping (first 256 entries)
"""

import argparse
import csv
import json
import os
import random
import time


# ---------------------------------------------------------------------------
# Collatz helpers
# ---------------------------------------------------------------------------

def v2(n: int) -> int:
    """Return the 2-adic valuation of n (largest k such that 2^k | n)."""
    if n <= 0:
        return 0
    k = 0
    while n & 1 == 0:
        n >>= 1
        k += 1
    return k


def collatz_stopping_time(n: int, max_steps: int) -> int:
    """Return the number of Collatz steps to reach 1, capped at max_steps."""
    steps = 0
    while n != 1 and steps < max_steps:
        if n & 1:
            n = 3 * n + 1
        else:
            n >>= 1
        steps += 1
    return steps


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collatz C9.2 empirical sampling"
    )
    parser.add_argument(
        "--N", type=int, default=10000,
        help="Number of samples (default: 10000)"
    )
    parser.add_argument(
        "--M", type=int, default=12,
        help="Window parameter: dyadic modulus = 2^M (default: 12)"
    )
    parser.add_argument(
        "--window-type", dest="window_type", default="dyadic",
        choices=["dyadic"],
        help="Window type (default: dyadic)"
    )
    parser.add_argument(
        "--output", default="scripts/out",
        help="Output directory (default: scripts/out)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    args = parser.parse_args()

    N = args.N
    M = args.M
    mod = 1 << M                       # 2^M
    max_steps = max(200, 20 * M)       # generous cap to ensure convergence

    os.makedirs(args.output, exist_ok=True)
    random.seed(args.seed)

    csv_path = os.path.join(args.output, f"c9_2_M{M}_N{N}.csv")
    summary_path = os.path.join(args.output, f"c9_2_M{M}_N{N}_summary.json")

    # Sample integers uniformly from [1, 2^(M+4)] to cover all residue classes
    upper = max(2 * mod, 1 << (M + 4))

    # Per-bucket accumulators
    bucket_count = [0] * mod
    bucket_hit = [0] * mod        # how many reached 1

    t0 = time.monotonic()

    rows = []
    for _ in range(N):
        n = random.randint(1, upper)
        residue = n & (mod - 1)       # n mod 2^M  (fast bitmask)
        v2_xi = v2(n)
        stopping = collatz_stopping_time(n, max_steps)
        reached = 1 if stopping < max_steps else 0

        rows.append({
            "n": n,
            "residue": residue,
            "v2_xi": v2_xi,
            "stopping_time": stopping,
            "reached_1": reached,
        })
        bucket_count[residue] += 1
        bucket_hit[residue] += reached

    runtime = time.monotonic() - t0

    # Aggregate statistics
    hat_p_vals = [
        bucket_hit[r] / bucket_count[r]
        for r in range(mod)
        if bucket_count[r] > 0
    ]
    filled = len(hat_p_vals)
    sparse_fraction = 1.0 - filled / mod if mod > 0 else 0.0

    if hat_p_vals:
        mean_hat_p = sum(hat_p_vals) / filled
        l2_variance = sum((x - mean_hat_p) ** 2 for x in hat_p_vals) / filled
    else:
        mean_hat_p = 0.0
        l2_variance = 0.0

    # per_v2_bucket: keyed by residue (capped at first 256 for readability)
    per_v2_bucket = {}
    cap = min(mod, 256)
    for r in range(cap):
        hp = (bucket_hit[r] / bucket_count[r]) if bucket_count[r] > 0 else None
        per_v2_bucket[str(r)] = {"hat_p": hp, "count": bucket_count[r]}

    # Write CSV
    fieldnames = ["n", "residue", "v2_xi", "stopping_time", "reached_1"]
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write summary JSON
    summary = {
        "M": M,
        "N": N,
        "window_type": args.window_type,
        "seed": args.seed,
        "mod": mod,
        "upper_bound": upper,
        "max_steps": max_steps,
        "mean_hat_p": mean_hat_p,
        "l2_variance": l2_variance,
        "sparse_fraction": sparse_fraction,
        "filled_buckets": filled,
        "runtime": runtime,
        "per_v2_bucket": per_v2_bucket,
    }
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2)

    print(
        f"M={M} N={N} "
        f"mean_hat_p={mean_hat_p:.6f} "
        f"l2_variance={l2_variance:.6f} "
        f"sparse_fraction={sparse_fraction:.4f} "
        f"runtime={runtime:.2f}s"
    )
    print(f"CSV    : {csv_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
