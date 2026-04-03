#!/usr/bin/env python3
"""
scripts/collatz_c9_2_sampling.py

Stdlib-only Collatz sampling script for C9.2 empirical pipeline.

Purpose:
  - Compute per-class conditional statistics for Collatz odd-step behavior
    conditioned on odd inputs (event_A = n odd).
  - Output CSV per-class rows and a JSON summary.

Usage:
  python3 scripts/collatz_c9_2_sampling.py --N 100000 --M 16 --window-type dyadic --output scripts/out

Outputs:
  - {output}/c9_2_M{M}_N{N}.csv
  - {output}/c9_2_M{M}_N{N}_summary.json

Notes:
  - Implement different event logic by editing event_A / event_B below.
  - Do NOT commit output files; attach them to Issue C9.2 #3.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
from collections import defaultdict
from statistics import mean

# ---------- USER: adjust these two functions if you want a different observable ----------
def event_A(n: int) -> bool:
    """
    Conditioning event A(n): default = n is odd (Collatz odd-step).
    Change this to implement a different conditioning.
    """
    return (n & 1) == 1


def collatz_one_step_image(n: int) -> int:
    """
    Compute the Collatz one-step image T(n):
      - if n is even: T(n) = n // 2
      - if n is odd:  T(n) = (3n + 1) // 2^{v2(3n+1)}  (i.e., divide out all factors of 2)
    Returns the integer image after applying the odd-step normalization.
    """
    if (n & 1) == 0:
        return n // 2
    x = 3 * n + 1
    # divide out factors of 2
    while (x & 1) == 0:
        x >>= 1
    return x


def event_B(n: int) -> bool:
    """
    Target event B(n): default = one-step contraction, i.e., T(n) < n.
    Change this to a different target if desired.
    """
    Tn = collatz_one_step_image(n)
    return Tn < n
# -------------------------------------------------------------------------

def weight(n: int) -> float:
    """Optional weight function; default is uniform."""
    return 1.0

def enumerate_window(window_type: str, N: int, start: int | None = None, end: int | None = None):
    if window_type == "dyadic":
        start = N
        end = 2 * N
    elif window_type == "range":
        if start is None or end is None:
            raise ValueError("range requires --start and --end")
    else:
        raise ValueError("unknown window_type")

    assert start is not None
    assert end is not None

    n = start
    while n <= end:
        yield n
        n += 1

def compute_per_class(
    N: int,
    M: int,
    window_type: str,
    start: int | None = None,
    end: int | None = None,
    sample_rate: float = 1.0,
):
    mod = 1 << M
    counts_A = defaultdict(float)
    counts_A_and_B = defaultdict(float)
    counts_raw_A = defaultdict(int)
    counts_raw_A_and_B = defaultdict(int)
    total_weight = 0.0
    total_seen = 0

    for n in enumerate_window(window_type, N, start, end):
        if sample_rate < 1.0 and random.random() > sample_rate:
            continue

        total_seen += 1
        total_weight += weight(n)
        a = n % mod

        if event_A(n):
            w = weight(n)
            counts_A[a] += w
            counts_raw_A[a] += 1

            if event_B(n):
                counts_A_and_B[a] += w
                counts_raw_A_and_B[a] += 1

    results = []
    for a in sorted(counts_A.keys()):
        ca = counts_A[a]
        cab = counts_A_and_B.get(a, 0.0)
        hat_p = (cab / ca) if ca > 0 else None
        results.append((a, ca, cab, hat_p, counts_raw_A.get(a, 0), counts_raw_A_and_B.get(a, 0)))

    return results, total_weight, total_seen

def compute_L2_variance(results):
    vals = [r[3] for r in results if r[3] is not None]
    if not vals:
        return None
    m = mean(vals)
    var = sum((x - m) ** 2 for x in vals) / len(vals)
    return var, m, len(vals)

def compute_sparse_fraction(results, threshold: float = 0.05):
    total = 0
    bad = 0
    for (_, _, _, hat_p, _, _) in results:
        if hat_p is None:
            continue
        total += 1
        if abs(hat_p - 0.5) > threshold:
            bad += 1
    return (bad / total) if total > 0 else None, bad, total

def main() -> int:
    parser = argparse.ArgumentParser(description="Collatz C9.2 sampling: per-class conditional probabilities")
    parser.add_argument("--N", type=int, default=100000, help="base N for window (dyadic uses [N,2N])")
    parser.add_argument("--M", type=int, default=16, help="modulus power M (mod 2^M)")
    parser.add_argument("--window-type", choices=["dyadic", "range"], default="dyadic")
    parser.add_argument("--start", type=int, default=None, help="start for range window")
    parser.add_argument("--end", type=int, default=None, help="end for range window")
    parser.add_argument("--output", type=str, default="scripts/out", help="output directory")
    parser.add_argument("--sample-rate", type=float, default=1.0, help="subsampling rate in (0,1]")
    parser.add_argument("--threshold", type=float, default=0.05, help="sparse threshold")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed (for subsampling)")
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.output, exist_ok=True)

    results, total_weight, total_seen = compute_per_class(args.N, args.M, args.window_type, args.start, args.end, args.sample_rate)
    mod = 1 << args.M

    base = f"c9_2_M{args.M}_N{args.N}"
    csv_path = os.path.join(args.output, f"{base}.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class", "weighted_count_A", "weighted_count_A_and_B", "hat_p", "raw_count_A", "raw_count_A_and_B"])
        for row in results:
            w.writerow(row)

    l2 = compute_L2_variance(results)
    sparse_frac, bad, total = compute_sparse_fraction(results, threshold=args.threshold)

    summary = {
        "N": args.N,
        "M": args.M,
        "window_type": args.window_type,
        "total_weight": total_weight,
        "total_seen": total_seen,
        "l2_variance": l2[0] if l2 else None,
        "l2_mean_hat_p": l2[1] if l2 else None,
        "num_classes": l2[2] if l2 else 0,
        "sparse_fraction": sparse_frac,
        "sparse_bad": bad,
        "sparse_total": total,
        "sample_rate": args.sample_rate,
        "seed": args.seed,
        "notes": "event_A = odd n; event_B = one-step contraction T(n) < n; change functions in script to alter."
    }

    json_path = os.path.join(args.output, f"{base}_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("Wrote CSV:", csv_path)
    print("Wrote summary JSON:", json_path)
    print("Summary:", summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
