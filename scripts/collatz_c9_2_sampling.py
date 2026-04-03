#!/usr/bin/env python3
"""
C9.2 Collatz per-class sampler (stdlib only).

Observable defaults:
  event_A = 1 if n is odd       (n falls in odd residue class)
  event_B = 1 if T(n) < n       (equivalently: n is even, so T(n) = n/2)

Window types:
  dyadic  -- class k = floor(log2(n)) % M
  residue -- class k = n % M

Output files (written to --output directory):
  c9_2_M{M}_N{N}.csv            one row per sampled integer
  c9_2_M{M}_N{N}_summary.json  per-class + global summary metrics

Usage:
  python3 collatz_c9_2_sampling.py --N 100000 --M 12 --window-type dyadic \\
      --output scripts/out --seed 1
"""

import argparse
import csv
import json
import math
import os
import random
import time


def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def collatz_stopping_time(n, max_steps=10000):
    """Return number of steps until n reaches 1 (capped at max_steps)."""
    steps = 0
    while n != 1 and steps < max_steps:
        n = collatz_step(n)
        steps += 1
    return steps


def dyadic_class(n, M):
    """floor(log2(n)) % M — assigns n to a bit-length residue class."""
    if n <= 0:
        return 0
    return int(math.log2(n)) % M


def residue_class(n, M):
    return n % M


def main():
    parser = argparse.ArgumentParser(description="C9.2 Collatz per-class sampler")
    parser.add_argument("--N", type=int, default=100000, help="Number of samples")
    parser.add_argument("--M", type=int, default=12, help="Number of classes")
    parser.add_argument(
        "--window-type",
        dest="window_type",
        choices=["dyadic", "residue"],
        default="dyadic",
        help="Class assignment scheme",
    )
    parser.add_argument("--output", type=str, default="scripts/out", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    N, M = args.N, args.M
    os.makedirs(args.output, exist_ok=True)
    random.seed(args.seed)

    # Sample from a range wide enough to populate all M dyadic levels.
    # For dyadic: bit-lengths 0..M-1 live in [1, 2^M); extend to [1, 2^(M+4))
    # so higher bit-length groups are also well-represented via the % M wrap.
    # Include 1 so class-0 statistics are not skewed by its exclusion.
    upper = 2 ** (M + 4)
    samples = [random.randint(1, upper) for _ in range(N)]

    t0 = time.time()

    csv_path = os.path.join(args.output, f"c9_2_M{M}_N{N}.csv")

    # Per-class accumulators
    class_counts = [0] * M
    class_A = [0] * M      # event_A: n is odd
    class_B = [0] * M      # event_B: T(n) < n  (n is even)
    stopping_times = []

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "class", "event_A", "event_B", "stopping_time"])
        for n in samples:
            c = dyadic_class(n, M) if args.window_type == "dyadic" else residue_class(n, M)
            ev_A = 1 if n % 2 == 1 else 0
            next_n = collatz_step(n)
            ev_B = 1 if next_n < n else 0
            st = collatz_stopping_time(n)

            class_counts[c] += 1
            class_A[c] += ev_A
            class_B[c] += ev_B
            stopping_times.append(st)

            writer.writerow([n, c, ev_A, ev_B, st])

    runtime = time.time() - t0

    # Per-class estimated P(A)
    hat_p = [
        class_A[c] / class_counts[c] if class_counts[c] > 0 else 0.0
        for c in range(M)
    ]

    mean_hat_p = sum(hat_p) / M
    l2_variance = sum((p - mean_hat_p) ** 2 for p in hat_p) / M
    sparse_fraction = sum(1 for cnt in class_counts if cnt == 0) / M
    mean_stopping_time = sum(stopping_times) / N

    summary = {
        "M": M,
        "N": N,
        "window_type": args.window_type,
        "seed": args.seed,
        "mean_hat_p": mean_hat_p,
        "l2_variance": l2_variance,
        "sparse_fraction": sparse_fraction,
        "mean_stopping_time": mean_stopping_time,
        "runtime": round(runtime, 4),
        "per_class": [
            {
                "class": c,
                "count": class_counts[c],
                "hat_p": hat_p[c],
                "event_B_fraction": (
                    class_B[c] / class_counts[c] if class_counts[c] > 0 else 0.0
                ),
            }
            for c in range(M)
        ],
    }

    summary_path = os.path.join(args.output, f"c9_2_M{M}_N{N}_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {csv_path}")
    print(f"Wrote {summary_path}")
    print(
        f"M={M} N={N} mean_hat_p={mean_hat_p:.6f} l2_variance={l2_variance:.6e} "
        f"sparse_fraction={sparse_fraction:.4f} runtime={runtime:.2f}s"
    )


if __name__ == "__main__":
    main()
