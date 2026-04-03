"""
AXLE — Transfer Matrix for the Syracuse (Collatz) Return Map
transfer_matrix_collatz.py

Builds the finite-dimensional transfer matrix P for the Syracuse return map

    T(n) = (3n + 1) / 2^{v_2(3n+1)}       (n odd)

modulo 2^M, acting on odd residues  {1, 3, 5, …, 2^M − 1}.

The entry P_{i,j} = 1/8 when T(i) ≡ j (mod 2^M), and 0 otherwise.
(Each row has exactly one non-zero entry = 1/8 because T is a deterministic
function, and uniform measure 1/8 flows along each transition at modulus 16.)

Features
--------
- Build P for any modulus 2^M  (default M = 4, i.e., mod 16)
- Spectral analysis: eigenvalues, spectral radius, dominant eigenvector
- Double-iterate  T²  via matrix squaring  P²
- Log-drift  E[log T²(n) − log n]  under uniform measure

Usage
-----
    python transfer_matrix_collatz.py
    python transfer_matrix_collatz.py --modulus 5        # mod 32
    python transfer_matrix_collatz.py --modulus 6        # mod 64
    python transfer_matrix_collatz.py --modulus 4 --iterate 2 --log-drift
    python transfer_matrix_collatz.py --output results.json

G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026
MIT License
"""

import argparse
import json
import math
import numpy as np
from pathlib import Path


# ── SYRACUSE RETURN MAP ───────────────────────────────────────────────────────

def v2(n: int) -> int:
    """2-adic valuation of n (largest k such that 2^k | n)."""
    if n == 0:
        return float("inf")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def syracuse_T(n: int) -> int:
    """Syracuse return map: T(n) = (3n+1) / 2^{v_2(3n+1)} for odd n."""
    if n % 2 == 0:
        raise ValueError(f"T is defined only for odd n; got {n}")
    m = 3 * n + 1
    return m >> v2(m)


# ── TRANSFER MATRIX BUILDER ───────────────────────────────────────────────────

def odd_residues(M: int) -> list[int]:
    """Return the 2^{M-1} odd residues modulo 2^M in sorted order."""
    mod = 1 << M          # 2^M
    return list(range(1, mod, 2))


def build_transfer_matrix(M: int) -> tuple[np.ndarray, list[int]]:
    """
    Build the (2^{M-1}) × (2^{M-1}) transfer matrix P for the Syracuse
    return map modulo 2^M.

    P_{i,j} = 1 / 2^{M-1}  if  T(states[i]) ≡ states[j]  (mod 2^M)
              0              otherwise.

    Returns
    -------
    P       : ndarray, shape (2^{M-1}, 2^{M-1})
    states  : list of odd residues modulo 2^M
    """
    states = odd_residues(M)
    n_states = len(states)          # = 2^{M-1}
    mod = 1 << M                    # 2^M
    weight = 1.0 / n_states         # uniform measure weight

    index = {s: i for i, s in enumerate(states)}
    P = np.zeros((n_states, n_states), dtype=float)

    for i, s in enumerate(states):
        target = syracuse_T(s) % mod
        j = index[target]
        P[i, j] = weight

    return P, states


# ── SPECTRAL ANALYSIS ─────────────────────────────────────────────────────────

def spectral_analysis(P: np.ndarray) -> dict:
    """
    Compute eigenvalues, spectral radius, and the dominant right eigenvector
    of the transfer matrix P.
    """
    eigenvalues = np.linalg.eigvals(P)
    spectral_radius = float(np.max(np.abs(eigenvalues)))

    # Dominant eigenvector (right) for the largest eigenvalue
    eigvals_full, eigvecs = np.linalg.eig(P)
    idx = np.argmax(np.abs(eigvals_full))
    dominant_vec = np.real(eigvecs[:, idx])
    dominant_vec /= dominant_vec.sum() if dominant_vec.sum() != 0 else 1.0

    return {
        "eigenvalues": eigenvalues.tolist(),
        "spectral_radius": spectral_radius,
        "dominant_eigenvalue": complex(eigvals_full[idx]),
        "dominant_eigenvector": dominant_vec.tolist(),
        "row_sums": P.sum(axis=1).tolist(),
    }


# ── LOG-DRIFT ─────────────────────────────────────────────────────────────────

def log_drift(M: int, iterate: int = 2) -> dict:
    """
    Compute  E[ log T^k(n) − log n ]  under uniform measure on odd residues
    modulo 2^M, using the explicit transitions.

    For each odd residue n, applies T exactly `iterate` times (tracking the
    true integer value modulo 2^M at each step) and accumulates log-ratios.

    Returns the mean log-ratio and standard deviation.
    """
    states = odd_residues(M)
    log_ratios = []
    for n in states:
        current = n
        for _ in range(iterate):
            current = syracuse_T(current) % (1 << M)
            if current == 0:          # wrap: treat 0 as the modulus itself
                current = 1 << M
        ratio = math.log(current / n) if n > 0 else 0.0
        log_ratios.append(ratio)

    arr = np.array(log_ratios)
    return {
        "iterate": iterate,
        "modulus": 1 << M,
        "mean_log_ratio": float(arr.mean()),
        "std_log_ratio": float(arr.std()),
        "negative_drift": bool(arr.mean() < 0),
    }


