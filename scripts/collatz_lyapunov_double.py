"""
Collatz / Syracuse double-iterate Lyapunov exponent λ₂.

For each modulus M (default 64 and 128) this script computes:

1. Transfer-operator spectral radius
   ρ(P_M) = 1 / (2^(M-1))   [exact, for the Syracuse map at modulus 2^M]
   ρ(P_M²) = ρ(P_M)²        [exact]
   λ₂^matrix = log ρ(P_M²)  [finite-resolution matrix exponent]

2. Empirical weighted drift
   λ₂^empirical = E[log(T²(n) / n)]
   averaged over all odd residue classes r mod 2^M,
   using `lifts_per_class` independent large random lifts
   n ≡ r (mod 2^M),  n_min ≤ n ≤ n_max.

The Syracuse map T used here is the fully-reduced "odd-to-odd" iterate:
  T(n) = (3n+1) / 2^v₂(3n+1)  for odd n,
where v₂ denotes the 2-adic valuation.  This always returns an odd integer
and gives E[log(T(n)/n)] ≈ log(3) − 2·log(2) = log(3/4) ≈ −0.2877,
matching the single-step Lyapunov exponent quoted in the problem statement.

Reference values (problem statement):
  Mod 64  : λ₁ ≈ -0.2872,  λ₂ ≈ -0.5744
  Mod 128 : λ₁ ≈ -0.287206, λ₂ ≈ -0.572187
"""

import argparse
import math
import random


# ---------------------------------------------------------------------------
# Syracuse / Collatz map (fully-reduced odd-to-odd form)
# ---------------------------------------------------------------------------

def T(n: int) -> int:
    """
    Fully-reduced Syracuse step for odd n.

    Returns (3n+1) / 2^v₂(3n+1), which is always odd.
    This is the standard "odd-to-odd" iterate used in Lyapunov analysis.
    """
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m


def T2(n: int) -> int:
    """Double iterate T²(n) = T(T(n))."""
    return T(T(n))


# ---------------------------------------------------------------------------
# Transfer-operator exact result
# ---------------------------------------------------------------------------

def matrix_exponent(mod_exp: int) -> dict:
    """
    For the Syracuse transfer operator at modulus 2^M (M = mod_exp):
      odd residues:      2^(M-1)
      spectral radius:   ρ(P_M)  = 1 / 2^(M-1)
      double-iterate:    ρ(P_M²) = 1 / 2^(2*(M-1))
      λ₂^matrix          = log ρ(P_M²) = -2(M-1) log 2
    """
    num_odd = 2 ** (mod_exp - 1)
    rho_single = 1.0 / num_odd
    rho_double = rho_single ** 2
    lam2_matrix = math.log(rho_double)
    return {
        "modulus": 2 ** mod_exp,
        "M": mod_exp,
        "num_odd_residues": num_odd,
        "rho_P": rho_single,
        "rho_P2": rho_double,
        "lambda2_matrix": lam2_matrix,
    }


# ---------------------------------------------------------------------------
# Empirical computation
# ---------------------------------------------------------------------------

