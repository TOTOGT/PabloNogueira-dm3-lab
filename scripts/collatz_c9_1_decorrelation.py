#!/usr/bin/env python3
"""
C9.1 — Residue-Class Decorrelation Lemma: Numerical Evidence
=============================================================

Collatz macro-step  T(n) = (3n+1) / 2^v2(3n+1)  for odd n.

Event A : v2(3n+1) = 1          (equivalently n ≡ 3 mod 4)
Event B : v2(3T(n)+1) = 1       (next macro-step is also a (1,1) step)

Lemma (C9.1):
  There exist δ < 1 and M0 such that for all odd n ≥ 33 and all M ≥ M0,
    | Pr(B | A, n mod 2^M) − p11 | ≤ δ,
  uniformly over residue classes compatible with the discrete contact form.

Closed-form analysis (see docs/collatz_c9_1_decorrelation.md):
  p11  = 1/2   (unconditional probability of B given A)
  δ    = 1/2   (tight: residue classes mod 2^M for M ≥ 3 give prob 0 or 1)
  M0   = 2

This script enumerates residue classes mod 2^M for M = 2..MAX_M and
verifies the bound empirically over odd n in [33, N_MAX].

Usage:
  python collatz_c9_1_decorrelation.py [--N N_MAX] [--max-M MAX_M] [--output DIR]
"""

import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Core arithmetic
# ---------------------------------------------------------------------------

def v2(n: int) -> int:
    """Return the 2-adic valuation of n (largest k with 2^k | n).

    Raises ValueError for n == 0.
    """
    if n == 0:
        raise ValueError("v2(0) is undefined (infinite)")
    k = 0
    while n & 1 == 0:
        n >>= 1
        k += 1
    return k


def collatz_T(n: int) -> int:
    """Collatz macro-step T(n) = (3n+1) / 2^v2(3n+1) for odd n."""
    if n % 2 == 0:
        raise ValueError(f"T is defined only for odd n, got n={n}")
    val = 3 * n + 1
    return val >> v2(val)


def event_A(n: int) -> bool:
    """v2(3n+1) = 1, equivalently n ≡ 3 (mod 4)."""
    return v2(3 * n + 1) == 1


def event_B(n: int) -> bool:
    """v2(3T(n)+1) = 1 (next macro-step is also a (1,1) event).

    Requires n odd and event_A(n) to be meaningful; returns False otherwise.
    """
    if n % 2 == 0 or not event_A(n):
        return False
    Tn = collatz_T(n)
    return v2(3 * Tn + 1) == 1


# ---------------------------------------------------------------------------
# Residue-class analysis
# ---------------------------------------------------------------------------

def analyse_residue_class(r: int, M: int, n_min: int, n_max: int):
    """Count event A and event B occurrences for odd n ≡ r (mod 2^M) in [n_min, n_max].

    Returns (count_A, count_AB) where
      count_A  = #{odd n in range : n ≡ r mod 2^M, event_A(n)}
      count_AB = #{odd n in range : n ≡ r mod 2^M, event_A(n), event_B(n)}
    """
    mod = 1 << M  # 2^M
    count_A = 0
    count_AB = 0

    # Find the first odd n ≥ n_min with n ≡ r (mod mod)
    n = n_min if n_min % 2 == 1 else n_min + 1
    remainder = n % mod
    if remainder != r % mod:
        n += (r % mod - remainder) % mod
    # now n ≡ r (mod mod); step by mod to stay in residue class
    while n <= n_max:
        if n % 2 == 1 and event_A(n):
            count_A += 1
            if event_B(n):
                count_AB += 1
        n += mod

    return count_A, count_AB