# ── PRETTY PRINTING ───────────────────────────────────────────────────────────

def print_matrix(P: np.ndarray, states: list[int], title: str = "Transfer Matrix P"):
    """Print the matrix in a readable tabular form."""
    n = len(states)
    col_w = 8
    header = f"{'':>4}  " + "".join(f"{s:>{col_w}}" for s in states)
    print(f"\n{title}")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for i, s in enumerate(states):
        row = f"{s:>4}  " + "".join(f"{P[i, j]:>{col_w}.4f}" for j in range(n))
        print(row)
    print()


def print_transitions(M: int):
    """Print explicit n → T(n) mod 2^M transitions for odd residues."""
    mod = 1 << M
    states = odd_residues(M)
    print(f"\nExplicit transitions mod {mod}:")
    for n in states:
        t = syracuse_T(n) % mod
        k = v2(3 * n + 1)
        print(f"  {n:>3} → {t:>3}   [v₂(3·{n}+1) = {k}]")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Syracuse return map transfer matrix (2-adic approximation)"
    )
    parser.add_argument(
        "--modulus", type=int, default=4, metavar="M",
        help="Work modulo 2^M  (default: 4 → mod 16)"
    )
    parser.add_argument(
        "--iterate", type=int, default=1, metavar="K",
        help="Matrix power P^K to compute  (default: 1)"
    )
    parser.add_argument(
        "--log-drift", action="store_true",
        help="Compute log-drift E[log T^K(n) − log n] under uniform measure"
    )
    parser.add_argument(
        "--output", type=str, default=None, metavar="FILE",
        help="Save results as JSON to FILE"
    )
    args = parser.parse_args()

    M = args.modulus
    mod = 1 << M

    print("=" * 60)
    print("AXLE — Syracuse Return Map Transfer Matrix")
    print(f"       Modulus: {mod}  (M = {M},  states: {1 << (M-1)})")
    print("G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026")
    print("=" * 60)

    # Build base matrix
    P, states = build_transfer_matrix(M)
    print_transitions(M)
    print_matrix(P, states, title=f"Transfer Matrix P  (mod {mod})")

    # Spectral analysis of P
    spec = spectral_analysis(P)
    print("Spectral Analysis of P:")
    print(f"  Spectral radius ρ(P) = {spec['spectral_radius']:.6f}")
    print(f"  Row sums (all should be {1.0 / (1 << (M-1)):.4f}): "
          f"min={min(spec['row_sums']):.4f}  max={max(spec['row_sums']):.4f}")
    eigs_sorted = sorted(np.abs(spec["eigenvalues"]), reverse=True)
    print(f"  |eigenvalues| (top 5): {[round(e, 6) for e in eigs_sorted[:5]]}")

    results: dict = {
        "modulus": mod,
        "M": M,
        "states": states,
        "matrix_P": P.tolist(),
        "spectral_radius_P": spec["spectral_radius"],
        "eigenvalues_P": [{"re": complex(e).real, "im": complex(e).imag}
                          for e in spec["eigenvalues"]],
    }

    # Matrix power P^K
    if args.iterate > 1:
        K = args.iterate
        PK = np.linalg.matrix_power(P, K)
        spec_K = spectral_analysis(PK)
        print_matrix(PK, states, title=f"P^{K}  (mod {mod})")
        print(f"Spectral Analysis of P^{K}:")
        print(f"  Spectral radius ρ(P^{K}) = {spec_K['spectral_radius']:.6f}")
        results[f"matrix_P{K}"] = PK.tolist()
        results[f"spectral_radius_P{K}"] = spec_K["spectral_radius"]
    else:
        K = 1

    # Log-drift
    if args.log_drift:
        drift = log_drift(M, iterate=K)
        print(f"\nLog-Drift  E[ log T^{K}(n) − log n ]  (mod {mod}):")
        print(f"  Mean log-ratio : {drift['mean_log_ratio']:.6f}")
        print(f"  Std  log-ratio : {drift['std_log_ratio']:.6f}")
        print(f"  Negative drift : {drift['negative_drift']}  "
              f"({'2-adic contraction confirmed' if drift['negative_drift'] else 'no contraction at this scale'})")
        results["log_drift"] = drift

    # JSON output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[AXLE] Results saved: {out_path}")

    print("\n[AXLE] C → K → F → U → ∞")
    return results


if __name__ == "__main__":
    main()
