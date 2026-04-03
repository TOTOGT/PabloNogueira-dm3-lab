"""
collatz_c9_3_averaging.py — C9.3 Averaging Measure and Finite-Window Implementation

G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026
MIT License

Implements the three canonical window types and averaging measure μ defined in
docs/d9_averaging_window_conventions.md for D9 analysis.

Window types
------------
contiguous  W_N  = {1, …, N},           |W| = N
dyadic      W_k  = {2^k, …, 2^(k+1)−1}, |W| = 2^k
logarithmic [1,N] with harmonic weights 1/n

Usage (CLI)
-----------
python scripts/collatz_c9_3_averaging.py \\
    --event odd \\
    --window-type dyadic \\
    --param 20 \\
    --output scripts/out/d9_example.json
"""

# ── standard library ─────────────────────────────────────────────────────────
import argparse
import json
import math
import os
from typing import Callable

# ── event definitions ─────────────────────────────────────────────────────────

def event_odd(n: int) -> bool:
    """A = {n : n is odd}."""
    return n % 2 == 1


def _v2(n: int) -> int:
    """2-adic valuation of n (largest k such that 2^k | n)."""
    if n == 0:
        return 0
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def collatz_step(n: int) -> int:
    """One step of the Collatz map: n → n/2 if even, (3n+1)/2^v2(3n+1) if odd."""
    if n % 2 == 0:
        return n // 2
    raw = 3 * n + 1
    return raw // (2 ** _v2(raw))


def event_strong_decrease(n: int) -> bool:
    """A = {n : T(n) < n/2} — strong Collatz decrease (used in C9.2)."""
    return collatz_step(n) < n / 2


EVENTS: dict[str, Callable[[int], bool]] = {
    "odd": event_odd,
    "strong_decrease": event_strong_decrease,
}

# ── window function helpers ───────────────────────────────────────────────────