def run_analysis(n_min: int, n_max: int, max_M: int):
    """Run the decorrelation analysis for all compatible residue classes mod 2^M.

    Returns a list of result dicts, one per (M, residue_class).
    """
    p11_exact = 0.5  # closed-form value
    results = []

    for M in range(2, max_M + 1):
        mod = 1 << M
        # Residue classes mod 2^M compatible with event A are exactly those r with r ≡ 3 (mod 4)
        compatible = [r for r in range(1, mod, 2) if r % 4 == 3]

        class_results = []
        total_A = 0
        total_AB = 0

        for r in compatible:
            count_A, count_AB = analyse_residue_class(r, M, n_min, n_max)
            cond_prob = count_AB / count_A if count_A > 0 else None
            deviation = abs(cond_prob - p11_exact) if cond_prob is not None else None
            class_results.append({
                "residue": r,
                "mod": mod,
                "M": M,
                "count_A": count_A,
                "count_AB": count_AB,
                "cond_prob_B_given_A": cond_prob,
                "deviation_from_p11": deviation,
            })
            total_A += count_A
            total_AB += count_AB

        max_dev = max(
            (cr["deviation_from_p11"] for cr in class_results if cr["deviation_from_p11"] is not None),
            default=None,
        )
        overall_cond = total_AB / total_A if total_A > 0 else None

        results.append({
            "M": M,
            "mod": mod,
            "n_range": [n_min, n_max],
            "p11_exact": p11_exact,
            "total_A": total_A,
            "total_AB": total_AB,
            "overall_cond_prob": overall_cond,
            "max_deviation_delta": max_dev,
            "num_compatible_classes": len(compatible),
            "class_results": class_results,
        })

    return results


def print_summary(results):
    """Print a human-readable summary table."""
    print("=" * 72)
    print("C9.1 Residue-Class Decorrelation Lemma — Numerical Evidence")
    print("=" * 72)
    print(f"{'M':>4}  {'mod':>6}  {'#classes':>8}  {'total_A':>10}  "
          f"{'cond_P(B|A)':>12}  {'max_δ':>8}")
    print("-" * 72)
    for r in results:
        overall = r["overall_cond_prob"]
        max_dev = r["max_deviation_delta"]
        print(f"{r['M']:>4}  {r['mod']:>6}  {r['num_compatible_classes']:>8}  "
              f"{r['total_A']:>10}  "
              f"{overall if overall is not None else 'N/A':>12.6f}  "
              f"{max_dev if max_dev is not None else 'N/A':>8.4f}")
    print("=" * 72)
    print()
    print("Closed-form result (see docs/collatz_c9_1_decorrelation.md):")
    print("  p11  = 1/2 (exact)")
    print("  δ    = 1/2 (tight bound; achieved at M ≥ 3 for individual classes)")
    print("  M0   = 2   (lemma holds for all M ≥ 2)")
    print()
    print("Key observation: for M = 2 the unique compatible class gives Pr(B|A) = 1/2 exactly.")
    print("For M ≥ 3, residue classes split evenly: half give Pr = 1, half give Pr = 0.")
    print("The deviation δ = 1/2 is strictly less than 1 — the lemma holds.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="C9.1 Decorrelation Lemma — numerical verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--N", type=int, default=10_000,
        help="Upper bound for odd n in the analysis (default: 10000)",
    )
    parser.add_argument(
        "--max-M", type=int, default=8,
        help="Maximum modulus exponent M (default: 8, giving mod 2^8 = 256)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory for JSON results (default: scripts/out/)",
    )
    args = parser.parse_args()

    n_min = 33
    n_max = args.N
    max_M = args.max_M

    if n_max < n_min:
        print(f"Error: --N must be at least {n_min}", file=sys.stderr)
        sys.exit(1)

    print(f"Analysing odd n in [{n_min}, {n_max}], M = 2..{max_M} ...")
    results = run_analysis(n_min, n_max, max_M)
    print_summary(results)

    # Write JSON output
    out_dir = args.output or os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"c9_1_N{n_max}_M{max_M}_decorrelation.json")
    with open(out_path, "w") as fh:
        json.dump(
            {
                "description": "C9.1 Residue-Class Decorrelation Lemma — numerical evidence",
                "parameters": {"n_min": n_min, "n_max": n_max, "max_M": max_M},
                "p11_exact": 0.5,
                "delta_bound": 0.5,
                "M0": 2,
                "results": results,
            },
            fh,
            indent=2,
        )
    print(f"\nFull results written to: {out_path}")


if __name__ == "__main__":
    main()