def empirical_lambda2(
    mod_exp: int,
    lifts_per_class: int = 300,
    n_min: int = 1_000_000,
    n_max: int = 10_000_000,
    seed: int | None = None,
) -> dict:
    """
    Estimate λ₂ = E[log(T²(n)/n)] by sampling.

    For each odd residue r mod 2^mod_exp, draw `lifts_per_class` random
    integers n in [n_min, n_max] with n ≡ r (mod 2^mod_exp) and accumulate
    log(T²(n) / n).

    Returns a dict with the estimate and supporting statistics.
    """
    if seed is not None:
        random.seed(seed)

    modulus = 2 ** mod_exp
    odd_residues = [r for r in range(1, modulus, 2)]  # 2^(M-1) residues

    total_log = 0.0
    total_count = 0

    for r in odd_residues:
        # Draw `lifts_per_class` random n ≡ r (mod modulus) in [n_min, n_max].
        # The smallest such n ≥ n_min is: n_min + ((r - n_min) % modulus).
        offset = (r - n_min % modulus) % modulus
        base = n_min + offset          # first n ≡ r (mod modulus) >= n_min
        if base > n_max:
            continue

        # Number of valid multiples in range
        k_max = (n_max - base) // modulus
        if k_max < 0:
            continue

        for _ in range(lifts_per_class):
            k = random.randint(0, k_max)
            n = base + k * modulus
            t2n = T2(n)
            total_log += math.log(t2n / n)
            total_count += 1

    lambda2_empirical = total_log / total_count if total_count > 0 else float("nan")

    return {
        "modulus": modulus,
        "M": mod_exp,
        "lifts_per_class": lifts_per_class,
        "num_odd_residues": len(odd_residues),
        "total_samples": total_count,
        "lambda2_empirical": lambda2_empirical,
    }


# ---------------------------------------------------------------------------
# Single-step λ₁ for comparison
# ---------------------------------------------------------------------------

def empirical_lambda1(
    mod_exp: int,
    lifts_per_class: int = 300,
    n_min: int = 1_000_000,
    n_max: int = 10_000_000,
    seed: int | None = None,
) -> float:
    """Estimate λ₁ = E[log(T(n)/n)] over odd residues mod 2^mod_exp."""
    if seed is not None:
        random.seed(seed)

    modulus = 2 ** mod_exp
    odd_residues = [r for r in range(1, modulus, 2)]

    total_log = 0.0
    total_count = 0

    for r in odd_residues:
        offset = (r - n_min % modulus) % modulus
        base = n_min + offset
        if base > n_max:
            continue
        k_max = (n_max - base) // modulus
        if k_max < 0:
            continue
        for _ in range(lifts_per_class):
            k = random.randint(0, k_max)
            n = base + k * modulus
            total_log += math.log(T(n) / n)
            total_count += 1

    return total_log / total_count if total_count > 0 else float("nan")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute double-iterate Lyapunov exponent λ₂ for the Collatz map."
    )
    parser.add_argument(
        "--mod-exp",
        type=int,
        nargs="+",
        default=[6, 7],
        metavar="M",
        help="Exponents M so that modulus = 2^M (default: 6 7 → mod 64 and mod 128)",
    )
    parser.add_argument(
        "--lifts",
        type=int,
        default=300,
        metavar="N",
        help="Random lifts per residue class (default: 300)",
    )
    parser.add_argument(
        "--n-min",
        type=int,
        default=1_000_000,
        help="Lower bound for random lifts (default: 1 000 000)",
    )
    parser.add_argument(
        "--n-max",
        type=int,
        default=10_000_000,
        help="Upper bound for random lifts (default: 10 000 000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    args = parser.parse_args()

    header = f"{'Modulus':>10}  {'M':>3}  {'Odd res':>8}  "
    header += f"{'ρ(P_M²)':>14}  {'λ₂ matrix':>12}  "
    header += f"{'λ₁ empir':>12}  {'λ₂ empir':>12}  {'ratio λ₂/λ₁':>12}"
    print(header)
    print("-" * len(header))

    for m in args.mod_exp:
        exact = matrix_exponent(m)
        lam1 = empirical_lambda1(m, args.lifts, args.n_min, args.n_max, args.seed)
        emp = empirical_lambda2(m, args.lifts, args.n_min, args.n_max, args.seed)
        lam2 = emp["lambda2_empirical"]
        ratio = lam2 / lam1 if lam1 != 0 else float("nan")

        print(
            f"{exact['modulus']:>10}  {m:>3}  {exact['num_odd_residues']:>8}  "
            f"{exact['rho_P2']:>14.8f}  {exact['lambda2_matrix']:>12.6f}  "
            f"{lam1:>12.6f}  {lam2:>12.6f}  {ratio:>12.6f}"
        )


if __name__ == "__main__":
    main()
