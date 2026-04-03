"""
collatz_c9_2_sampling_option1.py  –  Option 1: exhaustive / random sampler
Produces: scripts/out/c9_2_M{M}_N{N}.csv
Columns  : n, xi, v2_xi, p_hat
  n      – seed integer
  xi     – T^*(n) value after stripping trailing 2s  (= n / 2^v2(n+1) after one 3n+1 step)
  v2_xi  – 2-adic valuation of xi
  p_hat  – empirical estimator (always 1.0 per sample; caller averages)
"""

import argparse
import csv
import math
import os
import random
import sys


# ---------------------------------------------------------------------------
# Collatz helpers
# ---------------------------------------------------------------------------

def v2(n: int) -> int:
    """2-adic valuation of n (n must be a positive integer)."""
    if n == 0:
        return 0
    k = 0
    while n % 2 == 0:
        n >>= 1
        k += 1
    return k


def collatz_step(n: int):
    """One full Collatz step: if odd apply 3n+1 then strip all 2s.
    Returns (xi, v2_xi) where xi is the odd part of 3n+1."""
    if n % 2 == 0:
        # even: just halve (keep going until odd)
        val = n
        while val % 2 == 0:
            val >>= 1
        return val, 0  # v2_xi of the odd result is 0
    # odd
    m = 3 * n + 1
    k = v2(m)
    xi = m >> k
    return xi, k


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="C9.2 Option-1 sampler: exhaustive / random window")
    p.add_argument("--M", type=int, required=True,
                   help="Dyadic scale: window = [2^M, 2^(M+1))")
    p.add_argument("--N", type=int, required=True,
                   help="Target number of samples to collect")
    p.add_argument("--window-size", type=int, default=None,
                   help="Override window size (default: 2^M)")
    p.add_argument("--mode", choices=["exhaustive", "random"], default="exhaustive",
                   help="exhaustive: iterate all odd n in window; random: draw uniformly")
    p.add_argument("--max-samples", type=int, default=None,
                   help="Hard cap on rows written (subsample if exhaustive yields more)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=str, default="scripts/out")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    random.seed(args.seed)

    M = args.M
    N = args.N
    window_start = 2 ** M
    window_end = window_start + (args.window_size if args.window_size else 2 ** M)

    os.makedirs(args.out_dir, exist_ok=True)
    out_csv = os.path.join(args.out_dir, f"c9_2_M{M}_N{N}.csv")

    rows = []

    if args.mode == "exhaustive":
        # iterate all odd integers in [window_start, window_end)
        # start at first odd number >= window_start
        start = window_start if window_start % 2 == 1 else window_start + 1
        for n in range(start, window_end, 2):
            xi, v2_xi = collatz_step(n)
            rows.append((n, xi, v2_xi, 1.0))
            if len(rows) >= N:
                break
    else:
        # random: draw N odd integers uniformly from the window
        lo = window_start
        hi = window_end - 1
        for _ in range(N):
            n = random.randint(lo, hi)
            if n % 2 == 0:
                n += 1
            if n >= window_end:
                n -= 2
            xi, v2_xi = collatz_step(n)
            rows.append((n, xi, v2_xi, 1.0))

    # optional subsample
    if args.max_samples is not None and len(rows) > args.max_samples:
        rows = random.sample(rows, args.max_samples)
        rows.sort(key=lambda r: r[0])

    with open(out_csv, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["n", "xi", "v2_xi", "p_hat"])
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows → {out_csv}")


if __name__ == "__main__":
    main()
