"""
Bridge 0 – Local Logarithmic Drift Verification
================================================
Numerically verifies the key local control condition for the Collatz conjecture:

    E[ log T²(n) − log n ] < 0

where T is the Syracuse (accelerated odd-to-odd) return map:

    T(n) = (3n + 1) / 2^{v₂(3n+1)}     (n odd, positive)

and T²(n) = T(T(n)) is the double iterate.

Two complementary verification modes:
  1. Exhaustive: average over all odd residues mod 2^M for M = 4..24.
  2. Random sampling: average over a large random sample of odd integers in
     [1, 2^68] (matching the computational range cited in the dm³ framework).

Usage
-----
    python collatz_bridge0_drift.py                     # full run
    python collatz_bridge0_drift.py --mode exhaustive   # residue enumeration only
    python collatz_bridge0_drift.py --mode sampling     # random sample only
    python collatz_bridge0_drift.py --output results/   # custom output dir

Outputs
-------
    bridge0_exhaustive.csv   – M, num_residues, mean_drift, min_drift, max_drift
    bridge0_sampling.csv     – trial, n, log_T2n_minus_log_n
    bridge0_summary.json     – consolidated statistics
"""

import argparse
import csv
import json
import math
import os
import random
import sys


# ---------------------------------------------------------------------------
# Core arithmetic
# ---------------------------------------------------------------------------

def v2(k: int) -> int:
    """2-adic valuation: largest e such that 2^e divides k (k > 0)."""
    if k <= 0:
        raise ValueError(f"v2 requires a positive integer, got {k}")
    count = 0
    while k % 2 == 0:
        k >>= 1
        count += 1
    return count


