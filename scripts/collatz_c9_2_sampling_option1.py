"""C9.2 Conditional Sampler – Option 1 (dyadic window, stdlib-only).

Option 1 definition (Policy A):
  Window W_M = { n odd : 2^(M-1) <= n < 2^M }
  For each odd n in W_M, record
      v2      = v_2(3n+1)      (2-adic valuation of 3n+1)
      log_ratio = log( T(n)/n )  where T(n) = (3n+1)/2^v2 is the odd-to-odd step.

Modes:
  exhaustive  – iterate all odd n in W_M in ascending order, stop after
                min(max_samples, N) rows.  (window_size is ignored in this mode)
  random      – draw N odd integers uniformly at random from W_M (with seed).

Output
  <out_dir>/c9_2_M<M>_N<N>.csv   columns: n, v2, log_ratio
"""

import argparse
import csv
import math
import os
import random


# ---------------------------------------------------------------------------
# Collatz helpers
# ---------------------------------------------------------------------------

def v2_of(k: int) -> int:
    """2-adic valuation of k (number of trailing zero bits)."""
    if k == 0:
        return 0
    count = 0
    while k & 1 == 0:
        k >>= 1
        count += 1
    return count


def T_odd(n: int) -> int:
    """Fully-reduced Syracuse (odd-to-odd) step: T(n) = (3n+1)/2^v2(3n+1)."""
    m = 3 * n + 1
    while m & 1 == 0:
        m >>= 1
    return m


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_exhaustive(lo: int, hi: int, limit: int):
    """Yield (n, v2, log_ratio) for odd n in [lo, hi), up to `limit` rows."""
    n = lo | 1  # first odd number >= lo
    count = 0
    while n < hi and count < limit:
        val_v2 = v2_of(3 * n + 1)
        t = T_odd(n)
        log_ratio = math.log(t / n)
        yield n, val_v2, log_ratio
        n += 2
        count += 1


def sample_random(lo: int, hi: int, limit: int):
    """Yield (n, v2, log_ratio) for `limit` random odd n in [lo, hi)."""
    # odd numbers in [lo, hi): lo|1, lo|1+2, ...
    first_odd = lo | 1
    last_odd = (hi - 1) | 1
    if last_odd >= hi:
        last_odd -= 2
    pool_size = (last_odd - first_odd) // 2 + 1
    limit = min(limit, pool_size)
    # reservoir / Fisher-Yates for large pools
    indices = random.sample(range(pool_size), limit)
    indices.sort()  # preserve ascending order for reproducibility
    for idx in indices:
        n = first_odd + 2 * idx
        val_v2 = v2_of(3 * n + 1)
        t = T_odd(n)
        log_ratio = math.log(t / n)
        yield n, val_v2, log_ratio


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="C9.2 Sampler – Option 1 dyadic window (stdlib-only)"
    )
    parser.add_argument("--M", type=int, required=True,
                        help="Window exponent: sample from odd n in [2^(M-1), 2^M)")
    parser.add_argument("--N", type=int, required=True,
                        help="Target number of rows in output CSV")
    parser.add_argument("--window-size", type=int, default=None,
                        help="(unused for Option 1; kept for interface compatibility)")
    parser.add_argument("--mode", choices=["exhaustive", "random"], default="exhaustive",
                        help="Iteration strategy (default: exhaustive)")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Hard cap on samples collected (defaults to --N)")
    parser.add_argument("--seed", type=int, default=None,
                        help="RNG seed for reproducibility")
    parser.add_argument("--out-dir", type=str, default=".",
                        help="Directory for output CSV")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    limit = args.max_samples if args.max_samples is not None else args.N
    lo = 1 << (args.M - 1)   # 2^(M-1)
    hi = 1 << args.M          # 2^M

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"c9_2_M{args.M}_N{args.N}.csv")

    if args.mode == "exhaustive":
        rows = sample_exhaustive(lo, hi, limit)
    else:
        rows = sample_random(lo, hi, limit)

    count = 0
    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["n", "v2", "log_ratio"])
        for n, val_v2, log_ratio in rows:
            writer.writerow([n, val_v2, f"{log_ratio:.10f}"])
            count += 1

    print(f"[sampler] M={args.M}  N_requested={args.N}  rows_written={count}")
    print(f"[sampler] output → {out_path}")


if __name__ == "__main__":
    main()
