"""
Mod-27 Weighted Drift Calculation for the Double Syracuse Map T²
=================================================================
Computes  E[log(T²(n)/n)]  separately for each of the 13 odd residue
classes r (mod 27) and reports the uniform average over classes.

Method
------
For each class r in {1,3,5,7,9,11,13,15,17,19,21,23,25}:
  - Sample SAMPLES_PER_CLASS random odd integers n ≡ r (mod 27)
    drawn uniformly from [N_MIN, N_MAX].
  - Compute T²(n) = T(T(n)) where T is the Syracuse (shortcut Collatz) map:
        T(n) = (3n + 1) / 2^v₂(3n+1)   for odd n
  - Accumulate log(T²(n) / n) and average.

The overall weighted drift is the uniform average over all 13 classes.

Usage
-----
    python scripts/collatz_mod27_drift.py [--seed SEED]
                                          [--samples SAMPLES_PER_CLASS]
                                          [--nmin N_MIN] [--nmax N_MAX]
                                          [--output OUTPUT_JSON]

Defaults match the values cited in the dm³ + Crystal-Geometry paper
(seed=42, 5 000 samples per class, n in [10^6, 10^9]).
"""

import argparse
import json
import math
import os
import random


# ---------------------------------------------------------------------------
# Syracuse / Collatz helpers
# ---------------------------------------------------------------------------

def v2(k: int) -> int:
    """Return the 2-adic valuation of k (largest power of 2 dividing k)."""
    if k == 0:
        return 0
    count = 0
    while k % 2 == 0:
        k >>= 1
        count += 1
    return count


def syracuse_T(n: int) -> int:
    """
    Single step of the Syracuse (shortcut Collatz) map for odd n.
    T(n) = (3n + 1) / 2^v₂(3n+1)
    The result is always odd.
    """
    m = 3 * n + 1
    return m >> v2(m)


def syracuse_T2(n: int) -> int:
    """Double step: T²(n) = T(T(n))."""
    return syracuse_T(syracuse_T(n))


# ---------------------------------------------------------------------------
# Sampling helper
# ---------------------------------------------------------------------------

ODD_RESIDUES_MOD27 = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
TRIAD_RESIDUES = {3, 9, 15, 21}


def sample_odd_in_class(r: int, n_min: int, n_max: int, rng: random.Random) -> int:
    """
    Return a random odd integer n with n ≡ r (mod 27) and n_min ≤ n ≤ n_max.

    Because 27 is odd and r is odd, n = 27*k + r is odd iff k is even.
    Substituting k = 2*j gives n = 54*j + r, which is always odd and
    satisfies n ≡ r (mod 27).  We therefore sample uniformly over j
    in the appropriate range (step size 54).
    """
    j_min = math.ceil((n_min - r) / 54)
    j_max = math.floor((n_max - r) / 54)
    if j_min > j_max:
        raise ValueError(
            f"No odd integer n ≡ {r} (mod 27) in [{n_min}, {n_max}]"
        )
    j = rng.randint(j_min, j_max)
    return 54 * j + r


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_drift(
    samples_per_class: int,
    n_min: int,
    n_max: int,
    seed: int,
) -> dict:
    """
    Compute per-class and overall weighted drift E[log(T²(n)/n)].

    Returns a dict with keys:
      'per_class'   : {r: mean_log_ratio}
      'overall'     : float  (uniform average over the 13 classes)
      'class_count' : int
      'samples_per_class': int
      'seed'        : int
      'n_min'       : int
      'n_max'       : int
    """
    rng = random.Random(seed)
    per_class = {}

    for r in ODD_RESIDUES_MOD27:
        total = 0.0
        for _ in range(samples_per_class):
            n = sample_odd_in_class(r, n_min, n_max, rng)
            t2n = syracuse_T2(n)
            total += math.log(t2n / n)
        mean = total / samples_per_class
        per_class[r] = mean

    overall = sum(per_class.values()) / len(per_class)

    return {
        "per_class": per_class,
        "overall": overall,
        "class_count": len(ODD_RESIDUES_MOD27),
        "samples_per_class": samples_per_class,
        "seed": seed,
        "n_min": n_min,
        "n_max": n_max,
    }


def print_results(result: dict) -> None:
    """Pretty-print the drift table."""
    print()
    print("Mod-27 Weighted Drift  E[log(T²(n)/n)]")
    print("=" * 48)
    print(f"{'Residue r (mod 27)':<22} {'Mean log-ratio':>14}  {'Triad?':>6}")
    print("-" * 48)
    for r in ODD_RESIDUES_MOD27:
        triad_marker = " ✓" if r in TRIAD_RESIDUES else ""
        print(f"  r = {r:<17} {result['per_class'][r]:>14.6f}{triad_marker}")
    print("-" * 48)
    print(f"  {'Overall weighted drift':<19} {result['overall']:>14.6f}")
    print()
    vals = list(result["per_class"].values())
    print(f"  Range: {min(vals):.6f}  to  {max(vals):.6f}")
    print(f"  Samples per class : {result['samples_per_class']}")
    print(f"  n range           : [{result['n_min']}, {result['n_max']}]")
    print(f"  Seed              : {result['seed']}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute mod-27 weighted drift for the double Syracuse map T²."
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--samples", type=int, default=5000,
        help="Number of samples per residue class (default: 5000)"
    )
    parser.add_argument(
        "--nmin", type=int, default=10 ** 6,
        help="Lower bound for n (default: 1 000 000)"
    )
    parser.add_argument(
        "--nmax", type=int, default=10 ** 9,
        help="Upper bound for n (default: 1 000 000 000)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Optional path for JSON output file"
    )
    args = parser.parse_args()

    result = compute_drift(
        samples_per_class=args.samples,
        n_min=args.nmin,
        n_max=args.nmax,
        seed=args.seed,
    )

    print_results(result)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as fh:
            json.dump(result, fh, indent=2)
        print(f"  Results written to {args.output}")


if __name__ == "__main__":
    main()