def window_index_dyadic(n: int) -> int:
    """w_dyad(n) = floor(log2(n)) for n >= 1."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return int(math.floor(math.log2(n)))


def dyadic_window(k: int) -> range:
    """Return the dyadic window W_k = [2^k, 2^(k+1)) as a range."""
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    return range(2 ** k, 2 ** (k + 1))


def contiguous_window(N: int) -> range:
    """Return the contiguous window W_N = [1, N] as a range."""
    if N < 1:
        raise ValueError(f"N must be >= 1, got {N}")
    return range(1, N + 1)

# ── averaging measure ─────────────────────────────────────────────────────────

def mu_contiguous(event: Callable[[int], bool], N: int) -> float:
    """
    Contiguous averaging measure over [1, N].

    μ^arith_N(A) = |{n ∈ [1,N] : A(n)}| / N
    """
    hits = sum(1 for n in contiguous_window(N) if event(n))
    return hits / N


def mu_dyadic(event: Callable[[int], bool], k: int) -> float:
    """
    Dyadic averaging measure over [2^k, 2^(k+1)).

    μ^dyad_k(A) = |{n ∈ [2^k, 2^(k+1)) : A(n)}| / 2^k
    """
    window = dyadic_window(k)
    hits = sum(1 for n in window if event(n))
    return hits / len(window)


def mu_logarithmic(event: Callable[[int], bool], N: int) -> float:
    """
    Logarithmic (harmonic-weight) averaging measure over [1, N].

    μ^log_N(A) = (1/H_N) * Σ_{n=1}^{N} 1_A(n)/n,  H_N = Σ_{n=1}^{N} 1/n
    """
    harmonic_total = sum(1.0 / n for n in range(1, N + 1))
    weighted_hits = sum(1.0 / n for n in range(1, N + 1) if event(n))
    return weighted_hits / harmonic_total

# ── D9 metadata builder ───────────────────────────────────────────────────────

def build_d9_metadata(
    event_name: str,
    window_type: str,
    param: int,
    mu_value: float,
) -> dict:
    """
    Build a D9-compliant metadata dict following the canonical convention
    defined in docs/d9_averaging_window_conventions.md §6.
    """
    if window_type == "contiguous":
        window_str = f"[1, {param}]"
        window_size = param
    elif window_type == "dyadic":
        lo, hi = 2 ** param, 2 ** (param + 1)
        window_str = f"[{lo}, {hi})"
        window_size = lo
    else:  # logarithmic
        window_str = f"[1, {param}]"
        window_size = param

    return {
        "d9_convention_version": "1.0",
        "event": event_name,
        "window_type": window_type,
        "window_parameter": param,
        "window": window_str,
        "window_size": window_size,
        "mu_W": round(mu_value, 6),
        "limit_status": "finite_approximation",
        "limsup": None,
        "liminf": None,
        "source": "docs/d9_averaging_window_conventions.md",
    }

# ── limsup / liminf estimation ────────────────────────────────────────────────

def estimate_limsup_liminf(
    event: Callable[[int], bool],
    window_type: str,
    param_range: range,
) -> tuple[float, float]:
    """
    Estimate limsup and liminf of μ_W(A) over a sequence of windows.

    Parameters
    ----------
    event       : callable n → bool
    window_type : 'contiguous' | 'dyadic' | 'logarithmic'
    param_range : range of N (contiguous/logarithmic) or k (dyadic) values

    Returns
    -------
    (limsup_estimate, liminf_estimate)
    """
    measures = []
    for p in param_range:
        if window_type == "contiguous":
            measures.append(mu_contiguous(event, p))
        elif window_type == "dyadic":
            measures.append(mu_dyadic(event, p))
        else:
            measures.append(mu_logarithmic(event, p))
    return max(measures), min(measures)

# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.3 — Averaging measure μ for D9 analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--event",
        type=str,
        choices=list(EVENTS.keys()),
        required=True,
        help="Event A to measure",
    )
    parser.add_argument(
        "--window-type",
        type=str,
        choices=["contiguous", "dyadic", "logarithmic"],
        required=True,
        help="Canonical window type (see docs/d9_averaging_window_conventions.md)",
    )
    parser.add_argument(
        "--param",
        type=int,
        required=True,
        help="Window parameter: N for contiguous/logarithmic, k for dyadic",
    )
    parser.add_argument(
        "--limsup-liminf",
        action="store_true",
        default=False,
        help="Also estimate limsup/liminf over a sequence of windows ending at --param",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSON file path",
    )
    args = parser.parse_args()

    event_fn = EVENTS[args.event]
    window_type = args.window_type
    param = args.param

    # Compute μ_W(A)
    if window_type == "contiguous":
        mu_value = mu_contiguous(event_fn, param)
    elif window_type == "dyadic":
        mu_value = mu_dyadic(event_fn, param)
    else:
        mu_value = mu_logarithmic(event_fn, param)

    metadata = build_d9_metadata(args.event, window_type, param, mu_value)

    # Optionally estimate limsup / liminf
    if args.limsup_liminf:
        if window_type == "dyadic":
            seq = range(max(0, param - 9), param + 1)
        else:
            step = max(1, param // 10)
            seq = range(max(1, param - 9 * step), param + step, step)
        ls, li = estimate_limsup_liminf(event_fn, window_type, seq)
        metadata["limsup"] = round(ls, 6)
        metadata["liminf"] = round(li, 6)
        metadata["limit_status"] = (
            "converged" if round(ls - li, 4) == 0.0 else "finite_approximation"
        )

    # Write output
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[C9.3] window_type={window_type}  param={param}  "
          f"mu_W({args.event})={metadata['mu_W']}")
    if metadata["limsup"] is not None:
        print(f"[C9.3] limsup≈{metadata['limsup']}  liminf≈{metadata['liminf']}  "
              f"status={metadata['limit_status']}")
    print(f"[C9.3] D9 metadata written to {args.output}")


if __name__ == "__main__":
    main()