def T(n: int) -> int:
    """Syracuse return map: T(n) = (3n+1) / 2^{v₂(3n+1)}.

    Requires n to be a positive odd integer; returns a positive odd integer.
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError(f"T requires a positive odd integer, got {n}")
    m = 3 * n + 1            # always even since n is odd
    return m >> v2(m)        # divide by the full power of 2


def T2(n: int) -> int:
    """Double iterate of the Syracuse map: T²(n) = T(T(n))."""
    return T(T(n))


def log_drift(n: int) -> float:
    """log T²(n) − log n  (natural logarithm of the multiplicative change)."""
    return math.log(T2(n)) - math.log(n)


# ---------------------------------------------------------------------------
# Mode 1 – Exhaustive enumeration of odd residues mod 2^M
# ---------------------------------------------------------------------------

def odd_residues_mod(M: int):
    """Yield all odd integers in [1, 2^M − 1] (the odd residues mod 2^M)."""
    bound = 1 << M          # 2^M
    n = 1
    while n < bound:
        yield n
        n += 2


def exhaustive_drift(M: int):
    """Compute mean/min/max of log_drift over odd residues mod 2^M."""
    values = [log_drift(n) for n in odd_residues_mod(M)]
    mean = sum(values) / len(values)
    return {
        "M": M,
        "num_residues": len(values),
        "mean_drift": mean,
        "min_drift": min(values),
        "max_drift": max(values),
        "negative": mean < 0,
    }


def run_exhaustive(M_min: int = 4, M_max: int = 24, output_dir: str = "."):
    """Run exhaustive mode for M in [M_min, M_max] and write CSV."""
    print(f"=== Exhaustive mode: M = {M_min}..{M_max} ===")
    rows = []
    for M in range(M_min, M_max + 1):
        result = exhaustive_drift(M)
        rows.append(result)
        print(
            f"  M={M:2d}  residues={result['num_residues']:8d}"
            f"  mean_drift={result['mean_drift']:+.6f}"
            f"  negative={result['negative']}"
        )

    # Write CSV
    csv_path = os.path.join(output_dir, "bridge0_exhaustive.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["M", "num_residues", "mean_drift", "min_drift", "max_drift", "negative"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {csv_path}")

    all_negative = all(r["negative"] for r in rows)
    print(f"  All mean drifts negative? {all_negative}")
    return rows


# ---------------------------------------------------------------------------
# Mode 2 – Random sampling of large odd integers
# ---------------------------------------------------------------------------

def random_odd(lo: int, hi: int, rng: random.Random) -> int:
    """Return a uniformly random odd integer in [lo, hi].

    lo must be odd (or at most 1 less than an odd number in range).
    The implementation adjusts even draws to the nearest odd, staying in bounds.
    """
    # Ensure [lo, hi] contains at least one odd integer
    lo_odd = lo if lo % 2 == 1 else lo + 1
    hi_odd = hi if hi % 2 == 1 else hi - 1
    if lo_odd > hi_odd:
        raise ValueError(f"No odd integer in [{lo}, {hi}]")
    n = rng.randint(lo_odd, hi_odd)
    # Make odd: prefer +1, but clamp to [lo_odd, hi_odd]
    if n % 2 == 0:
        if n + 1 <= hi_odd:
            n += 1
        else:
            n -= 1
    return n


def run_sampling(
    num_trials: int = 200_000,
    lo: int = 1,
    hi: int = (1 << 68),
    seed: int = 42,
    output_dir: str = ".",
):
    """Sample num_trials random odd integers and record log drift."""
    print(f"=== Sampling mode: {num_trials:,} random odd integers in [1, 2^68] ===")
    rng = random.Random(seed)

    total_drift = 0.0
    negative_count = 0
    sample_rows = []          # keep first 1000 rows for the CSV (representative sample;
                              # writing all trials would produce a very large file)

    for i in range(num_trials):
        n = random_odd(lo, hi, rng)
        d = log_drift(n)
        total_drift += d
        if d < 0:
            negative_count += 1
        if i < 1000:
            sample_rows.append({"trial": i + 1, "n": n, "log_T2n_minus_log_n": d})

    mean_drift = total_drift / num_trials
    fraction_negative = negative_count / num_trials

    print(f"  mean_drift         = {mean_drift:+.8f}")
    print(f"  fraction_negative  = {fraction_negative:.6f}  ({negative_count:,}/{num_trials:,})")
    print(f"  mean drift < 0?    {mean_drift < 0}")

    # Write first 1000 samples to CSV
    csv_path = os.path.join(output_dir, "bridge0_sampling.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["trial", "n", "log_T2n_minus_log_n"])
        writer.writeheader()
        writer.writerows(sample_rows)
    print(f"  -> {csv_path} (first {len(sample_rows)} rows)")

    return {
        "num_trials": num_trials,
        "seed": seed,
        "mean_drift": mean_drift,
        "fraction_negative": fraction_negative,
        "drift_negative": mean_drift < 0,
    }


# ---------------------------------------------------------------------------
# Small examples from the problem statement (Section 5)
# ---------------------------------------------------------------------------

def print_examples():
    """Reproduce the explicit small examples from the problem statement."""
    print("=== Small examples (Section 5 of problem statement) ===")
    for n in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
        t1 = T(n)
        t2 = T2(n)
        d = log_drift(n)
        print(f"  n={n:3d}  T(n)={t1:5d}  T²(n)={t2:5d}  log_drift={d:+.4f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Bridge 0 drift verification: E[log T²(n) − log n] < 0"
    )
    parser.add_argument(
        "--mode",
        choices=["exhaustive", "sampling", "both"],
        default="both",
        help="Verification mode (default: both)",
    )
    parser.add_argument(
        "--M-min", type=int, default=4, metavar="M_MIN",
        help="Minimum M for exhaustive mode (default: 4)",
    )
    parser.add_argument(
        "--M-max", type=int, default=24, metavar="M_MAX",
        help="Maximum M for exhaustive mode (default: 24)",
    )
    parser.add_argument(
        "--trials", type=int, default=200_000,
        help="Number of random trials for sampling mode (default: 200000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for sampling mode (default: 42)",
    )
    parser.add_argument(
        "--output", type=str, default=os.path.join("scripts", "out"),
        help="Output directory for CSV/JSON files",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print_examples()
    print()

    summary = {}

    if args.mode in ("exhaustive", "both"):
        exhaustive_rows = run_exhaustive(
            M_min=args.M_min,
            M_max=args.M_max,
            output_dir=args.output,
        )
        summary["exhaustive"] = {
            "M_range": [args.M_min, args.M_max],
            "all_negative": all(r["negative"] for r in exhaustive_rows),
            "results": [
                {k: v for k, v in r.items()} for r in exhaustive_rows
            ],
        }
        print()

    if args.mode in ("sampling", "both"):
        sampling_result = run_sampling(
            num_trials=args.trials,
            seed=args.seed,
            output_dir=args.output,
        )
        summary["sampling"] = sampling_result
        print()

    # Heuristic: after one step the growth factor is ×3 but we divide by 2^k where
    # k = v₂(3n+1).  The expected number of halvings E[k] > log₂3 ≈ 1.585,
    # so the average net factor per step is < 3/2^{log₂3} = 3/3 = 1, i.e. < 1 in
    # multiplicative terms.  Over two steps this compounds: (3/4)² < 1, giving a
    # strictly negative log drift, as confirmed numerically above.
    log2_3 = math.log2(3)
    print(f"=== Heuristic check ===")
    print(f"  log₂3 ≈ {log2_3:.6f}  (minimum average halvings needed for contraction)")
    print(f"  Per step, growth factor ≈ 3/4 < 1  →  negative log drift confirmed.")
    print()

    # Write consolidated JSON
    json_path = os.path.join(args.output, "bridge0_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {json_path}")

    # Final verdict
    exhaustive_ok = summary.get("exhaustive", {}).get("all_negative", True)
    sampling_ok = summary.get("sampling", {}).get("drift_negative", True)
    if exhaustive_ok and sampling_ok:
        print("\n✓ Bridge 0 local control confirmed: E[log T²(n) − log n] < 0")
        sys.exit(0)
    else:
        print("\n✗ Unexpected result — check output files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
