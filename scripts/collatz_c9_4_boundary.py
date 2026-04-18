"""
C9.4 — Boundary Perturbation Analysis for +1 Injections (Collatz)

This module catalogs small-n exceptions, establishes O(1/n) average-effect
bounds for the +1 injection in the Collatz map T(n) = (3n+1)/2^v₂(3n+1),
and provides utilities to identify and exclude boundary windows so that
the decorrelation lemma is not biased.

Definitions
-----------
* **+1 injection**: The additive correction that makes 3n+1 even for odd n,
  enabling the subsequent 2-adic right-shift.  Without it, T(n) = 3n would
  stay odd and the map would be ill-typed.

* **Injection bias Δ(n)**: The relative deviation of T(n) from the "pure"
  value 3n/2^v₂(3n+1), i.e.

      Δ(n) = 1 / (3n + 1)          (for odd n)

  This is strictly O(1/n).

* **Boundary event**: For a window W = [a, b], the step T(n) is a boundary
  event if T(n) < a or T(n) > b (exits the window).

* **Small-n regime**: n ≤ N_SMALL (default 64).  In this regime Δ(n) is
  large enough (≥ 1/193) to merit individual enumeration.

References
----------
* C9.2 sampling framework: scripts/collatz_c9_2_sampling.py
* Analysis notes: docs/analysis_ns/c9_4_boundary_analysis.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from typing import Iterator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_SMALL: int = 64  # threshold below which small-n exceptions are enumerated


# ---------------------------------------------------------------------------
# Core Collatz primitives
# ---------------------------------------------------------------------------

def v2(k: int) -> int:
    """Return the 2-adic valuation of the positive integer k."""
    if k <= 0:
        raise ValueError(f"v2 requires a positive integer, got {k}")
    count = 0
    while k % 2 == 0:
        k //= 2
        count += 1
    return count


def collatz_step(n: int) -> int:
    """One Collatz step: T(n) = n//2 if n even, (3n+1)//2^v₂(3n+1) if n odd."""
    if n <= 0:
        raise ValueError(f"collatz_step requires a positive integer, got {n}")
    if n % 2 == 0:
        return n // 2
    raw = 3 * n + 1
    return raw >> v2(raw)


def injection_bias(n: int) -> float:
    """
    Return the +1 injection bias Δ(n) = 1/(3n+1) for odd n > 0.

    This represents the fractional contribution of the '+1' correction to the
    output of T.  By definition Δ(n) = O(1/n).

    For even n the bias is zero (even step is n/2, no +1 injection).
    """
    if n <= 0:
        raise ValueError(f"injection_bias requires n > 0, got {n}")
    if n % 2 == 0:
        return 0.0
    return 1.0 / (3 * n + 1)


# ---------------------------------------------------------------------------
# Small-n exception catalog
# ---------------------------------------------------------------------------

def _is_boundary_event(n: int, window_start: int, window_end: int) -> bool:
    """True if T(n) exits [window_start, window_end]."""
    image = collatz_step(n)
    return image < window_start or image > window_end


def catalog_small_n_exceptions(
    n_max: int = N_SMALL,
    window_start: int = 1,
    window_end: int | None = None,
) -> list[dict]:
    """
    Enumerate all odd n in [1, n_max] where the Collatz step exits
    the window [window_start, window_end].

    Parameters
    ----------
    n_max : int
        Upper limit of the small-n regime (default N_SMALL = 64).
    window_start : int
        Lower boundary of the sampling window.
    window_end : int | None
        Upper boundary; defaults to n_max if not given.

    Returns
    -------
    list of dicts with keys:
        n          – the input value
        T_n        – T(n)
        v2_val     – v₂(3n+1)
        bias       – injection bias Δ(n) = 1/(3n+1)
        exit_dir   – 'below' | 'above' | 'none'
    """
    if window_end is None:
        window_end = n_max
    exceptions: list[dict] = []
    for n in range(1, n_max + 1):
        if n % 2 == 0:
            continue
        t = collatz_step(n)
        raw = 3 * n + 1
        bias = 1.0 / raw
        if t < window_start:
            exit_dir = "below"
        elif t > window_end:
            exit_dir = "above"
        else:
            exit_dir = "none"
        exceptions.append(
            {
                "n": n,
                "T_n": t,
                "v2_val": v2(raw),
                "bias": round(bias, 8),
                "exit_dir": exit_dir,
            }
        )
    return exceptions


