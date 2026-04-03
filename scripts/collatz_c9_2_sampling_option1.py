#!/usr/bin/env python3
"""
collatz_c9_2_sampling_option1.py
Sampler for C9.2 observable — Option 1 semantics locked.

Option 1 definition:
  observable[i] = 1  if the i-th iterate n_i is odd (event A holds)
  observable[i] = 0  otherwise

Iterates the Collatz map T(n) = n/2 (even) or (3n+1)/2 (odd) for N steps
starting from a seed drawn uniformly from [1, 2^M - 1] (odd numbers only).

Outputs:
  <out-dir>/c9_2_M{M}_N{N}.csv  — columns: step, n, observable
"""

import argparse
import csv
import random
from pathlib import Path


def collatz_step(n: int) -> int:
    """Single step of the accelerated Collatz map."""
    if n % 2 == 1:
        return (3 * n + 1) // 2
    return n // 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--M", type=int, required=True,
                        help="Log2 of the starting range (seed drawn from [1, 2^M - 1] odd)")
    parser.add_argument("--N", type=int, required=True,
                        help="Number of iterates to record")
    parser.add_argument("--out-dir", type=str, required=True,
                        help="Output directory")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Draw an odd starting value in [1, 2^M - 1]
    upper = (1 << args.M) - 1
    candidates = list(range(1, upper + 1, 2))
    n = random.choice(candidates)

    out_path = out_dir / f"c9_2_M{args.M}_N{args.N}.csv"
    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["step", "n", "observable"])
        for step in range(args.N):
            # Option 1: observable = 1 iff current n is odd
            obs = 1 if n % 2 == 1 else 0
            writer.writerow([step, n, obs])
            n = collatz_step(n)

    print(f"Sampler (Option 1) complete -> {out_path}")


if __name__ == "__main__":
    main()