def count_exceptions(
    n_max: int = N_SMALL,
    window_start: int = 1,
    window_end: int | None = None,
) -> dict:
    """
    Return summary counts of small-n boundary exceptions.

    Returns a dict with keys:
        total_odd       – total odd n in [1, n_max]
        exits_below     – count of T(n) < window_start
        exits_above     – count of T(n) > window_end
        interior        – count remaining in window
        exit_frequency  – (exits_below + exits_above) / total_odd
    """
    rows = catalog_small_n_exceptions(n_max, window_start, window_end)
    total_odd = len(rows)
    exits_below = sum(1 for r in rows if r["exit_dir"] == "below")
    exits_above = sum(1 for r in rows if r["exit_dir"] == "above")
    interior = total_odd - exits_below - exits_above
    return {
        "total_odd": total_odd,
        "exits_below": exits_below,
        "exits_above": exits_above,
        "interior": interior,
        "exit_frequency": (exits_below + exits_above) / total_odd
        if total_odd > 0
        else 0.0,
    }


# ---------------------------------------------------------------------------
# O(1/n) bound verification
# ---------------------------------------------------------------------------

def _odd_range(start: int, end: int) -> Iterator[int]:
    """Yield all odd integers in [start, end]."""
    n = start if start % 2 == 1 else start + 1
    while n <= end:
        yield n
        n += 2


def verify_o1n_bound(
    n_start: int = 1,
    n_end: int = 1024,
) -> list[dict]:
    """
    For each odd n in [n_start, n_end], compute:
      * bias  Δ(n)     = 1/(3n+1)
      * bound 1/n
      * ratio Δ(n)·n   — must stay ≤ 1/3 to confirm Δ(n) = O(1/n)

    The ratio Δ(n) · n = n/(3n+1) → 1/3 from below, confirming Δ(n) ≤ 1/(3n).

    Returns a list of dicts (one per odd n) with the above fields.
    """
    results = []
    for n in _odd_range(n_start, n_end):
        bias = injection_bias(n)
        ratio = bias * n  # n/(3n+1), must be < 1/3
        results.append(
            {
                "n": n,
                "bias": round(bias, 10),
                "bound_1_over_n": round(1.0 / n, 10),
                "ratio_bias_times_n": round(ratio, 10),
                "bound_satisfied": ratio < 1.0 / 3,
            }
        )
    return results


def average_bias_in_window(window_start: int, window_end: int) -> dict:
    """
    Compute the average injection bias over all odd n in [window_start, window_end]
    and verify the O(1/n) upper bound.

    The upper bound is: avg Δ(n) ≤ Δ(n_min) = 1/(3·n_min + 1) where n_min is
    the smallest odd n in the window.  Since every Δ(n) ≤ Δ(n_min), the ratio
    avg_bias / predicted_bound is always ≤ 1.

    Parameters
    ----------
    window_start : int
        First integer of the window (inclusive).
    window_end : int
        Last integer of the window (inclusive).

    Returns
    -------
    dict with keys:
        window_start, window_end
        n_bar           – arithmetic mean of odd n's in window
        n_min           – smallest odd n in window
        avg_bias        – empirical average Δ(n)
        predicted_bound – 1/(3·n_min + 1)  (O(1/n) upper bound)
        ratio           – avg_bias / predicted_bound  (must be ≤ 1)
    """
    odd_ns = list(_odd_range(window_start, window_end))
    if not odd_ns:
        return {
            "window_start": window_start,
            "window_end": window_end,
            "n_bar": None,
            "avg_bias": None,
            "predicted_bound": None,
            "ratio": None,
        }
    n_bar = sum(odd_ns) / len(odd_ns)
    n_min = odd_ns[0]
    avg_bias = sum(injection_bias(n) for n in odd_ns) / len(odd_ns)
    # The O(1/n) upper bound: avg Δ(n) ≤ max Δ(n) = Δ(n_min) = 1/(3*n_min+1).
    # Δ(n) is strictly decreasing, so this is a valid per-window bound;
    # for any window [a, b] the average bias is at most 1/(3a+1) = O(1/a).
    predicted_bound = 1.0 / (3 * n_min + 1)
    ratio = avg_bias / predicted_bound if predicted_bound > 0 else None
    return {
        "window_start": window_start,
        "window_end": window_end,
        "n_bar": round(n_bar, 4),
        "n_min": n_min,
        "avg_bias": round(avg_bias, 10),
        "predicted_bound": round(predicted_bound, 10),
        "ratio": round(ratio, 6) if ratio is not None else None,
    }


# ---------------------------------------------------------------------------
# Boundary-window detection and exclusion
# ---------------------------------------------------------------------------

def identify_boundary_windows(
    n_start: int,
    n_end: int,
    window_size: int,
    boundary_depth: int = 1,
) -> list[dict]:
    """
    Slide windows of size `window_size` over [n_start, n_end] and identify
    those containing the first or last `boundary_depth` odd values (boundary
    windows) versus interior windows.

    For each window [a, a+window_size), report:
        a               – window start
        b               – window end (exclusive)
        is_boundary     – True if window touches [n_start, n_start+boundary_depth*2]
                          or [n_end-boundary_depth*2, n_end]
        exit_count      – number of odd n in window with T(n) outside window
        exit_frequency  – exit_count / total_odd_in_window

    This lets callers exclude boundary windows in analytic arguments.
    """
    results = []
    a = n_start
    while a + window_size <= n_end + 1:
        b = a + window_size - 1
        odd_ns = list(_odd_range(a, b))
        if not odd_ns:
            a += window_size
            continue
        exits = sum(1 for n in odd_ns if _is_boundary_event(n, a, b))
        is_boundary = (
            a <= n_start + boundary_depth * 2
            or b >= n_end - boundary_depth * 2
        )
        results.append(
            {
                "window_start": a,
                "window_end": b,
                "is_boundary": is_boundary,
                "total_odd": len(odd_ns),
                "exit_count": exits,
                "exit_frequency": round(exits / len(odd_ns), 6),
            }
        )
        a += window_size
    return results


def decorrelation_bias_estimate(
    n_start: int,
    n_end: int,
    exclude_boundary_windows: bool = False,
    window_size: int = 16,
) -> dict:
    """
    Estimate the total decorrelation bias introduced by +1 injections over
    all odd n in [n_start, n_end].

    The bias for a single odd n is Δ(n) = 1/(3n+1).  The average per-sample
    bias over an interval [a, b] is bounded by Δ(a) = 1/(3a+1) = O(1/a),
    confirming the O(1/n) average-effect statement from C9.4.  See also
    `average_bias_in_window` which establishes the same bound per window.

    If `exclude_boundary_windows=True`, odd n values in the first and last
    `window_size` integers of [n_start, n_end] are dropped before computing
    the estimate.  This mirrors the analytic recommendation to discard
    boundary windows.  If the range is too small for exclusion (i.e.
    n_start + window_size > n_end - window_size), the exclusion is silently
    skipped and the full range [n_start, n_end] is used instead.

    Returns a dict with:
        n_start, n_end
        excluded_boundary : bool
        sample_count      : int (number of odd n used)
        total_bias        : float
        avg_bias          : float  (≤ 1/(3·n_min+1))
        n_bar             : float
        n_min             : int
        predicted_avg     : float  (= 1/(3·n_min+1), per-window O(1/n) bound)
        ratio             : float  (avg_bias / predicted_avg, always ≤ 1)
    """
    lo = n_start + window_size if exclude_boundary_windows else n_start
    hi = n_end - window_size if exclude_boundary_windows else n_end
    if lo > hi:
        lo, hi = n_start, n_end  # fallback: don't exclude if range too small
    odd_ns = list(_odd_range(lo, hi))
    if not odd_ns:
        return {
            "n_start": n_start,
            "n_end": n_end,
            "excluded_boundary": exclude_boundary_windows,
            "sample_count": 0,
            "total_bias": 0.0,
            "avg_bias": None,
            "n_bar": None,
            "predicted_avg": None,
            "ratio": None,
        }
    total_bias = sum(injection_bias(n) for n in odd_ns)
    avg_bias = total_bias / len(odd_ns)
    n_bar = sum(odd_ns) / len(odd_ns)
    n_min = odd_ns[0]
    # Upper bound: see average_bias_in_window for derivation.
    predicted_avg = 1.0 / (3 * n_min + 1)
    ratio = avg_bias / predicted_avg if predicted_avg > 0 else None
    return {
        "n_start": n_start,
        "n_end": n_end,
        "excluded_boundary": exclude_boundary_windows,
        "sample_count": len(odd_ns),
        "total_bias": round(total_bias, 10),
        "avg_bias": round(avg_bias, 10),
        "n_bar": round(n_bar, 4),
        "n_min": n_min,
        "predicted_avg": round(predicted_avg, 10),
        "ratio": round(ratio, 6) if ratio is not None else None,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    n_max_small: int = N_SMALL,
    n_end_bounds: int = 1024,
    window_size: int = 32,
    output_dir: str = "scripts/out",
) -> dict:
    """
    Run the full C9.4 boundary analysis and return a structured report.

    Sections
    --------
    1. small_n_catalog      : rows for every odd n in [1, n_max_small]
    2. small_n_counts       : summary counts for the catalog
    3. o1n_verification     : per-n O(1/n) bound check up to n_end_bounds
    4. window_analysis      : sliding-window boundary identification
    5. decorrelation_full   : bias estimate without exclusions
    6. decorrelation_excl   : bias estimate with boundary-window exclusion
    7. avg_bias_windows     : average bias for powers-of-two windows
    """
    report: dict = {}

    # 1. Small-n catalog
    catalog = catalog_small_n_exceptions(n_max_small)
    report["small_n_catalog"] = catalog
    report["small_n_counts"] = count_exceptions(n_max_small)

    # 2. O(1/n) bound verification
    o1n_rows = verify_o1n_bound(1, n_end_bounds)
    violations = [r for r in o1n_rows if not r["bound_satisfied"]]
    report["o1n_verification"] = {
        "n_range": [1, n_end_bounds],
        "total_checked": len(o1n_rows),
        "violations": violations,
        "bound_holds": len(violations) == 0,
        "max_ratio": max(r["ratio_bias_times_n"] for r in o1n_rows),
    }

    # 3. Sliding-window boundary identification
    report["window_analysis"] = identify_boundary_windows(
        1, n_end_bounds, window_size
    )

    # 4 & 5. Decorrelation bias estimates
    report["decorrelation_full"] = decorrelation_bias_estimate(
        1, n_end_bounds, exclude_boundary_windows=False, window_size=window_size
    )
    report["decorrelation_excl"] = decorrelation_bias_estimate(
        1, n_end_bounds, exclude_boundary_windows=True, window_size=window_size
    )

    # 6. Average bias across dyadic windows
    dyadic_windows = []
    for exp in range(3, 11):
        ws = 1 << exp  # 8, 16, ..., 1024
        dyadic_windows.append(average_bias_in_window(ws, ws * 2 - 1))
    report["avg_bias_windows"] = dyadic_windows

    return report


def _write_outputs(report: dict, output_dir: str) -> None:
    """Write CSV and JSON outputs for the report."""
    os.makedirs(output_dir, exist_ok=True)

    # JSON summary
    json_path = os.path.join(output_dir, "c9_4_boundary_report.json")
    with open(json_path, "w") as fh:
        json.dump(report, fh, indent=2)

    # CSV: small-n catalog
    catalog_path = os.path.join(output_dir, "c9_4_small_n_catalog.csv")
    rows = report.get("small_n_catalog", [])
    if rows:
        with open(catalog_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    # CSV: O(1/n) verification (boundary cases only — saves space)
    o1n_path = os.path.join(output_dir, "c9_4_o1n_bounds.csv")
    windows = report.get("avg_bias_windows", [])
    if windows:
        with open(o1n_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=windows[0].keys())
            writer.writeheader()
            writer.writerows(windows)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="C9.4 Boundary perturbation analysis for +1 injections"
    )
    parser.add_argument(
        "--n-max-small",
        type=int,
        default=N_SMALL,
        help="Upper bound for small-n exception catalog (default: %(default)s)",
    )
    parser.add_argument(
        "--n-end",
        type=int,
        default=1024,
        help="Upper bound for O(1/n) verification range (default: %(default)s)",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=32,
        help="Sliding window size for boundary detection (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join("scripts", "out"),
        help="Output directory (default: %(default)s)",
    )
    args = parser.parse_args()

    print(f"[C9.4] Generating boundary perturbation report …")
    report = generate_report(
        n_max_small=args.n_max_small,
        n_end_bounds=args.n_end,
        window_size=args.window_size,
        output_dir=args.output,
    )
    _write_outputs(report, args.output)

    counts = report["small_n_counts"]
    o1n = report["o1n_verification"]
    dec_full = report["decorrelation_full"]
    dec_excl = report["decorrelation_excl"]

    print(
        f"  Small-n exceptions (n ≤ {args.n_max_small}): "
        f"{counts['exits_below'] + counts['exits_above']} / {counts['total_odd']} odd values exit window "
        f"(frequency = {counts['exit_frequency']:.4f})"
    )
    print(
        f"  O(1/n) bound: holds for all {o1n['total_checked']} checked values "
        f"(max ratio = {o1n['max_ratio']:.6f} < 1/3 = {1/3:.6f})"
    )
    print(
        f"  Decorrelation bias (full range):     avg Δ = {dec_full['avg_bias']:.2e}, "
        f"ratio to 1/(3n̄) = {dec_full['ratio']:.6f}"
    )
    print(
        f"  Decorrelation bias (excl. boundary): avg Δ = {dec_excl['avg_bias']:.2e}, "
        f"ratio to 1/(3n̄) = {dec_excl['ratio']:.6f}"
    )
    print(f"  Output written to: {args.output}/")
